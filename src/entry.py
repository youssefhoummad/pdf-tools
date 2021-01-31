import tkinter as tk
from tkinter import ttk


class NumEntry(ttk.Entry):
  """a Entry binding width up & down key to crease or increse number, placeholder """
  def __init__(self, root, placeholder='',_min=0, **kw): #, placeholder=''
    ttk.Entry.__init__(self, root, width=10, foreground="gray",font=(None, 11),**kw) #, foreground="gray"

    self.bind("<Up>", self.handleUp)
    self.bind("<Down>", self.handleDown)

    self.bind('<FocusIn>',self.focus_in)
    self.bind('<FocusOut>',self.focus_out)

    self.set(placeholder)
    self.placeholder = placeholder
    self.min = _min


  def handleUp(self, event):
    if not self.get().isdigit() : self.set(0)
    self.set(int(self.get()) + 1)


  def handleDown(self, event):
    if not self.get().isdigit() : self.set(0)
    if int(self.get()) == self.min: return
    self.set(int(self.get()) - 1)
    

  def focus_in(self, event):
    if self.get() == self.placeholder:
      self.set(str(self.min))
    self.configure(foreground='black')


  def focus_out(self, event):
    if self.get() == '':
      self.configure(foreground='gray')
      self.set(self.placeholder)


  def set(self, value):
    self.delete(0, tk.END)
    self.insert(tk.END, value)   
    

class EntryWithPlusMinus(tk.Frame):
  def __init__(self, master):
    super().__init__(master)

    self.plus = tk.Button(self, text='+')
    self.entry =tk.Entry(self, width=6)
    self.minus = tk.Button(self, text='-')

    self.plus.pack(side='left')
    self.entry.pack(side='left')
    self.minus.pack(side='left')

if __name__ == "__main__":
  root = tk.Tk()
  text = tk.StringVar()
  entry1 = EntryWithPlusMinus(root)
  entry1.pack(padx=20, pady=20)


  root.mainloop()
