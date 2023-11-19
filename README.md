# A simple scraper of the Munich startups portal

## Description
For this project I built a webscraper for the website en.munich-startup.de. 

I wanted to know what kind of startups were operating in Munich according to the official Munich portal.

The website used dynamic loading to generate the lists of startups, however the weblink was essentially the same, but with a new page number. 

This meant that I could iterate through web pages without resorting to something like Selenium to press a reload button.

I ended up having to do a lot of data cleaning after using the scraper and for the future would attempt to include as much of this process in the scraper pipeline as possible.


## Dataset

The data I recovered was unfortunately filled with blanks as all startups on the site that were updated before 2020 were lacking extra data apart from the name and location of the business. Also some of the startups were no longer active, but were still listed. 

I used the data to create a tableau dashboard (located [here](https://public.tableau.com/views/MunichStartupsinprogress/Dashboard1?:language=en-GB&publish=yes&:display_count=n&:origin=viz_share_link)) which highlights an interesting aspect of the data. 

# Conclusions
Overall I am happy with the results of this scraper; however, it is clear that there are many improvements to make, namely in the spider pipeline, and in the data wrangling/cleaning process.
