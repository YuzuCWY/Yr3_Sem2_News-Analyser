from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
import pandas as pd
import jieba
from GoogleNews import GoogleNews
from wordcloudNdf import search
#for windows only
from tkinter import CENTER, Tk, Label, Button, Entry, Frame, END, Toplevel
from tkinter import ttk
from tkinter import messagebox
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
from urllib.parse import urlparse
#create database
from updateDB import DbOperations

class root_window:
    def __init__(self, root, db):
        self.db = db
        self.root = root
        self.root.title("新聞情感分析家 News Sentiment Analyser")
        self.root.geometry("1800x1000+40+40")

        head_title = Label(self.root, text="新聞情感分析家 News Sentiment Analyser",
                           font=("MSYH.ttc", 20, 'bold'),
                           justify=CENTER,
                           anchor="center").grid(padx=140, pady=30)

        self.crud_frame = Frame(self.root, highlightbackground="lightgrey",
                                highlightthickness=2, padx=10, pady=30)
        self.crud_frame.grid(padx=20)

        self.create_entry_labels()
        self.create_entry_boxes()
        self.create_crud_buttons()
        self.create_records_tree()

    def create_entry_labels(self):
        self.col_no, self.row_no = 0, 0
        Label(self.crud_frame, text="Search Key",
                  font=("Arial", 12)).grid(row=self.row_no,
                                           column=self.col_no,
                                           padx=5, pady=2)      

    def create_crud_buttons(self):
        self.row_no += 1
        self.col_no = 0
        buttons_info = (('Search & Save', 'green', self.save_record),
##                        ('Update', 'green', self.update_record),
                        ('Delete', 'red', self.delete_record),
                        ('Delete ALL Records', 'red', self.delete_allrecord),
##                        ('Copy Password', 'green', self.copy_password),
                        ('Show All Records', 'green', self.show_records))
        for btn_info in buttons_info:
            Button(self.crud_frame, text=btn_info[0], bg=btn_info[1], fg='white',
                   font=("Arial", 12), padx=5, pady=1, width=30,
                   command=btn_info[2]).grid(row=self.row_no,
                                             column=self.col_no,
                                             padx=0, pady=20)
            self.col_no += 1
            
    def create_entry_boxes(self):
        ##self.row_no += 1
        self.col_no +=1
        self.entry_boxes = []
        entry_box = Entry(self.crud_frame, width=100, font=("Arial", 12))
        entry_box.grid(row=self.row_no, column=self.col_no, padx=5, pady=2, columnspan=15)

        self.entry_boxes.append(entry_box)
        self.col_no += 1

    # CRUD Functions
    def save_record(self):
        search_key = self.entry_boxes[0].get()
        #print("\n\n",search_key)

        if not search_key:
            messagebox.showerror("Error", "Search Key cannot be empty!")
            return
        df = search(search_key)
        rows, cols = df.shape
        ## print(f"My DataFrame has {rows} rows and {cols} columns.")

        for i in range (rows):       
            article = df.loc[i, 'News Title']
            media = df.loc[i, 'Media']
            link = df.loc[i, 'Link']
            sentiment = df.loc[i, 'Sentiment Scores']
            
            data = {'search_key': search_key, 'article': article, 'media': media, 'link': link, 'sentiment': sentiment}
            self.db.create_record(data)
        self.show_records()
        df.drop(df.index, inplace=True)
        
    def delete_record(self):
        ID = self.entry_boxes[0].get()
        self.db.delete_record(ID)
        self.show_records()
        
    def delete_allrecord(self):
        self.db.delete_allrecord()
        self.show_records()
        
    def show_records(self):
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)

        records_list = self.db.show_records()
        #print(records_list)
        for record in records_list:
            self.records_tree.insert('', END, values=(record[0], record[1],
                                                      record[2], record[3], record[4], record[5], record[6]))
    def create_records_tree(self):
        # Create a frame to hold the Treeview widget with padding
        tree_frame = ttk.Frame(self.root, padding=20)

        columns = ('ID', 'created_date', 'search_key', 'article', 'media', 'link', 'sentiment')
        
        self.records_tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.records_tree.configure(style='Treeview', height=30)
        self.records_tree.heading('ID', text="ID", command=lambda: self.sort_column('ID', False))
        self.records_tree.heading('created_date', text="Browse Time", command=lambda: self.sort_column('created_date', False))
        self.records_tree.heading('search_key', text="Search Key", anchor=CENTER, command=lambda: self.sort_column('search_key', False))
        self.records_tree.heading('article', text="Article", anchor=CENTER, command=lambda: self.sort_column('article', False))
        self.records_tree.heading('media', text="Media", anchor=CENTER, command=lambda: self.sort_column('media', False))
        self.records_tree.heading('link', text="Link", anchor=CENTER, command=lambda: self.sort_column('link', False))
        self.records_tree.heading('sentiment', text="Sentiment", anchor=CENTER, command=lambda: self.sort_column('sentiment', False))
        
        self.records_tree.column('ID', width=50, anchor=CENTER)
        self.records_tree.column('created_date', width=180, anchor=CENTER)
        self.records_tree.column('search_key', width=150, anchor=CENTER)
        self.records_tree.column('article', width=700, anchor=CENTER)
        self.records_tree.column('media', width=150, anchor=CENTER)
        self.records_tree.column('link', width=300, anchor=CENTER)
        self.records_tree.column('sentiment', width=100, anchor=CENTER)
        
        # Increase font size using a custom style
        style = ttk.Style()
        style.configure('Treeview', font=('Arial', 12), height=20)

        # Apply the custom style to the Treeview widget
        self.records_tree.configure(style='Treeview')
        self.records_tree['displaycolumn'] = ('ID', 'created_date', 'search_key', 'article', 'media', 'link', 'sentiment')

        # Grid the Treeview widget inside the frame
        self.records_tree.grid(row=4, padx=20)

        # Grid the frame inside the window with padding
        tree_frame.grid(row=4, column=1, padx=20, pady=20)
            
        def item_selected(event):
            for selected_item in self.records_tree.selection():
                item = self.records_tree.item(selected_item)
                record = item['values']
                for entry_box, item in zip(self.entry_boxes, record):
                    entry_box.delete(0, END)
                    entry_box.insert(0, item)
        
        self.records_tree.bind('<<TreeviewSelect>>', item_selected)
        self.records_tree.grid(pady=10)
        

        
    def sort_column(self, column, reverse):
        # Get the current data in the treeview
        data = [(self.records_tree.set(child, column), child) for child in self.records_tree.get_children('')]
        
        # Reverse the order if already sorted by the same column
        data.sort(reverse=reverse)
        
        for index, (value, child) in enumerate(data):
            self.records_tree.move(child, '', index)
        
        # Reverse the sorting order for the next click
        self.records_tree.heading(column, command=lambda col=column: self.sort_column(col, not reverse))


    
if __name__ == "__main__":
    # Create table if does not exist
    db_class = DbOperations()
    db_class.create_table()

    # create window
    root = Tk()
    root_class = root_window(root, db_class)

    root.mainloop()
