import os
import tkinter as tk
from tkinter import ttk

# import sv_ttk

from app import App, TabedView, Model


basedir = os.path.dirname(__file__)

def main():

  root = tk.Tk()

  root.title("Pdf tools")
  root.geometry('872x420')
  root.iconbitmap(os.path.join(basedir, r"icon.ico"))
  root.resizable(width=False, height=False)

  app = App(root, TabedView, Model)
  # style.configure('TNotebook',height=40, width=80) # tabposition='wn' option to change position of tab
  style = ttk.Style()
  style.configure('TNotebook.Tab',padding=(10,2)) # tabposition='wn' option to change position of tab


  app.mainloop()

if __name__ == '__main__':
  main()