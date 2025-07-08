
import sqlite3

# Create a connection to a SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Create a simple table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
''')

# Insert some sample data
cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ("John Doe", "john@example.com"))
cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", ("Jane Smith", "jane@example.com"))

# Commit the changes
conn.commit()

# Query the data
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print("Users in database:")
for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")

# Close the connection
conn.close()
