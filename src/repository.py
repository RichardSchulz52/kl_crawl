import sqlite3

class Repository:
    def __init__(self, db_file: str = "kl_cars.db") -> None:
        self.db_file = db_file
        self.con = None
        self.cur = None

    # (id, title, price, date, place, brand, model, details_text, cb_details)
    def open(self):
        self.con = sqlite3.connect(self.db_file)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS car (
                id int PRIMARY KEY, 
                title varchar(500),
                price varchar(20),
                date varchar(50),
                place varchar(50),
                brand varchar(50), 
                model varchar(100), 
                details varchar(2000), 
                cb_details varchar(2000),
                image blob
        )""")


    def safe(self, data, img_bytes):
        self.cur.execute("""
                    INSERT INTO car (id, title, price, date, place, brand, model, details, cb_details, image)
                    values (?,?,?,?,?,?,?,?,?,?)    
                """, (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], sqlite3.Binary(img_bytes)))
        self.con.commit()

    
    def id_exists(self, id):
        return self.cur.execute(f"""SELECT * from car WHERE id = {id}""").fetchone() is not None

    
    def close(self):
        self.con.close()
