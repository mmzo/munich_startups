# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy, re
from itemloaders.processors import MapCompose, Join, Identity, Compose,TakeFirst

def clean_text(text):
    # Perform any cleaning of the description text here if necessary
    return text.strip()


def check_foundation_year(text):
    if text and text.isdigit():
        # Convert the string to an integer
        return int(text)
    else:
        # Log an error or set to None if it's not a valid number
        scrapy.log.msg(f"Invalid foundation year: {text}", level=scrapy.log.ERROR)
        return None
    
def split_date(text):
    return text.split('am')[-1].strip()

def remove_leading_comma_and_name(value):
    # Strip leading comma and any whitespace
    value = value.lstrip(', ')
    parts = value.split(',', 1)  # Split only once
    if len(parts) > 1:
        return parts[1].strip()  # Return the address part without the name
    else:
        return value  # Return the original address if no comma is found 

class MunichStartupProjectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MunichStartupItem(scrapy.Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.setdefault(field, None)

    title = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    link = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    tags = scrapy.Field()
    # description = scrapy.Field()
    description = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=Join(' '),
        default=None
    )
    # team_size = scrapy.Field()
    total_team_size = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    founders_number = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    staff_size = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    # address = scrapy.Field()
    address = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor= Compose(Join(', '),remove_leading_comma_and_name),
        default=None
    )
    # foundation_year = scrapy.Field()
    foundation_year = scrapy.Field(
        input_processor=MapCompose(clean_text,check_foundation_year),
        output_processor=TakeFirst(),
        default=None
    )
    business_model = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    growth_stage = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    telephone = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    email = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    website = scrapy.Field(
        output_processor=TakeFirst(),
        default=None
    )
    last_updated = scrapy.Field(
        input_processor=MapCompose(clean_text,split_date),
        output_processor=TakeFirst(),
        default=None
    )
    is_active = scrapy.Field(
        # input_processor=MapCompose(is_active),
        output_processor=TakeFirst(),
        default='active'
    )