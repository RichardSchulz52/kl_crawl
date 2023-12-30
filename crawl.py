from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import urllib.request
import sqlite3
import time

options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')

print("Starting")
dbfile = 'file.db'
con = sqlite3.connect(dbfile)

cur = con.cursor()
print("create table")
cur.execute("""CREATE TABLE IF NOT EXISTS raw (
                url varchar(2000) PRIMARY KEY,
                text varchar(2000),
                image blob
)""")

print("open driver")
driver = webdriver.Remote(
command_executor='http://localhost:4444/wd/hub',
options=options
)

driver.maximize_window()

print("fetch site")
driver.get("https://www.kleinanzeigen.de/s-autos/c216")

url_exists_in_db = False
while not url_exists_in_db:
    print("find elements in page")
    items_in_page = driver.find_elements(By.CLASS_NAME, 'ad-listitem    ')
    for item in items_in_page:
        # get informations
        try:
            img_element = item.find_element(By.TAG_NAME, "img")
            img_url = img_element.get_attribute("src")
        except NoSuchElementException:
            print("no img tag found. Skipping.")
            continue
        print(f"fetching img {img_url}")
        text = item.text
        print(f"loading img {img_url}")
        urllib.request.urlretrieve(img_url, "tmp.png")
        print("check if item is in db")
        if cur.execute(f"""SELECT * from raw WHERE url = '{img_url}'""").fetchone():
            url_exists_in_db = True
            print(f"ending because {img_url} already exists")
        else:
            print("save to db")
            with open("tmp.png", 'rb') as f:
                cur.execute("""
                    INSERT INTO raw (url, text, image)
                    values (?,?,?)    
                """, (img_url, text, sqlite3.Binary(f.read())))
            print("sleep for 30")
            time.sleep(30)
    print("going to next page")
    driver.find_element(By.CLASS_NAME, 'pagination-next').click() #ElementClickInterceptedException "is not clickable at point (966, 861)"
    # auch möglich https://www.kleinanzeigen.de/s-autos/seite:1/c216
driver.close()
driver.quit()
print("Successfully Completed!")