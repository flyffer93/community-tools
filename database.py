import sqlite3
from datetime import date, timedelta

DB_NAME = "tool_library.db"

def connect():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT,
            join_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tools (
            tool_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            brand TEXT,
            serial_no TEXT,
            purchase_date TEXT,
            purchase_price REAL,
            status TEXT DEFAULT 'Available',
            FOREIGN KEY(category_id) REFERENCES Categories(category_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            tool_id INTEGER,
            loan_date TEXT,
            due_date TEXT,
            return_date TEXT,
            condition_out TEXT,
            condition_in TEXT,
            late_fee REAL DEFAULT 0.0,
            FOREIGN KEY(member_id) REFERENCES Members(member_id),
            FOREIGN KEY(tool_id) REFERENCES Tools(tool_id)
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM Tools")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT OR IGNORE INTO Staff (username, password) VALUES ('admin', 'admin')")
        
        cursor.execute("INSERT INTO Categories (category_name) VALUES ('Power Tools'), ('Garden Tools')")
        
        members_data = [
            ('Sarah Johnson', '821234567', 'sarah.j@email.com', '12 Oak St', '2026-01-01'),
            ('David Smith', '839876543', 'david.smith@mail.com', '88 Pine Ave', '2026-01-01'),
            ('Aisha Patel', '815559988', 'aisha.p@email.com', '5 Maple Rd', '2026-01-01')
        ]
        cursor.executemany("INSERT INTO Members (name, phone, email, address, join_date) VALUES (?, ?, ?, ?, ?)", members_data)

        tools_data = [
            ('Cordless Drill', 1, 'Bosch', 'BSC-88421', '2022-03-15', 3200.0, 'Available'),
            ('Circular Saw', 1, 'Makita', 'MK-22911', '2021-11-02', 4500.0, 'Available'),
            ('Hedge Trimmer', 2, 'Ryobi', 'RY-77812', '2023-09-20', 2800.0, 'Available'),
            ('Lawn Mower', 2, 'Husqvarna', 'HQ-44190', '2020-05-18', 7800.0, 'Available')
        ]
        cursor.executemany('''
            INSERT INTO Tools (name, category_id, brand, serial_no, purchase_date, purchase_price, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', tools_data)
        
    conn.commit()
    conn.close()

def get_all_tools():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.tool_id, t.name, c.category_name, t.status, 
               IFNULL(m.name, ''), IFNULL(l.due_date, '')
        FROM Tools t
        LEFT JOIN Categories c ON t.category_id = c.category_id
        LEFT JOIN Loans l ON t.tool_id = l.tool_id AND l.return_date IS NULL
        LEFT JOIN Members m ON l.member_id = m.member_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def borrow_tool(tool_id, member_id):
    conn = connect()
    cursor = conn.cursor()
    loan_date = date.today().strftime("%Y-%m-%d")
    due_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    cursor.execute("UPDATE Tools SET status = 'Borrowed' WHERE tool_id = ?", (tool_id,))
    cursor.execute('''
        INSERT INTO Loans (member_id, tool_id, loan_date, due_date, condition_out) 
        VALUES (?, ?, ?, ?, 'Good')
    ''', (member_id, tool_id, loan_date, due_date))
    
    conn.commit()
    conn.close()

def return_tool(tool_id):
    conn = connect()
    cursor = conn.cursor()
    return_date = date.today().strftime("%Y-%m-%d")
    
    cursor.execute("UPDATE Tools SET status = 'Available' WHERE tool_id = ?", (tool_id,))
    cursor.execute('''
        UPDATE Loans 
        SET return_date = ?, condition_in = 'Good'
        WHERE tool_id = ? AND return_date IS NULL
    ''', (return_date, tool_id))
    
    conn.commit()
    conn.close()

def add_member(name, phone, join_date):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Members (name, phone, join_date) VALUES (?, ?, ?)", (name, phone, join_date))
    conn.commit()
    conn.close()

def member_has_active_loans(member_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Loans WHERE member_id = ? AND return_date IS NULL", (member_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def delete_member(member_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Members WHERE member_id = ?", (member_id,))
    conn.commit()
    conn.close()

def delete_tool(tool_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tools WHERE tool_id = ?", (tool_id,))
    conn.commit()
    conn.close()

def get_active_members():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, name FROM Members")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_members():
    conn = connect()
    cursor = conn.cursor()
    # Henter ID, navn, telefon og dato for GUI-tabellen, men skjuler e-post og adresse
    cursor.execute("SELECT member_id, name, phone, join_date FROM Members")
    rows = cursor.fetchall()
    conn.close()
    return rows