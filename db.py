"""
This script creates the keywords and keyword_performance databases.
It also fills the databases with dummy data.
"""

import sqlite3
import datetime
import random
import locale
from dateutil import rrule

if __name__ == '__main__':

    locale.setlocale(locale.LC_ALL, 'US')

    start = datetime.date(2013, 1, 1)
    end = datetime.date(2014, 9, 1)
    
    keyword_performance = []
    days = []
    
    # Populate keywords
    keywords = [
        ("vinyl records", None),
        ("music download", None),
        ("music", None),
        ("24-bit hi-res", None),
        ("flac download", None),
        ("flac music download", None),
        ("24-bit", None),
        ("high definition music", None),
        ("album download", None),
        ("single download", None),
        ("where can I download music", None),
        ("free music download", None)
               ]

    # Iterate over keywords to produce performance data for each keyword each day
    # TODO: Change randomint to normal distribution
    for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
        days.append((day))
        for keyword in keywords:
            id = keywords.index(keyword) + 1
            cpc = random.normalvariate(1, 0.4)
            impressions = random.randint(1000000, 10000000)
            clicks = random.randint(1000, 1000000)
            converted_clicks = random.randint(200, 200000)
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



