import scrapy, re, json
from datetime import datetime as dt




class MunichStartupSpider(scrapy.Spider):
    name = 'munich_startup'
    allowed_domains = ['munich-startup.de']
    start_urls = ['https://www.munich-startup.de/startups/?paging=1']
    def __init__(self, *args, **kwargs):
        super(MunichStartupSpider, self).__init__(*args, **kwargs)
        timestamp = dt.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.custom_settings = {
            'FEED_FORMAT': 'json',
            'FEED_URI': f'output-{timestamp}.json'
        }
    def parse(self, response):
        # Replace 'your_xpath_to_items' with the actual XPath to match items
        for startup in response.xpath("//*[contains(@class, 'w-full') and contains(@class, 'md:w-1/2') and contains(@class, 'lg:w-1/3') and contains(@class, 'mt-8')]"):

            item = {
                'title': startup.xpath(".//a[1]//h2/text()").get(),
                'link': startup.xpath(".//a[1]/@href").get(),
                # Use .getall() to get all matching tags and then join them into a string
                'tags': startup.xpath(".//li[contains(@class, 'startup-term')]/text()").getall(),
            }

            # If title is unavailable, log it
            if item['title'] is None:
                self.logger.error(f"Title is missing for {response.url}")
            else:
                page_url = response.urljoin(item['link'])
                request = scrapy.Request(page_url, callback=self.parse_startup_page)
                request.meta['item'] = item
                yield request


        ####TEST SCRAPE
        # Retrieve the current page number from the meta, if it doesn't exist it's the first page
        current_page = response.meta.get('current_page', 1)

        # Logic for next page URL
        next_page_url = response.xpath("//a[contains(@class, 'wp-block-button__link') and contains(text(), 'Mehr Startups laden')]/@href").get()

        # If there is a next page and we're not already on the second page
        if next_page_url and current_page < 2:
            # Increment the page number
            next_page_number = current_page + 1
            # Follow the next page link and pass the updated page number in the meta
            yield scrapy.Request(
                response.urljoin(next_page_url),
                callback=self.parse,
                meta={'current_page': next_page_number}
            )
        ####FULL SCRAPE
        # # # After you have scraped the startups on the current page, look for the next page link
        # next_page_url = response.xpath("//a[contains(@class, 'wp-block-button__link') and contains(text(), 'Mehr Startups laden')]/@href").get()

        # # # If there is a next page, schedule a new request
        # if next_page_url:
        #     yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)
    
    def parse_startup_page(self, response):
        item = response.meta['item']

        # Extract details using their respective XPaths
        # Use .getall() to get all matching <p> elements and join them with a space
        item['description'] = ' '.join(response.xpath('//*[@class="container map-single-content"]//*[@class="entry-content"]//p/text()').getall())

        ##########TEAM SIZE
        team_size_text = ' '.join(response.xpath("*//h2[contains(., 'Team')]/following-sibling::p[1]/text()").getall()).strip()
        
        founders = None
        staff = None
        total = None

        # Use regular expressions to find numbers next to specific words
        founders_match = re.search(r'(\d+)\s*GründerInnen', team_size_text)
        staff_match = re.search(r'(\d+)\s*MitarbeiterInnen', team_size_text)

        # Check if founders information exists
        if founders_match:
            founders = int(founders_match.group(1))
        else:
            founders = None

        # Check if staff information exists
        if staff_match:
            staff = int(staff_match.group(1))
        elif founders is not None:
            staff = 0
        else:
            staff = None

        # Calculate total only if either founders or staff is not None
        if founders is not None or staff is not None:
            total = (founders if founders is not None else 0) + (staff if staff is not None else 0)

        # Assign the values to a dictionary
        item['team_size'] = {
            'founders': founders,
            'staff': staff,
            'total': total
        }

        ########ADDRESS
        # Extract the address text, split by any whitespace (including newlines)
        address_parts = response.xpath("*//h2[contains(., 'Firmensitz')]//following-sibling::address/p/text()").getall()

        # Clean each part and filter out empty strings
        cleaned_address_parts = [part.strip() for part in address_parts if part.strip()]
        # Join the cleaned parts with a comma and a space
        address_text = ', '.join(cleaned_address_parts)

        # Add the cleaned address with commas to item
        item['address'] = address_text

        ########FOUNDATION YEAR
        foundation_year_str = response.xpath("*//h2[contains(., 'Gründungsjahr')]/following-sibling::p[1]/text()").get()

        # Check if the string is not None and if it contains digits
        if foundation_year_str and foundation_year_str.strip().isdigit():
            # Convert the string to an integer
            item['foundation_year'] = int(foundation_year_str.strip())
        else:
            # Log an error or set to None if it's not a valid number
            self.logger.error(f"Invalid foundation year: {foundation_year_str}")
            item['foundation_year'] = None
        
        item['business_model'] = response.xpath("*//h2[contains(., 'Geschäftsmodel')]/following-sibling::p[1]/text()").get()
        item['growth_stage'] = response.xpath("*//h2[contains(., 'Stage')]/following-sibling::p[1]/text()").get()
        item['telephone'] = response.xpath("*//div[h2[contains(., 'Kontakt')]]//a[starts-with(@href, 'tel:')]/text()").get()
        item['email'] = response.xpath("*//div[h2[contains(., 'Kontakt')]]//a[starts-with(@href, 'mailto')]/text()").get()
        company_website = response.xpath("*//div[h2[contains(., 'Kontakt')]]//a[starts-with(@href, 'http')]/text()").get()
        #in case I want to check the functionality of company websites later. this will however significantly increase the number of http requests and will slow the spider down. maybe not what I need.

        item['website'] = company_website
        # XPath to match the div containing the update date text
        update_date_xpath = "//*[contains(@class, 'w-1/2') and contains(@class, 'text-left') and contains(@class, 'pl-3') and contains(@class, 'italic')]/text()"

        # Extract the text, strip whitespace and split by 'am' to get the date part
        update_date_text = response.xpath(update_date_xpath).get().strip()
        update_date = update_date_text.split('am')[-1].strip()

        # Add the date to your item
        item['last_updated'] = update_date



        ####active
        # This will return the first matching element for the given xpath or None if there is no match
        inactive_text = response.xpath("//span[@class='text-pink' and contains(text(), '(inaktiv)')]").get()

        # Check if the element was found
        if inactive_text:
            # The text '(inaktiv)' is present, handle the inactive company case
            # For example, set a flag or store the company's data differently
            is_active = False
        else:
            # The text '(inaktiv)' is not present, handle the active company case
            is_active = True

        item['is_active'] = is_active

        # Check for missing fields and set them to None if they are missing
        for field in ['description', 'team_size', 'address', 'foundation_year',
                      'business_model', 'growth_stage', 'telephone', 'email', 'website', 'last_updated']:
            if field not in item or not item[field]:
                item[field] = None

        yield item

# The command to run the spider remains the same:
# scrapy runspider munich_startup_spider.py -o startups.json
