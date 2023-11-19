import scrapy, re, json
from datetime import datetime as dt
from scrapy.loader import ItemLoader
from munich_startup_project.items import MunichStartupItem 


##function to calculate team sizes
def team_size_calculate(joined_text):
    
    founders = None
    staff = None
    total = None
    # Use regular expressions to find numbers next to specific words
    founders_match = re.search(r'(\d+)\s*GründerInnen', joined_text)
    staff_match = re.search(r'(\d+)\s*MitarbeiterInnen', joined_text)

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
    return founders, staff, total

def check_is_active(inactive_text):
     # Check if the element was found
    return False if inactive_text is not None else True

class MunichStartupSpider(scrapy.Spider):
    name = 'munich_startup2'
    allowed_domains = ['munich-startup.de']
    start_urls = ['https://www.munich-startup.de/startups/?paging=1']

    def parse(self, response):
        # Replace 'your_xpath_to_items' with the actual XPath to match items
        for startup in response.xpath("//*[contains(@class, 'w-full') and contains(@class, 'md:w-1/2') and contains(@class, 'lg:w-1/3') and contains(@class, 'mt-8')]"):
            loader = ItemLoader(item=MunichStartupItem(), selector=startup)
            
            loader.add_xpath('title',".//a[1]//h2/text()"),
            loader.add_xpath('link',".//a[1]/@href"),
                # Use .getall() to get all matching tags and then join them into a string
            loader.add_xpath('tags',".//li[contains(@class, 'startup-term')]/text()"),
            
            item = loader.load_item()

            # If title is unavailable, log it
            if item['title'] is None:
                self.logger.error(f"Title is missing for {response.url}")
            else:
                page_url = response.urljoin(item['link'])
                request = scrapy.Request(page_url, callback=self.parse_startup_page)
                request.meta['item'] = item
                yield request
                


        ####TEST SCRAPE
        ## Retrieve the current page number from the meta, if it doesn't exist it's the first page
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

        ###FULL SCRAPE
        # # # After you have scraped the startups on the current page, look for the next page link
        # next_page_url = response.xpath("//a[contains(@class, 'wp-block-button__link') and contains(text(), 'Mehr Startups laden')]/@href").get()

        # # # If there is a next page, schedule a new request
        # if next_page_url:
        #     yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)
    
    def parse_startup_page(self, response):
        item = response.meta['item']

        # Create a new ItemLoader with the item received
        loader = ItemLoader(item=item, selector=response)

        # Extract details using their respective XPaths
        
        loader.add_xpath('description', '//*[@class="container map-single-content"]//*[@class="entry-content"]//p/text()')
        

        ########ADDRESS
        # Extract the address text, split by any whitespace (including newlines)
        loader.add_xpath('address',"*//h2[contains(., 'Firmensitz')]//following-sibling::address/p/text()")

        ########FOUNDATION YEAR

        loader.add_xpath('foundation_year',"*//h2[contains(., 'Gründungsjahr')]/following-sibling::p[1]/text()")
        
        loader.add_xpath('business_model',"*//h2[contains(., 'Geschäftsmodel')]/following-sibling::p[1]/text()")
        loader.add_xpath('growth_stage',"*//h2[contains(., 'Stage')]/following-sibling::p[1]/text()")
        loader.add_xpath('telephone',"*//div[h2[contains(., 'Kontakt')]]//a[starts-with(@href, 'tel:')]/text()")
        loader.add_xpath('email',"*//div[h2[contains(., 'Kontakt')]]//a[starts-with(@href, 'mailto')]/text()")
        
        loader.add_xpath('website',"*//div[h2[contains(., 'Kontakt')]]//a[starts-with(@href, 'http')]/text()")
        
        # XPath to match the div containing the update date text
        update_date_xpath = "//*[contains(@class, 'w-1/2') and contains(@class, 'text-left') and contains(@class, 'pl-3') and contains(@class, 'italic')]/text()"

        # Extract the text, strip whitespace and split by 'am' to get the date part
        loader.add_xpath('last_updated',update_date_xpath)
       
        ####active
        # This will return the first matching element for the given xpath or None if there is no match
        
        # loader.add_xpath('is_active',"//span[@class='text-pink' and contains(text(), '(inaktiv)')]/text()")

        item = loader.load_item()

        ##########TEAM SIZE
        # loader.add_xpath('team_size',"*//h2[contains(., 'Team')]/following-sibling::p[1]/text()")
        team_size_text = ' '.join(response.xpath("*//h2[contains(., 'Team')]/following-sibling::p[1]/text()").getall()).strip()
        item['founders_number'], item['staff_size'], item['total_team_size'] = team_size_calculate(team_size_text)

        ####active
        # This will return the first matching element for the given xpath or None if there is no match
        inactive_text = response.xpath("//span[@class='text-pink' and contains(text(), '(inaktiv)')]").get()

        item['is_active'] = check_is_active(inactive_text)
        yield item

# The command to run the spider remains the same:
# scrapy runspider munich_startup_spiderv2.py -o startups.json
