import crawl
import argparse
import time

parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')
parser.add_argument('--wd_url', default='http://192.168.0.2:4444/wd/hub', help="The url pinting to the selenium web driver")
parser.add_argument('--db_path', default='kl_cars.db', help="Path to the sqlite database file")

args = parser.parse_args()
c = crawl.KleinanzeigenCrawlerAutos(remote_web_driver_url=args.wd_url, db_file=args.db_path)
while True:
    try:
        c.startup()
        c.fetch_all()
    except Exception as e:
        print(f"unexpected error {type(e)}")
    finally:
        c.close()
    if c.finished:
        print("crawler got all. Sleeping for an hour.")
        time.sleep(60 * 60)
    else:
        print("Some error interupted. Trying again in 5 mins.")
        time.sleep(5 * 60)