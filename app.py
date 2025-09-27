import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DATABASE_NAME = 'resource_hub.db'

class DBManager:
    """Handles all database connections and operations."""
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        # The main table structure
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT,
                tags TEXT,
                full_content TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_resource(self, title, url, tags, content):
        """Inserts a new resource into the database."""
        self.cursor.execute(
            "INSERT INTO resources (title, url, tags, full_content) VALUES (?, ?, ?, ?)",
            (title, url, tags, content)
        )
        self.conn.commit()

    def fetch_all_resources(self):
        """Retrieves all resources from the database."""
        self.cursor.execute("SELECT id, title, url, tags, date_added FROM resources ORDER BY date_added DESC")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# For Phase 1 testing only:
if __name__ == '__main__':
    db = DBManager()
    db.add_resource("Test Link", "http://.com", "python, test", "This is the scraped content.")
    print("Database check: ", db.fetch_all_resources())
    db.close()