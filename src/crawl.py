
import repository, driver


class KleinanzeigenCrawlerAutos:

    def __init__(self, db_file: str = "kl_cars.db", remote_web_driver_url: str = 'http://localhost:4444/wd/hub') -> None:
        self.repo = repository.Repository(db_file)
        self.driver = driver.Driver(remote_web_driver_url)
        self.page = 1
        
    
    def startup(self):
        self.repo.open()
        self.page = 1
        self.driver.start()

        
    def close(self):
        if self.driver is not None:
            self.driver.close()
        if self.repo is not None:
            self.repo.close()


    def fetch_all(self):
        self.finished = False
        while not self.finished:
            print("fetch page " + str(self.page))
            items_in_page = self.driver.fetch_from_page(self.page)
            self.finished = self.save_items(items_in_page)
            self.page += 1
        print("finished")


    def save_items(self, items_in_page):
        for item in items_in_page:
            data = self.driver.fetch_data(item[0])
            if data is None:  
                continue
            if self.repo.id_exists(data[0]):
                print(f"id {data[0]} already in db")
                return True
            img_bytes = self.driver.img_bytes(item[1])
            self.repo.safe(data, img_bytes)
        return False
        


if __name__ == "__main__":
    c = KleinanzeigenCrawlerAutos(remote_web_driver_url="http://192.168.0.2:4444/wd/hub")
    try:
        c.startup()
        c.fetch_all()
    finally:
        c.close()