import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk # Custom Tkinter for modern UI
# Ensure summarize_content is correctly imported from scraper.py
from scraper import scrape_url, summarize_content 

# --- CONFIGURATION ---
DATABASE_NAME = 'resource_hub.db'

# --- DB MANAGER CLASS (Modified to include 'summary_content' in all relevant methods) ---

class DBManager:
    """Handles all database connections and operations."""
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        # NOTE: If you run this after already creating the DB, you will need to
        # manually delete resource_hub.db or run an ALTER TABLE command once.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT,
                tags TEXT,
                full_content TEXT,
                summary_content TEXT,  -- <-- NEW FIELD
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_resource(self, title, url, tags, content, summary): # <-- CORRECTED SIGNATURE
        """Inserts a new resource into the database."""
        self.cursor.execute(
            "INSERT INTO resources (title, url, tags, full_content, summary_content) VALUES (?, ?, ?, ?, ?)",
            (title, url, tags, content, summary) # <-- CORRECTED VALUES TUPLE
        )
        self.conn.commit()

    def fetch_summary_resources(self):
        self.cursor.execute("""
            SELECT id, title, url, tags, date_added 
            FROM resources 
            ORDER BY date_added DESC
        """)
        return [tuple(row) for row in self.cursor.fetchall()]

    def fetch_resource_details(self, resource_id):
        self.cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        return self.cursor.fetchone() 

    def search_resources(self, search_term):
        term = f'%{search_term.lower()}%'
        
        # Searching across title, tags, and full_content (summaries implicitly included in full_content search)
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
        self.conn.close()

# --- RESOURCE HUB APP CLASS (CTk Implementation) ---

class ResourceHubApp:
    def __init__(self, root):
        self.root = root 
        self.root.title("ResourceHub - Knowledge Manager")
        
        # --- CTk Setup ---
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Initialize variables before widgets are created
        self.search_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.tags_var = tk.StringVar()

        self.db = DBManager()
        
        self.create_main_widgets()
        self.load_resources()

    def create_main_widgets(self):
        """Sets up the modern CTk application layout."""
        
        # 1. Configure the main grid layout
        self.root.grid_columnconfigure(0, weight=1) 
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_rowconfigure(3, weight=1) 
        
        # --- ROW 0: Top Search/Action Frame (CTkFrame & CTk widgets) ---
        self.top_frame = ctk.CTkFrame(self.root, fg_color="transparent") 
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        
        # 1. Search Label (CTkLabel)
        ctk.CTkLabel(self.top_frame, text="🔍 Search:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        # 2. Search Entry Widget (CTkEntry)
        self.search_entry = ctk.CTkEntry(self.top_frame, textvariable=self.search_var, placeholder_text="Search Title, Tags, or Content...")
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda event: self.search_handler())

        # 3. Search Button (CTkButton)
        self.search_button = ctk.CTkButton(self.top_frame, text="Search", command=self.search_handler, width=80)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        # 4. Clear Button (CTkButton)
        self.clear_button = ctk.CTkButton(self.top_frame, text="Clear", command=self.clear_search, width=60)
        self.clear_button.pack(side=tk.LEFT) 


        # --- ROW 2: Input Form Frame (CTkFrame & CTk widgets) ---
        self.input_frame = ctk.CTkFrame(self.root, fg_color="transparent", border_width=1)
        self.input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5) 
        self.input_frame.grid_columnconfigure(1, weight=1) 

        # 1. Title Input (CTkLabel and CTkEntry)
        ctk.CTkLabel(self.input_frame, text="Title:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ctk.CTkEntry(self.input_frame, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # 2. URL Input (CTkLabel and CTkEntry)
        ctk.CTkLabel(self.input_frame, text="URL:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = ctk.CTkEntry(self.input_frame, textvariable=self.url_var)
        self.url_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # 3. Tags Input (CTkLabel and CTkEntry)
        ctk.CTkLabel(self.input_frame, text="Tags:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.tags_entry = ctk.CTkEntry(self.input_frame, textvariable=self.tags_var, placeholder_text="comma-separated")
        self.tags_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # 4. Save Button (CTkButton - Custom Color)
        self.save_button = ctk.CTkButton(self.input_frame, text="SAVE RESOURCE & SCRAPE", 
                                         command=self.add_resource_handler,
                                         fg_color="#1F9E3B", hover_color="#187D2F") 
        self.save_button.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=(10, 5), pady=5)


        # --- ROW 3: Main Content (List and Detail Panes) ---

        # List Frame (Treeview container - CTkFrame)
        list_frame = ctk.CTkFrame(self.root, corner_radius=0) 
        list_frame.grid(row=3, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Note: Treeview is still standard ttk
        columns = ('ID', 'Title', 'URL', 'Tags', 'Date Added')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        style = ttk.Style(self.root)
        style.theme_use('default') 

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


        # Detail Pane (Scraped Content Viewer - CTkFrame)
        detail_frame = ctk.CTkFrame(self.root, corner_radius=0)
        detail_frame.grid(row=3, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10)) 
        detail_frame.grid_rowconfigure(1, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)

        # Label for context (CTkLabel)
        self.detail_label = ctk.CTkLabel(detail_frame, text="Resource Details (Full Content):", font=("Arial", 14, "bold"))
        self.detail_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Text widget for content display (CTkTextbox)
        self.content_text = ctk.CTkTextbox(detail_frame, wrap="word", state="disabled", font=('Arial', 11))
        self.content_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Bind the selection event 
        self.tree.bind('<<TreeviewSelect>>', self.show_resource_details)

    # --- Support Methods ---

    def load_resources(self, data=None):
        """Clears the Treeview and loads resources from the database."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if data is None:
            data = self.db.fetch_summary_resources()
            
        for row in data:
            self.tree.insert('', tk.END, values=row)


    def show_resource_details(self, event):
        """Event handler for Treeview selection. Displays the SUMMARY prominently."""
        selected_item = self.tree.focus()
        if not selected_item:
            return

        item_values = self.tree.item(selected_item, 'values')
        resource_id = item_values[0]
        resource = self.db.fetch_resource_details(resource_id) # fetches all columns, including summary_content
        
        if resource:
            # --- CORRECTED DISPLAY LOGIC to show summary prominently ---
            content_to_display = (
                f"Title: {resource['title']}\n"
                f"URL: {resource['url']}\n"
                f"Tags: {resource['tags']}\n"
                f"Date Added: {resource['date_added']}\n"
                f"\n--- 💡 SUMMARY ---\n"
                f"{resource['summary_content']}\n" # <-- SUMMARY CONTENT HERE
                f"\n--- RAW CONTENT ---\n"
                f"{resource['full_content']}"
            )
            
            # Use CTkTextbox methods
            self.content_text.configure(state="normal")
            self.content_text.delete('0.0', 'end')
            self.content_text.insert('0.0', content_to_display)
            self.content_text.configure(state="disabled")
            
            self.detail_label.configure(text=f"Resource Details: {resource['title']}") 

    def search_handler(self):
        """Retrieves the search term, queries the database, and updates the Treeview."""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            self.load_resources()
            return

        results = self.db.search_resources(search_term)
        
        if results:
            self.load_resources(data=results)
            self.detail_label.configure(text=f"Search Results: {len(results)} items found for '{search_term}'")
        else:
            self.load_resources(data=[])
            messagebox.showinfo("Search Result", f"No resources found matching '{search_term}'.")


    def clear_search(self):
        """Clears the search bar and reloads all resources into the Treeview."""
        self.search_var.set("") 
        self.load_resources() 
        self.detail_label.configure(text="Resource Details (Full Content):") 
    
    def add_resource_handler(self):
        """
        Handles form submission, calls scraper, generates summary, and saves to DB.
        This method is now correctly integrated with the Gemini API (via summarize_content).
        """
        title = self.title_var.get().strip()
        url = self.url_var.get().strip()
        tags = self.tags_var.get().strip()
        
        if not title:
            messagebox.showerror("Input Error", "Title is required for every resource.")
            return
        
        # Initialize variables
        final_summary = "[No Summary Generated]"
        
        if url.startswith('http'):
            try:
                # 1. Scraping
                self.save_button.configure(text="SCRAPING...", state="disabled")
                self.root.update()
                
                scraped_title, full_content = scrape_url(url)
                final_title = title if len(title) > 5 else scraped_title
                
                # 2. Summarization (NEW STEP)
                self.save_button.configure(text="SUMMARIZING...", state="disabled")
                self.root.update()
                final_summary = summarize_content(full_content)
                
            except Exception as e:
                messagebox.showwarning("Scraping Failed", f"Could not process URL. Saving title only. Error: {e}")
                final_title = title
                full_content = f"[SCRAPING FAILED] Could not retrieve content from {url}"
                final_summary = "[Summary Failed due to Scrape Error]"
        else:
            # Handle notes, snippets, or resources without a URL
            final_title = title
            full_content = f"User Note/Snippet: {title} (No URL provided)"
            final_summary = "[User Note - Not Summarized]"

        # 3. Save to Database (Passing the summary)
        self.db.add_resource(final_title, url, tags, full_content, final_summary)
        
        # 4. Cleanup and Refresh
        self.title_var.set("")
        self.url_var.set("")
        self.tags_var.set("")
        self.load_resources() 
        self.save_button.configure(text="SAVE RESOURCE & SCRAPE", state="normal")
        messagebox.showinfo("Success", f"Resource '{final_title}' saved successfully!")


# --- MAIN EXECUTION BLOCK ---


if __name__ == '__main__':
    try:
        root = ctk.CTk()
        root.geometry("1200x800")
        app = ResourceHubApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'app' in locals() and hasattr(app, 'db'):
            app.db.close()
            print("Database connection closed.")