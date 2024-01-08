from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import InvalidSessionIdException
from urllib3.exceptions import ReadTimeoutError

import urllib.request
import remote_gateway

class Driver:

    def __init__(self, remote_web_driver_url: str = 'http://localhost:4444/wd/hub') -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')

        self.remote_web_driver_url = remote_web_driver_url
        self.driver = None
        self.next_sleep_time = 0

        self.gateway = remote_gateway.RemoteGateway(retryable_errors=[ReadTimeoutError], 
                                                    accepted_errors=[NoSuchElementException, StaleElementReferenceException],
                                                    error_handlers=[(InvalidSessionIdException, self.restart)])
        
     
    def restart(self):
        self.close()
        self.start()


    def start(self):
        self.driver = webdriver.Remote(
            command_executor=self.remote_web_driver_url,
            options=self.options
        )
        self.driver.maximize_window()


    def close(self):
        self.driver.close()
        self.driver.quit()

    
    def fetch_from_page(self, page):
        self.gateway.crawl_call(lambda: self.driver.get(f"https://www.kleinanzeigen.de/s-autos/seite:{page}/c216"))
        items = self.gateway.call(lambda: self.driver.find_elements(By.CLASS_NAME, 'ad-listitem    '))
        infos = []
        for item in items:
            rel_url = self.gateway.call(lambda: self.fetch_rel_url(item))
            if rel_url is None:
                continue
            url = "https://www.kleinanzeigen.de" + rel_url
            img_url = self.gateway.call(lambda: self.fetch_img_url(item))
            if img_url is not None:
                infos.append((url, img_url))
        return infos
    
    def fetch_rel_url(self, item):
        article = item.find_element(By.TAG_NAME, "article")
        return article.get_attribute("data-href")


    def fetch_img_url(self, item):
        img_element = item.find_element(By.TAG_NAME, "img")
        return img_element.get_attribute("src")


    def fetch_data(self, url):
        print(f"fetch details from {url}")
        self.gateway.crawl_call(lambda: self.driver.get(url))
        details_element = self.gateway.call(lambda: self.driver.find_element(By.ID, "viewad-details"))
        if details_element is None:
            return
        details = details_element.text.split("\n")
        brand = details[1]
        model = details[3]
        details_text = ",".join(details[4:])
        cb_details_element = self.gateway.call(lambda: self.driver.find_element(By.ID, "viewad-configuration"))
        id_element = self.gateway.call(lambda: self.driver.find_element(By.ID, "viewad-ad-id-box"))
        if cb_details_element is None or id_element is None:
            return
        cb_details = cb_details_element.text.replace("\n", ",")
        id = id_element.text.split("\n")[1]

        return (id, brand, model, details_text, cb_details)
    

    def img_bytes(self, img_url):
        print(f"fetch img bytes from {img_url}")
        message = self.gateway.crawl_call(lambda: urllib.request.urlopen(img_url))
        img_bytes = message.read()
        return img_bytes


    