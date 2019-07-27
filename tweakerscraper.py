import time
import sys

from bs4 import BeautifulSoup
import requests


def main(arg):
    start_time = time.time()

    cookie = "__Secure-TnetID=0S9lFR1e0AMIUz9mUvsx9Hk0LHM53yVW; lastConsentChange=1564229933834; " \
             "wt3_eid=%3B318816705845986%7C2154996479730406671%232156422993166350719; " \
             "_vwo_uuid_v2=DF22274025AB9148EC8EE889EE068AAEC|37c2b53e0f8cfd361aca8a66ffd96702; " \
             "_ga=GA1.2.2096494696.1549964798; wt_rla=318816705845986%2C1%2C1564229931177; uid=1117597; " \
             "_vis_opt_s=2%7C; _vis_opt_exp_114_exclude=1; LastVisit=1562253620; SessionTime=1560068907; " \
             "tc=1564229927%2C1563136343; " \
             "__gads=ID=e198f3129a5c2ac3:T=1562253622:S=ALNI_MZmcw3qWXWggzyBkrdYE9wodlUP1w; pl=3090%3A0; " \
             "_sotmpid=0:jy2vxfw3:1x8ZAc_Osx18n9ie0nYB6T8maQwYxfzr; _vis_opt_exp_130_exclude=1; wt_cdbeid=1; " \
             "wt3_sid=%3B318816705845986; _gid=GA1.2.80576767.1564229933 "

    count = 0
    duration = time.time() - start_time
    print(f"Scraped {count} in {duration} seconds")


if __name__ == "__main__":
    main(sys.argv[1])
