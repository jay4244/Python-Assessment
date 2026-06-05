import tkinter as tk
from tkinter import messagebox
import os
import glob

# Constants
POSTS_DIR = "posts"

class User:
    def __init__(self, name):
        self.name = name.strip()

class Post:
    def __init__(self, user, title, content):
        self.user = user
        self.title = title.strip()
        self.content = content.strip()
        
    def get_filename(self):
        # Sanitize filename (basic)
        safe_title = "".join([c for c in self.title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        safe_title = safe_title.replace(' ', '_')
        safe_name = "".join([c for c in self.user.name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        safe_name = safe_name.replace(' ', '_')
        return f"{safe_name}_{safe_title}.txt"

class MiniBlogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniBlog")
        self.root.geometry("650x550")
        
        # Ensure posts directory exists
        os.makedirs(POSTS_DIR, exist_ok=True)
        
        self.setup_ui()
        self.refresh_post_list()

    def setup_ui(self):
        # Left Frame: Create Post
        create_frame = tk.LabelFrame(self.root, text="Create New Post", padx=10, pady=10)
        create_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(create_frame, text="Author Name:").pack(anchor=tk.W)
        self.name_entry = tk.Entry(create_frame, width=30)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(create_frame, text="Post Title:").pack(anchor=tk.W)
        self.title_entry = tk.Entry(create_frame, width=30)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(create_frame, text="Post Content:").pack(anchor=tk.W)
        self.content_text = tk.Text(create_frame, width=30, height=15)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        save_btn = tk.Button(create_frame, text="Save Post", command=self.save_post, bg="#4CAF50", fg="white")
        save_btn.pack(fill=tk.X)

        # Right Frame: View Posts
        view_frame = tk.LabelFrame(self.root, text="View Saved Posts", padx=10, pady=10)
        view_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(view_frame, text="Select Post:").pack(anchor=tk.W)
        
        # Listbox with Scrollbar
        list_frame = tk.Frame(view_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.posts_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.posts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.posts_listbox.yview)

        btn_frame = tk.Frame(view_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = tk.Button(btn_frame, text="Refresh", command=self.refresh_post_list)
        refresh_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        view_btn = tk.Button(btn_frame, text="View Post", command=self.view_post, bg="#2196F3", fg="white")
        view_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        tk.Label(view_frame, text="Post Content:").pack(anchor=tk.W)
        self.view_text = tk.Text(view_frame, width=30, height=10, state=tk.DISABLED)
        self.view_text.pack(fill=tk.BOTH, expand=True)

    def save_post(self):
        name = self.name_entry.get()
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END)

        if not name.strip() or not title.strip() or not content.strip():
            messagebox.showwarning("Input Error", "Name, Title, and Content cannot be empty.")
            return

        user = User(name)
        post = Post(user, title, content)
        
        filename = post.get_filename()
        if not filename or filename == ".txt":
             messagebox.showwarning("Input Error", "Please use valid characters in name and title.")
             return
             
        filepath = os.path.join(POSTS_DIR, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(f"Title: {post.title}\n")
                file.write(f"Author: {post.user.name}\n")
                file.write("-" * 30 + "\n")
                file.write(post.content)
            
            messagebox.showinfo("Success", f"Post saved successfully as {filename}")
            
            # Clear fields after saving
            self.title_entry.delete(0, tk.END)
            self.content_text.delete("1.0", tk.END)
            
            # Refresh list
            self.refresh_post_list()
            
        except IOError as e:
            messagebox.showerror("File Error", f"An error occurred while saving the file: {e}")

    def refresh_post_list(self):
        self.posts_listbox.delete(0, tk.END)
        try:
            # List all txt files in posts directory
            files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.txt')]
            for f in files:
                self.posts_listbox.insert(tk.END, f)
        except OSError as e:
            messagebox.showerror("Error", f"Could not access posts directory: {e}")

    def view_post(self):
        selected_indices = self.posts_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a post to view.")
            return

        filename = self.posts_listbox.get(selected_indices[0])
        filepath = os.path.join(POSTS_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
            self.view_text.config(state=tk.NORMAL)
            self.view_text.delete("1.0", tk.END)
            self.view_text.insert(tk.END, content)
            self.view_text.config(state=tk.DISABLED)
        except FileNotFoundError:
            messagebox.showerror("File Error", "The selected file could not be found.")
            self.refresh_post_list() # Remove from list
        except IOError as e:
            messagebox.showerror("File Error", f"An error occurred while reading the file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniBlogApp(root)
    root.mainloop()
