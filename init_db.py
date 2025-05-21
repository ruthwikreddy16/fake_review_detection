import sqlite3

# Connect to database (creates users.db if not exists)
conn = sqlite3.connect('users.db')

# Create a table for users
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
''')

# Create a table for prediction history
conn.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        review_text TEXT NOT NULL,
        prediction TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
''')

print("Database and tables created successfully.")

conn.commit()
conn.close()
