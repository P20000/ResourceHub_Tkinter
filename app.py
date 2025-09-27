import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
# Ensure you have scraper.py with the scrape_url function defined
from scraper import scrape_url 

DATABASE_NAME = 'resource_hub.db'

class DBManager:
    """Handles all database connections and operations."""
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        # Use row_factory to get results as dictionaries for easier access by column name
        self.conn.row_factory = sqlite3.Row
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

    def fetch_summary_resources(self):
        """Retrieves ID, Title, URL, Tags, and Date for display in the Treeview (summary)."""
        self.cursor.execute("""
            SELECT id, title, url, tags, date_added 
            FROM resources 
            ORDER BY date_added DESC
        """)
        return [tuple(row) for row in self.cursor.fetchall()]

    def fetch_resource_details(self, resource_id):
        """Retrieves ALL details for a single resource by ID (including full_content)."""
        self.cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        return self.cursor.fetchone() 

    def search_resources(self, search_term):
        """
        Searches resources based on title, tags, or full content.
        Uses the LIKE operator for fuzzy matching.
        """
        term = f'%{search_term.lower()}%'
        
        self.cursor.execute("""
            SELECT id, title, url, tags, date_added 
            FROM resources 
            WHERE 
                LOWER(title) LIKE ? OR 
                LOWER(tags) LIKE ? OR 
                LOWER(full_content) LIKE ? 
            ORDER BY date_added DESC
        """, (term, term, term))
        
        return [tuple(row) for row in self.cursor.fetchall()]
    
    def close(self):
        """Properly closes the database connection."""
        self.conn.close()

# ResourceHubApp Class (Main Tkinter Application)

class ResourceHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ResourceHub - Knowledge Manager")
        self.db = DBManager()
        
        self.create_main_widgets()
        self.load_resources() # Load initial data into the Treeview

    # --- Phase 3, Part 1: GUI Structure and Detail Pane (Based on last step) ---

    def create_main_widgets(self):
        """Sets up the main application layout: Search, Input Form, List, and Detail Pane."""
        # 1. Configure the main grid layout
        self.root.grid_columnconfigure(0, weight=1) # Treeview column
        self.root.grid_columnconfigure(1, weight=3) # Detail Pane column (wider)
        self.root.grid_rowconfigure(3, weight=1)    # Main content row (Row 3 gets all extra vertical space)
        
        # --- ROW 0: Top Search/Action Frame ---
        self.top_frame = ttk.Frame(self.root, padding="10")
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # 1. Search Label
        ttk.Label(self.top_frame, text="Search Resources:").pack(side=tk.LEFT, padx=(0, 5))
        
        # 2. Search Entry Widget
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.top_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda event: self.search_handler())

        # 3. Search Button
        self.search_button = ttk.Button(self.top_frame, text="Search", command=self.search_handler)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 4. Clear Button
        self.clear_button = ttk.Button(self.top_frame, text="Clear Search", command=self.clear_search)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5)) 


        # --- ROW 2: Input Form Frame ---
        self.input_frame = ttk.Frame(self.root, padding="10")
        self.input_frame.grid(row=2, column=0, columnspan=2, sticky="ew") 
        self.input_frame.grid_columnconfigure(1, weight=1)

        # 1. Title Input
        ttk.Label(self.input_frame, text="Title:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(self.input_frame, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # 2. URL Input
        ttk.Label(self.input_frame, text="URL:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.input_frame, textvariable=self.url_var)
        self.url_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # 3. Tags Input
        ttk.Label(self.input_frame, text="Tags (comma-separated):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.tags_var = tk.StringVar()
        self.tags_entry = ttk.Entry(self.input_frame, textvariable=self.tags_var)
        self.tags_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # 4. Save Button
        self.save_button = ttk.Button(self.input_frame, text="SAVE RESOURCE & SCRAPE", 
                                      command=self.add_resource_handler)
        self.save_button.grid(row=0, column=2, rowspan=3, sticky="ns", padx=(10, 0))


        # --- ROW 3: Main Content (List and Detail Panes) ---

        # List Frame (Treeview)
        list_frame = ttk.Frame(self.root, padding="10 0 5 10")
        list_frame.grid(row=3, column=0, sticky="nsew") # PLACED at ROW 3
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        columns = ('ID', 'Title', 'URL', 'Tags', 'Date Added')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.tree.heading('ID', text='ID', anchor='center'); self.tree.column('ID', width=40, anchor='center', stretch=tk.NO)
        self.tree.heading('Title', text='Title')
        self.tree.heading('URL', text='URL')
        self.tree.heading('Tags', text='Tags')
        self.tree.heading('Date Added', text='Date Added')
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        # Treeview Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')


        # Detail Pane (Scraped Content Viewer)
        detail_frame = ttk.Frame(self.root, padding="10 0 10 10")
        detail_frame.grid(row=3, column=1, sticky="nsew") # PLACED at ROW 3
        detail_frame.grid_rowconfigure(0, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)

        # Label for context
        self.detail_label = ttk.Label(detail_frame, text="Resource Details (Full Content):")
        self.detail_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Text widget for content display
        self.content_text = tk.Text(detail_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                    font=('Arial', 10), bd=2, relief=tk.SUNKEN)
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Text widget Scrollbar
        text_scrollbar = ttk.Scrollbar(self.content_text, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_text.config(yscrollcommand=text_scrollbar.set)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind the selection event 
        self.tree.bind('<<TreeviewSelect>>', self.show_resource_details)

    # --- Support Methods ---

    def load_resources(self, data=None):
        """Clears the Treeview and loads resources from the database."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get data from DB (or use provided search results)
        if data is None:
            data = self.db.fetch_summary_resources()
            
        # Insert new data
        for row in data:
            self.tree.insert('', tk.END, values=row)


    def show_resource_details(self, event):
        """
        Event handler for Treeview selection. 
        Fetches the full content and displays it in the detail pane.
        """
        selected_item = self.tree.focus()
        if not selected_item:
            return

        # Get the values of the selected row
        item_values = self.tree.item(selected_item, 'values')
        
        # The first value (index 0) is the ID
        resource_id = item_values[0]

        # Fetch all resource details (including full_content)
        resource = self.db.fetch_resource_details(resource_id)
        
        if resource:
            # Prepare content string
            content_to_display = (
                f"Title: {resource['title']}\n"
                f"URL: {resource['url']}\n"
                f"Tags: {resource['tags']}\n"
                f"Date Added: {resource['date_added']}\n"
                f"----------------------------------------\n\n"
                f"{resource['full_content']}"
            )
            
            # Enable, Clear, Insert, and Disable the Text widget
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete('1.0', tk.END)
            self.content_text.insert(tk.END, content_to_display)
            self.content_text.config(state=tk.DISABLED)
            
            self.detail_label.config(text=f"Resource Details: {resource['title']}")
    def search_handler(self):
        """
        Retrieves the search term, queries the database, and updates the Treeview.
        """
        search_term = self.search_var.get().strip()
        
        if not search_term:
            # If the search box is empty, load all resources
            self.load_resources()
            return

        # Call the powerful search method from DBManager
        results = self.db.search_resources(search_term)
        
        if results:
            self.load_resources(data=results)
            self.detail_label.config(text=f"Search Results: {len(results)} items found for '{search_term}'")
        else:
            # If no results, clear the Treeview and show a message
            self.load_resources(data=[])
            messagebox.showinfo("Search Result", f"No resources found matching '{search_term}'.")


    def clear_search(self):
        """
        Clears the search bar and reloads all resources into the Treeview.
        """
        self.search_var.set("") # Clear the Entry widget
        self.load_resources()   # Reload all resources
        self.detail_label.config(text="Resource Details (Full Content):")    
        # Add a handler for saving resources (from Phase 2 logic)
        # Placeholder for a method to handle inputs and call self.db.add_resource()
        # def add_resource_handler(self, ...):
        #     ... your scraping and saving logic goes here ...
        #     self.db.add_resource(final_title, url, tags, full_content)
        #     self.load_resources()
    def add_resource_handler(self):
        """
        Handles form submission, calls scraper if URL is provided, and saves to DB.
        """
        title = self.title_var.get().strip()
        url = self.url_var.get().strip()
        tags = self.tags_var.get().strip()
        
        # 1. Basic Validation
        if not title:
            messagebox.showerror("Input Error", "Title is required for every resource.")
            return

        # 2. Scrape or Use Placeholder Content
        if url.startswith('http'):
            # Attempt to scrape the URL
            try:
                self.save_button.config(text="SCRAPING...", state=tk.DISABLED)
                
                # Using the scraped title if the user didn't provide a good one
                scraped_title, full_content = scrape_url(url)
                final_title = title if len(title) > 5 else scraped_title
                
            except Exception as e:
                messagebox.showwarning("Scraping Failed", f"Could not scrape URL. Saving only URL and title. Error: {e}")
                final_title = title
                full_content = f"[SCRAPING FAILED] Could not retrieve content from {url}"
        else:
            # Handle notes, snippets, or resources without a URL
            final_title = title
            full_content = f"User Note/Snippet: {title} (No URL provided)"


        # 3. Save to Database
        self.db.add_resource(final_title, url, tags, full_content)
        
        # 4. Cleanup and Refresh
        self.title_var.set("")
        self.url_var.set("")
        self.tags_var.set("")
        self.load_resources() # Refresh the Treeview list
        self.save_button.config(text="SAVE RESOURCE & SCRAPE", state=tk.NORMAL)
        messagebox.showinfo("Success", f"Resource '{final_title}' saved successfully!")


# Main Execution Block


if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = ResourceHubApp(root)
        root.mainloop()
    except Exception as e:
        # Handle exceptions gracefully, but ensure the DB connection is closed
        print(f"An error occurred: {e}")
    finally:
        # It's good practice to close the DB connection when the app closes
        if 'app' in locals() and hasattr(app, 'db'):
            app.db.close()
            print("Database connection closed.")