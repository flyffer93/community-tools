import sqlite3

DB_NAME = "tool_library.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS Staff (
                    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')
                    
    c.execute('''CREATE TABLE IF NOT EXISTS Categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT UNIQUE NOT NULL)''')
                    
    c.execute('''CREATE TABLE IF NOT EXISTS Members (
                    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_number TEXT NOT NULL,
                    join_date TEXT NOT NULL)''')
                    
    c.execute('''CREATE TABLE IF NOT EXISTS Tools (
                    tool_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    status TEXT NOT NULL DEFAULT 'Available',
                    FOREIGN KEY(category_id) REFERENCES Categories(category_id))''')
                    
    c.execute('''CREATE TABLE IF NOT EXISTS Loans (
                    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER,
                    tool_id INTEGER,
                    loan_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    return_date TEXT,
                    FOREIGN KEY(member_id) REFERENCES Members(member_id),
                    FOREIGN KEY(tool_id) REFERENCES Tools(tool_id))''')

    c.execute("INSERT OR IGNORE INTO Staff (username, password) VALUES ('admin', 'admin')")
    c.execute("INSERT OR IGNORE INTO Categories (category_name) VALUES ('Power Tools')")
    c.execute("INSERT OR IGNORE INTO Categories (category_name) VALUES ('Gardening')")
    
    # Prevent duplicate default data on startup
    c.execute("SELECT COUNT(*) FROM Tools")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO Tools (name, category_id, status) VALUES ('Bosch Drill', 1, 'Available'), ('Husqvarna Chainsaw', 2, 'Available')")
    
    conn.commit()
    conn.close()


# -- Members --
def get_all_members():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT member_id, name, contact_number, join_date FROM Members")
    data = c.fetchall()
    conn.close()
    return data

def add_member(name, contact, join_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO Members (name, contact_number, join_date) VALUES (?, ?, ?)", (name, contact, join_date))
    conn.commit()
    conn.close()

def update_member(member_id, name, contact, join_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE Members SET name=?, contact_number=?, join_date=? WHERE member_id=?", (name, contact, join_date, member_id))
    conn.commit()
    conn.close()

def member_has_active_loans(member_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM Loans WHERE member_id=? AND return_date IS NULL", (member_id,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def delete_member(member_id):
    conn = get_connection()
    c = conn.cursor()
    # Delete associated loans first to prevent orphaned records (FK constraint)
    c.execute("DELETE FROM Loans WHERE member_id=?", (member_id,))
    c.execute("DELETE FROM Members WHERE member_id=?", (member_id,))
    conn.commit()
    conn.close()


# -- Tools and Loans --
def get_all_tools():
    conn = get_connection()
    c = conn.cursor()
    query = '''
        SELECT 
            Tools.tool_id, 
            Tools.name, 
            Categories.category_name, 
            Tools.status,
            IFNULL(Members.name, '') AS borrowed_by,
            IFNULL(Loans.due_date, '') AS due_date
        FROM Tools 
        JOIN Categories ON Tools.category_id = Categories.category_id
        LEFT JOIN Loans ON Tools.tool_id = Loans.tool_id AND Loans.return_date IS NULL
        LEFT JOIN Members ON Loans.member_id = Members.member_id
    '''
    c.execute(query)
    data = c.fetchall()
    conn.close()
    return data

def add_tool(name, category_name):
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT category_id FROM Categories WHERE category_name=?", (category_name,))
    cat_result = c.fetchone()
    
    if cat_result:
        category_id = cat_result[0]
    else:
        c.execute("INSERT INTO Categories (category_name) VALUES (?)", (category_name,))
        category_id = c.lastrowid
        
    c.execute("INSERT INTO Tools (name, category_id, status) VALUES (?, ?, 'Available')", (name, category_id))
    conn.commit()
    conn.close()

def delete_tool(tool_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM Loans WHERE tool_id=?", (tool_id,))
    c.execute("DELETE FROM Tools WHERE tool_id=?", (tool_id,))
    conn.commit()
    conn.close()

def borrow_tool(tool_id, member_id, loan_date, due_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE Tools SET status='Borrowed' WHERE tool_id=?", (tool_id,))
    c.execute("INSERT INTO Loans (member_id, tool_id, loan_date, due_date) VALUES (?, ?, ?, ?)", 
              (member_id, tool_id, loan_date, due_date))
    conn.commit()
    conn.close()

def return_tool(tool_id, return_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE Tools SET status='Available' WHERE tool_id=?", (tool_id,))
    c.execute("UPDATE Loans SET return_date=? WHERE tool_id=? AND return_date IS NULL", (return_date, tool_id))
    conn.commit()
    conn.close()