import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class NoteManager:
    def __init__(self):
        self.notes = {}
        self.next_id = 1

    def create_note(self, title, content, category="General"):
        note = {
            "id": self.next_id,
            "title": title,
            "content": content,
            "category": category,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        }
        self.notes[self.next_id] = note
        self.next_id += 1
        return note

    def get_note(self, note_id):
        return self.notes.get(note_id)

    def get_all_notes(self, category=None):
        return [note for note in self.notes.values() if note['category'] == category] if category else list(self.notes.values())

    def update_note(self, note_id, title=None, content=None, category=None):
        if note_id not in self.notes:
            return None
        if title:
            self.notes[note_id]["title"] = title
        if content:
            self.notes[note_id]["content"] = content
        if category:
            self.notes[note_id]["category"] = category
        self.notes[note_id]["updated_at"] = datetime.datetime.now()
        return self.notes[note_id]

    def delete_note(self, note_id):
        return self.notes.pop(note_id, None)

    def search_notes(self, query):
        query = query.lower()
        return [note for note in self.notes.values() if query in note["title"].lower() or query in note["content"].lower()]

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note Manager App")
        self.manager = NoteManager()
        self.current_note_id = None
        self.setup_ui()
        
        # Bind Ctrl+S to save
        self.root.bind('<Control-s>', lambda event: self.save_note())
        self.root.bind('<Control-n>', lambda event: self.new_note())

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Note list (left panel)
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        self.note_list = ttk.Treeview(list_frame, columns=("ID", "Title"), show="headings")
        self.note_list.heading("ID", text="ID")
        self.note_list.heading("Title", text="Title")
        self.note_list.column("ID", width=50)
        self.note_list.column("Title", width=150)
        self.note_list.pack(fill=tk.Y, expand=True)
        self.note_list.bind('<<TreeviewSelect>>', self.load_selected_note)

        # Button controls
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(buttons_frame, text="New", command=self.new_note).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_note).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(buttons_frame, text="Search", command=self.search_notes).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Editor (right panel)
        editor_frame = ttk.Frame(main_frame)
        editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Title field
        self.title_var = tk.StringVar()
        ttk.Label(editor_frame, text="Title:").pack(anchor=tk.W)
        self.title_entry = ttk.Entry(editor_frame, textvariable=self.title_var)
        self.title_entry.pack(fill=tk.X)

        # Content editor
        ttk.Label(editor_frame, text="Content:").pack(anchor=tk.W, pady=(5, 0))
        self.text_editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD)
        self.text_editor.pack(fill=tk.BOTH, expand=True)

        # Save button
        ttk.Button(editor_frame, text="Save", command=self.save_note).pack(fill=tk.X, pady=(5, 0))

        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(editor_frame, textvariable=self.status_var).pack(anchor=tk.W)

        self.refresh_notes()

    def new_note(self):
        self.current_note_id = None
        self.title_var.set("")
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.focus()
        self.status_var.set("New note created")

    def load_selected_note(self, event=None):
        selection = self.note_list.selection()
        if not selection:
            return
            
        note_id = self.note_list.item(selection[0])["values"][0]
        note = self.manager.get_note(note_id)
        
        if note:
            self.current_note_id = note_id
            self.title_var.set(note["title"])
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(tk.END, note["content"])
            self.status_var.set(f"Editing note {note_id}")

    def save_note(self):
        title = self.title_var.get().strip()
        content = self.text_editor.get(1.0, tk.END).strip()
        
        if not title:
            messagebox.showerror("Error", "Title cannot be empty!")
            return
            
        if not content:
            messagebox.showerror("Error", "Content cannot be empty!")
            return

        if self.current_note_id:
            # Update existing note
            self.manager.update_note(self.current_note_id, title=title, content=content)
            self.status_var.set(f"Note {self.current_note_id} updated")
        else:
            # Create new note
            note = self.manager.create_note(title, content)
            self.current_note_id = note["id"]
            self.status_var.set(f"Note {note['id']} created")

        self.refresh_notes()

    def delete_note(self):
        if not self.current_note_id:
            messagebox.showerror("Error", "No note selected to delete!")
            return
            
        if messagebox.askyesno("Confirm Delete", "Delete this note?"):
            self.manager.delete_note(self.current_note_id)
            self.new_note()  # Clear editor
            self.refresh_notes()
            self.status_var.set(f"Note deleted")

    def refresh_notes(self):
        # Save current selection
        selected_id = self.current_note_id
        
        # Clear and repopulate list
        self.note_list.delete(*self.note_list.get_children())
        for note in self.manager.get_all_notes():
            self.note_list.insert("", tk.END, values=(note["id"], note["title"]))
        
        # Restore selection if it still exists
        if selected_id:
            for child in self.note_list.get_children():
                if self.note_list.item(child)["values"][0] == selected_id:
                    self.note_list.selection_set(child)
                    break

    def search_notes(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Notes")

        ttk.Label(search_window, text="Search Query:").pack(padx=10, pady=5)
        search_entry = ttk.Entry(search_window, width=40)
        search_entry.pack(padx=10, pady=5)
        search_entry.focus()

        result_tree = ttk.Treeview(search_window, columns=("ID", "Title", "Preview"), show="headings")
        result_tree.heading("ID", text="ID")
        result_tree.heading("Title", text="Title")
        result_tree.heading("Preview", text="Preview")
        result_tree.column("ID", width=50)
        result_tree.column("Title", width=150)
        result_tree.column("Preview", width=250)
        result_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def perform_search():
            query = search_entry.get().strip()
            if not query:
                messagebox.showerror("Error", "Please enter a search term")
                return

            results = self.manager.search_notes(query)
            result_tree.delete(*result_tree.get_children())
            
            if not results:
                messagebox.showinfo("No Results", "No matching notes found")
                return

            for note in results:
                preview = note["content"][:50] + ("..." if len(note["content"]) > 50 else "")
                result_tree.insert("", tk.END, values=(note["id"], note["title"], preview))

        search_button = ttk.Button(search_window, text="Search", command=perform_search)
        search_button.pack(pady=5)
        
        # Bind Enter key to search
        search_window.bind('<Return>', lambda event: perform_search())

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()
