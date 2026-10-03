import tkinter as tk
from database import setup_database
from gui import ToolLibraryApp

if __name__ == "__main__":
    setup_database()
    
    root = tk.Tk()
    app = ToolLibraryApp(root)
    root.mainloop()