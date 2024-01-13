import crawl
import argparse
import time
import os

parser = argparse.ArgumentParser(
                    prog='Kl Crawler',
                    description='Crawls data from Kl',
                    epilog='Use cautiosly')
parser.add_argument('--wd_url', default='http://localhost:4444/wd/hub', help="The url pointing to the selenium web driver")
parser.add_argument('--db_path', default='kl_cars.db', help="Path to the sqlite database file")

args = parser.parse_args()
print("wd_url: " + os.environ['wd_url'])
wd_url = os.environ.get('wd_url', args.wd_url)
c = crawl.KleinanzeigenCrawlerAutos(remote_web_driver_url=wd_url, db_file=args.db_path)
while True:
    try:
        c.startup()
        c.fetch_all()
    except Exception as e:
        print(f"unexpected error\n{e}")
    finally:
        c.close()
    if c.finished:
        print("crawler got all. Sleeping for 30 seconds.")
        time.sleep(30)
    else:
        print("Some error interupted. Trying again in 5 mins.")
        time.sleep(5 * 60)