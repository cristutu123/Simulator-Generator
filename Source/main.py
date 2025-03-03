import tkinter as tk
from objects import TestStep, TestCase, Argument, Command
import interface




# Start the application
if __name__ == "__main__":
 
    root = tk.Tk()
    app = interface.App(root)
    root.mainloop()
