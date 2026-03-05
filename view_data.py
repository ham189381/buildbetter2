import sqlite3

conn = sqlite3.connect("drivers.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM drivers")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()