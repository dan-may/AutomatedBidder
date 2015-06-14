"""
This script creates the keywords and keyword_performance databases.
It also fills the databases with dummy data.
"""

import sqlite3
import datetime
import random
import locale
import math
from dateutil import rrule

if __name__ == '__main__':

    locale.setlocale(locale.LC_ALL, 'US')

    start = datetime.date(2013, 1, 1)
    end = datetime.date(2014, 9, 1)
    
    keyword_performance = []
    days = []
    
    # Populate keywords
    keywords = [
        ("buy vinyl records", None),
        ("music download", None),
        ("flac download", None),
        ("album download", None),
        ("single download", None),
        ("flac music download", None),
        ("24-bit hi-res", None),
        ("24-bit", None),
        ("high definition music", None),
        ("where can I download music", None),
        ("free music download", None),
        ("music", None)
                ]
    
    variance = (0.1, 2, 1.7, 5.7, 3.3, 0.3, 0.4, 1, 7.2, 3, 3.2, 4.5)

    # Iterate over keywords to produce performance data for each keyword each day
    for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
        days.append((day))
        for keyword in keywords:
            id = keywords.index(keyword) + 1
            cpc = random.normalvariate(1, 0.2)
            impressions = random.randint(1000000, 10000000)
            clicks = impressions / 1000
            # Taking absolute values because some negative numbers were creeping in;
            # half normal distribution
            if id in range(1, 5):
                # High conversion (more specific) keywords
                converted_clicks = round(clicks / abs(random.normalvariate((10/3), math.sqrt(variance[id - 1]))))
            elif id in range (6, 9):
                # Medium conversion keywords
                converted_clicks = round(clicks / abs(random.normalvariate((10/2), math.sqrt(variance[id - 1]))))
            elif id in range (10, 12):
                # Low conversion (more general) keywords
                converted_clicks = round(clicks / abs(random.normalvariate((10/1), math.sqrt(variance[id - 1]))))
            cost = cpc * clicks
            revenue = converted_clicks * 10
            leads = converted_clicks
            keyword_performance.append(
                (day, 
                 id, 
                 None, 
                 locale.currency(cpc), 
                 impressions, 
                 clicks, 
                 converted_clicks,
                 locale.currency(cost),
                 locale.currency(revenue),
                 leads))

    con = sqlite3.connect("adwords.db")

    # Enable foreign keys
    con.execute("pragma foreign_keys = on")

    # Drop tables if exist
    con.execute("drop table if exists keywords")
    con.execute("drop table if exists keyword_performance")

    # Create the keywords table
    con.execute("""create table keywords(
    keyword_id integer primary key autoincrement, 
    keyword_text varchar(128),
    bid decimal,
    updated_at timestamp default current_timestamp)""")

    # Create the keyword_performance table
    con.execute("""create table keyword_performance(
    date date,
    keyword_id integer,
    bid decimal,
    cpc decimal,
    impressions integer,
    clicks integer,
    converted_clicks integer,
    cost decimal,
    revenue decimal,
    leads integer,
    updated_at timestamp default current_timestamp,
    primary key(date, keyword_id),
    foreign key(keyword_id) references keywords(keyword_id))""")

    # Create a trigger to auto-update timestamps
    con.execute("""
    create trigger update_timestamp update of bid on keywords
    begin
        update keywords set updated_at=current_timestamp where keyword_id=old.keyword_id;
    end""")

    # Fill the tables
    con.executemany("insert into keywords(keyword_text, bid) values (?, ?)", keywords)
    con.executemany("""insert into keyword_performance(
    date, keyword_id, bid, cpc, impressions, clicks, converted_clicks, cost, revenue, leads) 
    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", keyword_performance)

    con.commit()
    con.close()



