from db import Databse
from datetime import datetime

test_db = Databse()

now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

test_db.insert(now_date,'ON')

