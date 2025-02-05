import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import configparser

class MySQLGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MySQL Connection Interface")
        self.root.geometry("800x600")

        # 讀取設定檔
        self.config = configparser.ConfigParser()
        self.config.read("db_config.ini")

        # 連線框架
        self.conn_frame = ttk.LabelFrame(self.root, text="Connection Details", padding="10")
        self.conn_frame.pack(fill="x", padx=10, pady=5)

        # 連線資訊輸入欄位
        self.create_connection_widgets()

        # SQL 查詢框架
        self.query_frame = ttk.LabelFrame(self.root, text="SQL Query", padding="10")
        self.query_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.query_text = tk.Text(self.query_frame, height=5)
        self.query_text.pack(fill="x", padx=5, pady=5)

        self.execute_btn = ttk.Button(self.query_frame, text="Execute Query", command=self.execute_query)
        self.execute_btn.pack(pady=5)

        # 結果顯示框架
        self.results_frame = ttk.LabelFrame(self.root, text="Results", padding="10")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(self.results_frame)
        self.tree.pack(fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.connection = None

    def create_connection_widgets(self):
        """建立 GUI 中的連線輸入框架"""
        labels = ["Host", "Port", "Database", "Username", "Password"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(self.conn_frame, text=f"{label}:").grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.conn_frame, show="*" if label == "Password" else None)
            entry.grid(row=i, column=1, padx=5, pady=5)
            
            # 如果有設定檔，就讀取預設值
            if label.lower() in self.config["DATABASE"]:
                entry.insert(0, self.config["DATABASE"][label.lower()])
            
            self.entries[label.lower()] = entry
        
        # 連線按鈕
        self.connect_btn = ttk.Button(self.conn_frame, text="Connect", command=self.connect_to_database)
        self.connect_btn.grid(row=len(labels), column=1, padx=5, pady=5)

    def connect_to_database(self):
        """嘗試連接 MySQL 資料庫"""
        try:
            self.connection = mysql.connector.connect(
                host=self.entries["host"].get(),
                port=self.entries["port"].get(),
                database=self.entries["database"].get(),
                user=self.entries["username"].get(),
                password=self.entries["password"].get(),
                connection_timeout=5  # 增加安全性，防止無限等待
            )

            if self.connection.is_connected():
                messagebox.showinfo("Success", "Connected to database successfully!")
        
        except Error as e:
            messagebox.showerror("Error", f"Connection failed: {e}")

    def execute_query(self):
        """執行 SQL 查詢"""
        if not self.connection or not self.connection.is_connected():
            messagebox.showerror("Error", "Not connected to database")
            return

        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return

        try:
            cursor = self.connection.cursor(prepared=True)  # 使用預備語句
            cursor.execute(query)

            # 清除舊結果
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 顯示欄位名稱
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                self.tree["columns"] = columns
                self.tree["show"] = "headings"

                for col in columns:
                    self.tree.heading(col, text=col)
                    self.tree.column(col, width=100)

                # 插入查詢結果
                for row in cursor.fetchall():
                    self.tree.insert("", tk.END, values=row)
            else:
                messagebox.showinfo("Success", "Query executed successfully, but no data returned.")

            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"Query execution failed: {e}")

    def close_connection(self):
        """關閉資料庫連線"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            messagebox.showinfo("Info", "Database connection closed.")

    def run(self):
        """運行 GUI 應用程式"""
        self.root.protocol("WM_DELETE_WINDOW", self.close_connection)  # 視窗關閉時自動關閉連線
        self.root.mainloop()

if __name__ == "__main__":
    app = MySQLGUI()
    app.run()
