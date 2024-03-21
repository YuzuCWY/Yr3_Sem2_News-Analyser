import sqlite3

# Connect to the database (create a new one if it doesn't exist)
conn = sqlite3.connect('news_database.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the browse_history table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS browse_history (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        browse_keyword TEXT,
        browse_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        article_id INTEGER
    )
''')

# Create the news_article table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_article (
        article_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        article_media_name TEXT,
        article_title TEXT,
        article_date TEXT,
        article_keywords TEXT
    )
''')

# Create the sentiment table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sentiment (
        article_id INTEGER PRIMARY KEY,
        article_sentiment TEXT
    )
''')

# Create the article_media table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS article_media (
        article_media_name TEXT PRIMARY KEY,
        article_title TEXT,
        article_date TEXT,
        article_id INTEGER
    )
''')

# Create the user table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY,
        browse_keyword TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
