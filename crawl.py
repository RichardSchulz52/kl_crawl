from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import urllib.request
import sqlite3
import time


class KleinanzeigenCrawlerAutos:

    SHORT_SLEEP = 1
    NORMAL_SLEEP = 10

    def __init__(self, db_file: str = "kl_cars.db", remote_web_driver_url: str = 'http://localhost:4444/wd/hub', ) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')

        self.db_file = db_file
        self.remote_web_driver_url = remote_web_driver_url
        self.con = None
        self.cur = None
        self.driver = None
        self.page = 1
        self.next_sleep_time = 10
        
    
    def startup(self):
        self.con = sqlite3.connect(self.db_file)

        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS car (
                id int PRIMARY KEY, 
                brand varchar(50), 
                model varchar(100), 
                details varchar(2000), 
                cb_details varchar(2000),
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
            data = self.fetch_data(item[0])
            if data is None:
                continue
            exists = self.id_already_saved(data[0])
            img_bytes = self.img_bytes(item[1])
            if exists:
                return True
            self.save_data(data, img_bytes)
        return False
                

    def fetch_from_page(self):
        self.driver.get(f"https://www.kleinanzeigen.de/s-autos/seite:{self.page}/c216")
        self.sleep()
        items = self.driver.find_elements(By.CLASS_NAME, 'ad-listitem    ')
        infos = []
        for item in items:
            try:
                article = item.find_element(By.TAG_NAME, "article")
                rel_url = article.get_attribute("data-href")
                url = "https://www.kleinanzeigen.de" + rel_url
                img_url = self.fetch_img_url(item)
            except Exception:
                continue
            if img_url is not None:
                infos.append((url, img_url))
        return infos
            
        

    def fetch_img_url(self, item):
        try:
            img_element = item.find_element(By.TAG_NAME, "img")
            return img_element.get_attribute("src")
        except (NoSuchElementException, StaleElementReferenceException):
            return None
        
    
    def fetch_data(self, url):
        try:
            print(f"fetch details from {url}")
            self.driver.get(url)
            self.sleep()
            self.next_sleep_time = KleinanzeigenCrawlerAutos.NORMAL_SLEEP
            details = self.driver.find_element(By.ID, "viewad-details").text.split("\n")
            brand = details[1]
            model = details[3]
            details_text = ",".join(details[4:])
            cb_details = self.driver.find_element(By.ID, "viewad-configuration").text.replace("\n", ",")
            id = self.driver.find_element(By.ID, "viewad-ad-id-box").text.split("\n")[1]
            return (id, brand, model, details_text, cb_details)
        except Exception as e:
            print(e)

        
        
    def img_bytes(self, img_url):
        print(f"fetch img bytes from {img_url}")
        message = urllib.request.urlopen(img_url)
        self.sleep()
        if message.getheader('X-From-Cache', 'false') == 'true':
            self.next_sleep_time = KleinanzeigenCrawlerAutos.SHORT_SLEEP
        else: 
            self.next_sleep_time = KleinanzeigenCrawlerAutos.NORMAL_SLEEP
        img_bytes = message.read()
        return img_bytes
    
    
    def id_already_saved(self, id):
        return self.cur.execute(f"""SELECT * from car WHERE id = {id}""").fetchone() is not None
    
    def save_data(self, data, img_bytes):
        self.cur.execute("""
                    INSERT INTO car (id, brand, model, details, cb_details, image)
                    values (?,?,?,?,?,?)    
                """, (data[0], data[1], data[2], data[3], data[4], sqlite3.Binary(img_bytes)))
        self.con.commit()

    def sleep(self):
        print(f"Sleep for {self.next_sleep_time}")
        time.sleep(self.next_sleep_time)
        

if __name__ == "__main__":
    c = KleinanzeigenCrawlerAutos(remote_web_driver_url="http://192.168.0.2:4444/wd/hub")
    try:
        c.startup()
        c.fetch_all()
    finally:
        c.close()