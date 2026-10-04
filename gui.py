import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date, timedelta
import database
import auth

class ToolLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project 11 - Community Tool Library")
        self.root.geometry("850x650") 
        self.current_user = None
        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        self.show_login()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # -- Authentication --
    def show_login(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Staff Login", font=("Arial", 16, "bold")).pack(pady=40)
        
        tk.Label(self.main_frame, text="Username:").pack()
        self.user_entry = tk.Entry(self.main_frame)
        self.user_entry.pack(pady=5)
        
        tk.Label(self.main_frame, text="Password:").pack()
        self.pass_entry = tk.Entry(self.main_frame, show="*")
        self.pass_entry.pack(pady=5)
        
        tk.Button(self.main_frame, text="Login", command=self.login, width=15).pack(pady=5)
        tk.Button(self.main_frame, text="Register New User", command=self.register_user, width=15).pack(pady=5)

    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if auth.verify_login(username, password):
            self.current_user = username
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    def register_user(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please fill in both fields to register.")
            return
            
        if auth.register_staff(username, password):
            join_date = date.today().strftime("%Y-%m-%d")
            database.add_member(username, "Not provided", join_date)
            
            messagebox.showinfo("Success", f"User '{username}' created and added as a member! You can now log in.")
            self.user_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Username already exists. Choose another.")

    # -- Dashboard --
    def show_dashboard(self):
        self.clear_frame()
        
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_tools = tk.Frame(notebook)
        self.tab_members = tk.Frame(notebook)
        
        notebook.add(self.tab_tools, text="Manage Tools & Loans")
        notebook.add(self.tab_members, text="Manage Members")
        
        self.setup_tools_tab()
        self.setup_members_tab()
        
        tk.Button(self.main_frame, text="Log Out", command=self.show_login).pack(pady=5)

    # -- Members Tab --
    def setup_members_tab(self):
        form_frame = tk.Frame(self.tab_members)
        form_frame.pack(pady=10, fill="x")
        
        tk.Label(form_frame, text="Add New Member", font=("Arial", 12, "bold")).pack()
        
        tk.Label(form_frame, text="Name:").pack()
        self.mem_name = tk.Entry(form_frame)
        self.mem_name.pack(pady=5)
        
        tk.Label(form_frame, text="Contact Number:").pack()
        self.mem_contact = tk.Entry(form_frame)
        self.mem_contact.pack(pady=5)
        
        tk.Button(form_frame, text="Register Member", command=self.add_member).pack(pady=10)
        
        list_frame = tk.Frame(self.tab_members)
        list_frame.pack(pady=10, fill="both", expand=True, padx=10)
        
        tk.Label(list_frame, text="Registered Members", font=("Arial", 12, "bold")).pack(pady=5)
        
        columns = ("ID", "Name", "Contact Number", "Join Date")
        self.member_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.member_tree.heading(col, text=col)
            self.member_tree.column(col, width=150) 
            
        self.member_tree.pack(pady=5, fill="both", expand=True)
        
        action_frame = tk.Frame(list_frame)
        action_frame.pack(pady=5)
        
        tk.Button(action_frame, text="Edit Selected Member", command=self.edit_member).grid(row=0, column=0, padx=10)
        tk.Button(action_frame, text="Delete Selected Member", command=self.delete_member, fg="red").grid(row=0, column=1, padx=10)
        
        self.load_members()

    def load_members(self):
        for row in self.member_tree.get_children():
            self.member_tree.delete(row)
            
        members = database.get_all_members()
        for row in members:
            self.member_tree.insert("", tk.END, values=row)
            
        self.update_member_dropdown(members)

    def add_member(self):
        name = self.mem_name.get()
        contact = self.mem_contact.get()
        join_date = date.today().strftime("%Y-%m-%d")
        
        if not name or not contact:
            messagebox.showwarning("Warning", "All fields are required.")
            return
        if not contact.isdigit():
            messagebox.showwarning("Validation Error", "Please enter a valid numeric format for the contact number.")
            return
            
        database.add_member(name, contact, join_date)
        messagebox.showinfo("Success", f"Member '{name}' added successfully.")
        self.mem_name.delete(0, tk.END)
        self.mem_contact.delete(0, tk.END)
        self.load_members()

    def edit_member(self):
        selected = self.member_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member from the list to edit.")
            return
            
        member_id, name, contact, join_date = self.member_tree.item(selected[0], "values")
        
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Member")
        edit_win.geometry("300x260") 
        
        tk.Label(edit_win, text="Update Name:").pack(pady=5)
        name_var = tk.StringVar(value=name)
        tk.Entry(edit_win, textvariable=name_var).pack(pady=2)
        
        tk.Label(edit_win, text="Update Contact:").pack(pady=5)
        contact_var = tk.StringVar(value=contact)
        tk.Entry(edit_win, textvariable=contact_var).pack(pady=2)
        
        tk.Label(edit_win, text="Update Join Date (YYYY-MM-DD):").pack(pady=5)
        date_var = tk.StringVar(value=join_date)
        tk.Entry(edit_win, textvariable=date_var).pack(pady=2)
        
        def save_changes():
            new_name = name_var.get()
            new_contact = contact_var.get()
            new_date = date_var.get()
            
            if not new_name or not new_contact or not new_date:
                messagebox.showwarning("Warning", "Fields cannot be empty.")
                return
            
            database.update_member(member_id, new_name, new_contact, new_date)
            self.load_members()
            edit_win.destroy()
            messagebox.showinfo("Success", "Member updated successfully.")
            
        tk.Button(edit_win, text="Save Changes", command=save_changes).pack(pady=15)

    def delete_member(self):
        selected = self.member_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member from the list to delete.")
            return
            
        member_id, name, contact, _ = self.member_tree.item(selected[0], "values")
        
        if database.member_has_active_loans(member_id):
            messagebox.showerror("Error", f"Cannot delete '{name}' because they have active tool loans. Return the tools first.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete member '{name}'?")
        if confirm:
            database.delete_member(member_id)
            self.load_members()
            messagebox.showinfo("Success", f"Member '{name}' was deleted successfully.")

    # -- Tools Tab --
    def setup_tools_tab(self):
        add_frame = tk.Frame(self.tab_tools)
        add_frame.pack(pady=10, fill="x")
        
        tk.Label(add_frame, text="Add New Tool", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=5, pady=5)
        
        tk.Label(add_frame, text="Tool Name:").grid(row=1, column=0, padx=5)
        self.tool_name_entry = tk.Entry(add_frame)
        self.tool_name_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(add_frame, text="Category:").grid(row=1, column=2, padx=5)
        self.tool_category_cb = ttk.Combobox(add_frame, values=["Power Tools", "Gardening"], state="readonly", width=15)
        self.tool_category_cb.grid(row=1, column=3, padx=5)
        self.tool_category_cb.current(0) 
        
        tk.Button(add_frame, text="Register Tool", command=self.add_tool).grid(row=1, column=4, padx=10)

        list_frame = tk.Frame(self.tab_tools)
        list_frame.pack(pady=5, fill="both", expand=True, padx=10)
        
        columns = ("ID", "Name", "Category", "Status", "Borrowed By", "Due Date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.column("ID", width=40)
        self.tree.column("Name", width=180)
        self.tree.column("Category", width=110)
        self.tree.column("Status", width=90)
        self.tree.column("Borrowed By", width=130)
        self.tree.column("Due Date", width=110)
        
        self.tree.pack(pady=5, fill="both", expand=True)
        
        btn_frame = tk.Frame(self.tab_tools)
        btn_frame.pack(pady=15)
        
        tk.Label(btn_frame, text="Select Member:").grid(row=0, column=0, padx=5)
        
        self.borrow_member_cb = ttk.Combobox(btn_frame, state="readonly", width=25)
        self.borrow_member_cb.grid(row=0, column=1, padx=5)
        
        tk.Button(btn_frame, text="Borrow Tool", command=self.borrow_tool).grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="Return Tool", command=self.return_tool).grid(row=0, column=3, padx=10)
        tk.Button(btn_frame, text="Delete Tool", command=self.delete_tool, fg="red").grid(row=0, column=4, padx=10)
        
        self.load_tools()

    def update_member_dropdown(self, members=None):
        if members is None:
            members = database.get_all_members()
            
        member_list = [f"{m[0]} - {m[1]}" for m in members]
        
        if hasattr(self, 'borrow_member_cb'):
            self.borrow_member_cb['values'] = member_list
            if member_list:
                self.borrow_member_cb.current(0)
            else:
                self.borrow_member_cb.set('')

    def add_tool(self):
        name = self.tool_name_entry.get()
        category_name = self.tool_category_cb.get()
        
        if not name:
            messagebox.showwarning("Warning", "Tool name is required.")
            return
            
        database.add_tool(name, category_name)
        messagebox.showinfo("Success", f"Tool '{name}' registered successfully.")
        self.tool_name_entry.delete(0, tk.END)
        self.load_tools()

    def load_tools(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for row in database.get_all_tools():
            self.tree.insert("", tk.END, values=row)

    def borrow_tool(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a tool to borrow.")
            return
            
        tool_id, _, _, status, _, _ = self.tree.item(selected[0], "values")
        selected_member_str = self.borrow_member_cb.get()
        
        if status == "Borrowed":
            messagebox.showerror("Error", "Tool is already borrowed.")
            return
        if not selected_member_str:
            messagebox.showerror("Error", "Please select a member from the dropdown.")
            return
            
        # Extract member_id from Combobox string
        member_id = int(selected_member_str.split(" - ")[0])
            
        loan_date = date.today().strftime("%Y-%m-%d")
        due_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        database.borrow_tool(tool_id, member_id)
        
        self.load_tools()
        messagebox.showinfo("Success", "Tool borrowed successfully.")

    def return_tool(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a tool to return.")
            return
            
        tool_id, _, _, status, _, _ = self.tree.item(selected[0], "values")
        
        if status == "Available":
            messagebox.showinfo("Info", "Tool is already available.")
            return
            
        return_date = date.today().strftime("%Y-%m-%d")
        database.return_tool(tool_id)
        
        self.load_tools()
        messagebox.showinfo("Success", "Tool returned successfully.")

    def delete_tool(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a tool to delete.")
            return
            
        tool_id, name, _, status, _, _ = self.tree.item(selected[0], "values")
        
        if status == "Borrowed":
            messagebox.showerror("Error", f"Cannot delete '{name}' because it is currently borrowed. Return it first.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}' from the library?")
        if confirm:
            database.delete_tool(tool_id)
            self.load_tools()
            messagebox.showinfo("Success", f"Tool '{name}' was deleted successfully.")