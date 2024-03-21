import sqlite3

class DbOperations:

    def connect_to_db(self):
        conn = sqlite3.connect("search_records.db")
        return conn

    def create_table(self, table_name="record"):
        conn = self.connect_to_db()
        query = f'''
                CREATE TABLE IF NOT EXISTS {table_name}(
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                search_key TEXT NOT NULL,
                article TEXT NOT NULL,
                media TEXT NOT NULL,
                link TEXT NOT NULL,
                sentiment TEXT NOT NULL
        );
        '''
        with conn:
            cursor = conn.cursor()
            cursor.execute(query)
            
    def create_record(self, data, table_name="record"):
        search_key = data['search_key']
        article = data['article']
        media = data['media']
        link = data['link']
        sentiment = data['sentiment']

        conn = self.connect_to_db()
        query = f'''
        INSERT INTO {table_name} ('search_key', 'article', 'media', 'link',
                                    'sentiment') VALUES (?, ?, ?, ?, ?);
        '''
        
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, (search_key, article, media, link, sentiment))
            ##print("Saved", (search_key, article, media, link, sentiment))

    def show_records(self, table_name="record"):
        conn = self.connect_to_db()
        query = f'''
        SELECT * FROM {table_name};
        '''
        with conn:
            cursor = conn.cursor()
            cursor.execute(query)
            list_records = cursor.fetchall()
            return list_records
                             
    def delete_record(self, ID, table_name="record"):
        conn = self.connect_to_db()
        query = f'''
        DELETE FROM {table_name} WHERE ID = ?;
        '''
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, (ID,))

    def delete_allrecord(self, table_name="record"):
        conn = self.connect_to_db()
        cursor = conn.cursor()

        # Delete all records from the table
        cursor.execute(f'''DELETE FROM {table_name};''')

        # Reset the auto-increment value to 1
        cursor.execute(f'''UPDATE sqlite_sequence SET seq=0 WHERE name='{table_name}';''')

        # Commit the changes and close the cursor and connection
        conn.commit()
        cursor.close()
        conn.close()
