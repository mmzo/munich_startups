# munich_startups
simple scraper of the munich startups website

For this project I built a webscraper for the website en.munich-startup.de. 

I wanted to know what kind of startups were operating in Munich according to the official Munich portal.

The website used dynamic loading to generate the lists of startups, however the weblink was essentially the same, but with a new page number. 

This meant that I could iterate through web pages without resorting to something like Selenium to press a reload button.

I ended up having to do a lot of data cleaning after using the scraper and for the future would attempt to include as much of this process in the scraper pipeline as possible.

# Dataset

The data I recovered was unfortunately filled with blanks as all startups on the site that were updated before 2020 were lacking extra data apart from the name and location of the business. Also some of the startups were no longer active, but were still listed. 
