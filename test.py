import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import threading
import os
import configparser

class FileUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Uploader")
        
        self.config = self.load_config()

        self.start_frame = tk.Frame(root)
        self.start_frame.pack(padx=10, pady=10)
        
        self.choice_label = tk.Label(self.start_frame, text="Choose data source:")
        self.choice_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.csv_button = tk.Button(self.start_frame, text="Load CSV", command=self.load_csv_ui)
        self.csv_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.folder_button = tk.Button(self.start_frame, text="Select Folder", command=self.select_folder_ui)
        self.folder_button.grid(row=1, column=1, padx=5, pady=5)
        
        self.main_frame = tk.Frame(root)
        
        self.file_path_entry = tk.Entry(self.main_frame, width=50)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.browse_button = tk.Button(self.main_frame, text="Browse...", command=self.browse_files)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.load_csv_button = tk.Button(self.main_frame, text="Load CSV", command=self.load_csv)
        
        self.table_frame = tk.Frame(self.main_frame)
        
        self.table_canvas = tk.Canvas(self.table_frame)
        self.table_scrollbar = tk.Scrollbar(self.table_frame, orient="vertical", command=self.table_canvas.yview)
        self.table_canvas.configure(yscrollcommand=self.table_scrollbar.set)
        
        self.horizontal_scrollbar = tk.Scrollbar(self.main_frame, orient="horizontal", command=self.table_canvas.xview)
        self.table_canvas.configure(xscrollcommand=self.horizontal_scrollbar.set)
        
        self.table_inner_frame = tk.Frame(self.table_canvas)
        
        self.table_inner_frame.bind("<Configure>", lambda e: self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all")))
        
        self.table_canvas.create_window((0, 0), window=self.table_inner_frame, anchor="nw")
        self.table_scrollbar.pack(side="right", fill="y")
        self.table_canvas.pack(side="top", fill="both", expand=True)
        
        self.horizontal_scroll_frame = tk.Frame(self.main_frame)
        self.horizontal_scroll_frame.pack(fill="x", side="bottom")
        self.horizontal_scrollbar.pack(in_=self.horizontal_scroll_frame, fill="x")

        self.add_column_button = tk.Button(self.main_frame, text="Add Column", command=self.add_column)
        self.upload_button = tk.Button(self.main_frame, text="Upload to Server", command=self.upload_to_server)
        
        self.data = None
        self.entries = []
        self.mode = None

        self.add_column_button.pack()
        self.upload_button.pack()
    
    def load_config(self):
        config = configparser.ConfigParser()
        config.read('rest_api.config')
        return {
            'host_url': config.get('API', 'host_url'),
            'username': config.get('API', 'username'),
            'password': config.get('API', 'password')
        }
    
    def load_csv_ui(self):
        self.mode = "csv"
        self.start_frame.pack_forget()
        self.main_frame.pack(padx=10, pady=10)
        self.load_csv_button.grid(row=1, column=0, columnspan=3, pady=10)
        self.table_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.add_column_button.grid(row=4, column=0, columnspan=3, pady=10)
        self.upload_button.grid(row=5, column=0, columnspan=3, pady=10)
    
    def select_folder_ui(self):
        self.mode = "folder"
        self.start_frame.pack_forget()
        self.main_frame.pack(padx=10, pady=10)
        self.browse_button.config(command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, padx=10, pady=10)
        self.file_path_entry.grid(row=1, column=1, padx=10, pady=10)
        self.table_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.add_column_button.grid(row=4, column=0, columnspan=3, pady=10)
        self.upload_button.grid(row=5, column=0, columnspan=3, pady=10)
    
    def browse_files(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, folder_path)
        self.select_folder(folder_path)
        
    def load_csv(self):
        file_path = self.file_path_entry.get()
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.display_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "No file selected.")
    
    def select_folder(self, folder_path):
        if folder_path:
            self.data = pd.DataFrame(columns=["File Path"])
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path)):
                    new_row = pd.DataFrame({"File Path": [file_path]})
                    self.data = pd.concat([self.data, new_row], ignore_index=True)
            self.display_data()
        else:
            messagebox.showwarning("Warning", "No folder selected.")
    
    def add_column(self):
        if self.data is not None:
            column_name = simpledialog.askstring("Input", "Enter column name:")
            if column_name:
                self.data[column_name] = ""
                self.display_data()
        else:
            messagebox.showwarning("Warning", "No data to add columns to.")
    
    def display_data(self):
        if self.data is not None:
            # Przechowanie bieżących danych wpisanych przez użytkownika
            current_data = {col: [] for col in self.data.columns}
            if self.entries:
                for i in range(len(self.entries)):
                    for j, col in enumerate(self.data.columns):
                        current_data[col].append(self.entries[i][j].get())
            
            for widget in self.table_inner_frame.winfo_children():
                widget.destroy()
            
            self.entries = []
            for i, col in enumerate(self.data.columns):
                label = tk.Label(self.table_inner_frame, text=col)
                label.grid(row=0, column=i, padx=5, pady=5)
            
            label_status = tk.Label(self.table_inner_frame, text="Status")
            label_status.grid(row=0, column=len(self.data.columns), padx=5, pady=5)
            
            for i, row in self.data.iterrows():
                row_entries = []
                for j, value in enumerate(row):
                    entry = tk.Entry(self.table_inner_frame)
                    entry.insert(0, str(value))  # Zamiana wartości na ciągi znaków
                    entry.grid(row=i+1, column=j, padx=5, pady=5)
                    row_entries.append(entry)
                
                status_label = tk.Label(self.table_inner_frame, text="Pending")
                status_label.grid(row=i+1, column=len(self.data.columns), padx=5, pady=5)
                row_entries.append(status_label)
                self.entries.append(row_entries)
            
            # Przywrócenie bieżących danych wpisanych przez użytkownika
            for col, values in current_data.items():
                if col in self.data.columns:
                    for i, value in enumerate(values):
                        self.entries[i][self.data.columns.get_loc(col)].delete(0, tk.END)
                        self.entries[i][self.data.columns.get_loc(col)].insert(0, str(value))

            self.adjust_window_width()
    
    def adjust_window_width(self):
        self.root.update_idletasks()
        table_width = sum(widget.winfo_reqwidth() for widget in self.table_inner_frame.winfo_children() if widget.winfo_manager() == 'grid')
        window_width = min(max(table_width, 800), 1000)
        self.root.geometry(f"{window_width}x{self.root.winfo_height()}")
        self.table_canvas.configure(width=window_width)
    
    def upload_to_server(self):
        if self.data is not None:
            threading.Thread(target=self.async_upload).start()
        else:
            messagebox.showwarning("Warning", "No data to upload.")
    
    def async_upload(self):
        for i, row in self.data.iterrows():
            row_data = {col: self.entries[i][j].get() for j, col in enumerate(self.data.columns)}
            self.update_status(i, "In progress")
            success = self.upload_row_to_server(row_data)
            self.update_status(i, "Sent" if success else "Error")
    
    def update_status(self, row_index, status):
        self.entries[row_index][-1].config(text=status)
    
    def upload_row_to_server(self, row_data):
        host_url = self.config['host_url']
        username = self.config['username']
        password = self.config['password']
        
        print(f"Uploading {row_data} to {host_url} with username {username}")
        
        # Przykładowe użycie w żądaniu HTTP
        response = requests.post(host_url, json=row_data, auth=(username, password))
        return response.status_code == 200

if __name__ == "__main__":
    root = tk.Tk()
    app = FileUploaderApp(root)
    root.mainloop()
