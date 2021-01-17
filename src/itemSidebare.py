import tkinter as tk
from tkinter import ttk
from .imageLabel import ImageLabel
from .constant import *



class ItemSidebare(tk.Frame):
  def __init__(self, parent, text, icon=None, command=None):
    ttk.Frame.__init__(self, parent)
    self.text = text
    self.command= command

    self.s = ttk.Style() 

  
    self.s.configure('Basic.TFrame', background='#F2F2F2')
    self.s.configure('Hover.TFrame', background='#DEDEDE')
    self.s.configure('Press.TFrame', background='#CFCFCF')
    self.s.configure('Basic.TLabel', background='#F2F2F2')
    self.s.configure('Hover.TLabel', background='#DEDEDE')
    self.s.configure('Press.TLabel', background='#CFCFCF')
    self.s.configure('TButton', background='white')

    self.config(style="Basic.TFrame")

    if icon:
      self.imageLabel = ImageLabel(self, image_path=icon, style="Basic.TLabel", width=28, height=28)
    else:
      self.imageLabel = ttk.Label(self, style="Basic.TLabel")

    self.textLabel = ttk.Label(self, text=text, style='Basic.TLabel', font=('Calibri',12,"bold"))
    
    self.imageLabel.pack(sid=START_DIR, pady=8, padx=START_PADDING_24)
    self.textLabel.pack(sid=START_DIR, padx=END_PADDING_10)

    if not icon: 
      self.imageLabel.pack(padx=0)
      self.textLabel.pack(padx=START_PADDING_24)


    self.bind("<ButtonPress-1>", self.on_press)
    self.bind("<ButtonRelease-1>", self.on_release)
    self.bind("<Enter>", self.on_hover)
    self.bind("<Leave>", self.on_leave)

    self.textLabel.bind("<ButtonPress-1>", self.on_press)
    self.textLabel.bind("<ButtonRelease-1>", self.on_release)
    self.textLabel.bind("<Enter>", self.on_hover)
    self.textLabel.bind("<Leave>", self.on_leave)

    self.imageLabel.bind("<ButtonPress-1>", self.on_press)
    self.imageLabel.bind("<ButtonRelease-1>", self.on_release)
    self.imageLabel.bind("<Enter>", self.on_hover)
    self.imageLabel.bind("<Leave>", self.on_leave)
  
  def on_hover(self, e):
    self.config(style="Hover.TFrame")
    self.textLabel.config(style="Hover.TLabel")
    self.imageLabel.config(style="Hover.TLabel")
  
  def on_press(self, e):
    self.config(style="Press.TFrame")
    self.textLabel.config(style="Press.TLabel")
    self.imageLabel.config(style="Press.TLabel")

  def on_leave(self, e):
    self.config(style="Basic.TFrame")
    self.textLabel.config(style="Basic.TLabel")
    self.imageLabel.config(style="Basic.TLabel")

  def on_release(self, e):
    self.on_hover(e=None)
    self.command()


# if __name__ == "__main__":
#     root = tk.Tk()
#     f = SideFrame(root, "Color Picker", icon=r'3.png')
#     f.pack(fill='both', expand='True')
#     e = SideFrame(root, "text", icon=r'2.png')
#     e.pack(fill='both', expand='True')
#     root.mainloop()
