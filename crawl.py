from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import urllib.request
import sqlite3
import time


class kleinanzeigen_crawler_autos:
    def __init__(self, db_file: str = "file.db", remote_web_driver_url: str = 'http://localhost:4444/wd/hub', ) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')

        self.db_file = db_file
        self.remote_web_driver_url = remote_web_driver_url
        self.con = None
        self.cur = None
        self.driver = None
        self.page = 1
        
    
    def startup(self):
        self.con = sqlite3.connect(self.db_file)

        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS raw (
                url varchar(2000) PRIMARY KEY,
                text varchar(2000),
                image blob
        )""")

        self.driver = webdriver.Remote(
        command_executor=self.remote_web_driver_url,
        options=self.options
        )
        self.driver.maximize_window()

        

    def close(self):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()

    def fetch_all(self):
        finished = False
        while not finished:
            print("fetch page " + str(self.page))
            items_in_page = self.fetch_from_page()
            finished = self.save_items(items_in_page)
            self.page += 1
        print("finished")

    def save_items(self, items_in_page):
        for item in items_in_page:
            img_url = self.fetch_img_url(item)
            print("fetch " + img_url)
            data = self.data_as_tuple(item, img_url)
            exists = self.url_already_saved(img_url)
            if exists:
                return True
            self.save_data(data)

            sleep_time = 10
            print("sleep "+str(sleep_time)+" before continue")
            time.sleep(sleep_time)
        finished = False
        
            


    def fetch_from_page(self) -> bool:
        self.driver.get(f"https://www.kleinanzeigen.de/s-autos/seite:{self.page}/c216")
        return self.driver.find_elements(By.CLASS_NAME, 'ad-listitem    ')
        

    def fetch_img_url(self, item):
        try:
            img_element = item.find_element(By.TAG_NAME, "img")
            return img_element.get_attribute("src")
        except NoSuchElementException:
            print("no img tag found. Skipping.")
            return None
        
    def data_as_tuple(self, item, img_url):
        text = item.text
        img_bytes = urllib.request.urlopen(img_url).read()
        return (img_url, text, img_bytes)
    
    def url_already_saved(self, img_url):
        return self.cur.execute(f"""SELECT * from raw WHERE url = '{img_url}'""").fetchone()
    
    def save_data(self, data):
        self.cur.execute("""
                    INSERT INTO raw (url, text, image)
                    values (?,?,?)    
                """, (data[0], data[1], sqlite3.Binary(data[2])))
        self.con.commit()
        

if __name__ == "__main__":
    c = kleinanzeigen_crawler_autos(remote_web_driver_url="http://192.168.0.2:4444/wd/hub")
    try:
        c.startup()
        c.fetch_all()
    finally:
        c.close()