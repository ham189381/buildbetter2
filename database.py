import sqlite3

#create or connect to database
conn = sqlite3.connect("database.db")

#create a cursor (used to run SQL)
cursor = conn.cursor()

#create a drivers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    district TEXT,
    division TEXT,
    town TEXT,
    phone NUMBER,
    truck_name TEXT,
    image1 TEXT,
    image2 TEXT,
    image3 TEXT                                       
)
""")
#save changes 
conn.commit()

#close connection
conn.close()

print("Database.db and drivers table created successfully")