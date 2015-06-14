"""
This script bids a keyword to a specific margin 
"""

import sys
import string
import json
from io import StringIO
import urllib.request

def main(args):
    try: 
        # Call the web service with our keyword, date range, and target margin
        response = urllib.request.urlopen("http://127.0.0.1:5555/keyword-performance/" + args[2].strip().replace(' ', '%20') + 
                               "?start_date=" + str.strip(args[0], "'").strip() + "&end_date=" + str.strip(args[1], "'").strip())
        # Decode the response
        data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
        # Work out the bid needed to reach the margin
        bid = data['rpc'] * (1-float(args[3]))
        print(round(bid, 2))
    except IndexError:
        print("""Invalid number of arguments, try:
./automated_bidder.py <start_date> <end_date> <keyword> <margin>""")

if __name__ == "__main__":
    main(sys.argv[1:])