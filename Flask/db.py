import sqlite3

connection = sqlite3.connect('Flask/students_sqllite.db')

cursor = connection.cursor()

cursor.execute(''' CREATE TABLE IF NOT EXISTS Products 
               (product_id INTEGER PRIMARY KEY AUTOINCREMENT, product TEXT,
               supplier TEXT, price_per_tonne INT)
               ''')

productsToInsert = [
    ('Bannans', 'United Bannans', 7000),
    ('Avocados', 'United Avocados', 12000),
    ('Tometos', 'United Tomatos', 3100)
]

# cursor.executemany('''
#                     INSERT INTO Products(product, supplier, price_per_tonne)
#                    VALUES (?,?,?)
#                    ''', productsToInsert)

cursor.execute("SELECT * FROM Products")
print(cursor.fetchall())

connection.commit()
connection.close()