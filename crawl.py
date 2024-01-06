from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from urllib3.exceptions import ReadTimeoutError
import urllib.request
import time
import repository


class KleinanzeigenCrawlerAutos:

    SHORT_SLEEP = 1
    NORMAL_SLEEP = 5
    CONNECTION_TIMEOUT_SLEEP = (5 * 60) + 30

    def __init__(self, db_file: str = "kl_cars.db", remote_web_driver_url: str = 'http://localhost:4444/wd/hub') -> None:
        self.repo = repository.Repository()

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')

        self.remote_web_driver_url = remote_web_driver_url
        self.driver = None
        self.page = 1
        self.next_sleep_time = 0
        
    
    def startup(self):
        self.repo.open()

        self.page = 1

        self.driver = webdriver.Remote(
        command_executor=self.remote_web_driver_url,
        options=self.options
        )
        self.driver.maximize_window()

        
    def close(self):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()
        if self.repo is not None:
            self.repo.close()


    def fetch_all(self):
        self.finished = False
        while not self.finished:
            print("fetch page " + str(self.page))
            items_in_page = self.fetch_from_page()
            self.finished = self.save_items(items_in_page)
            self.page += 1
        print("finished")


    def save_items(self, items_in_page):
        for item in items_in_page:
            data = self.fetch_data(item[0])
            if data is None:  
                continue
            exists = self.repo.id_exists(data[0])
            img_bytes = self.img_bytes(item[1])
            if exists:
                print(f"id {data[0]} already in db")
                return True
            self.repo.safe(data, img_bytes)
        return False
                
    def get_and_retry(self, url):
        retries = 0
        while retries < 5:
            try:
                self.driver.get(url)
                self.sleep()
                return
            except ReadTimeoutError:
                sleep_time = KleinanzeigenCrawlerAutos.CONNECTION_TIMEOUT_SLEEP
                print(f"ReadTimeoutError on driver get. Retrying in {sleep_time} seconds.")
                self.close()
                time.sleep(sleep_time)
                self.startup()
                retries += 1


    def fetch_from_page(self):
        self.get_and_retry(f"https://www.kleinanzeigen.de/s-autos/seite:{self.page}/c216")
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
            self.get_and_retry(url)
            self.next_sleep_time = KleinanzeigenCrawlerAutos.NORMAL_SLEEP
            details = self.driver.find_element(By.ID, "viewad-details").text.split("\n") # FIXME auch hier kann es zu problemen kommen, die zum absturz führen, da auf den remote driver zugegriffen wird 
            brand = details[1]
            model = details[3]
            details_text = ",".join(details[4:])
            cb_details = self.driver.find_element(By.ID, "viewad-configuration").text.replace("\n", ",")
            id = self.driver.find_element(By.ID, "viewad-ad-id-box").text.split("\n")[1]
            return (id, brand, model, details_text, cb_details)
        except NoSuchElementException:
            print("NoSuchElementException")

        
        
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