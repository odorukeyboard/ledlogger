import pymysql

class Databse():
    def __init__(self):
        self.db = pymysql.connect(host='localhost', port=3306, user='test', passwd='1234', db='test', charset='utf8')
        self.cursor = self.db.cursor()

    def show(self):
        sql="""SELECT * from test """

        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        print(result)
        return(result)

    def query_search(self,st,ed):
        print(st)
        print(ed)
        sql="""SELECT * FROM test where DATE(date) BETWEEN (%s) AND (%s) ORDER BY date DESC"""
        self.cursor.execute(sql,(st,ed))
        result = self.cursor.fetchall()
        print(result)
        return(result)

    def insert(self, date, data):
        sql="""insert into test (date, data) values (%s, %s)"""
        self.cursor.execute(sql,(date,data))
        self.db.commit()

if __name__ == "__main__":
    db=Databse()
    db.show()