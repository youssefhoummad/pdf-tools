import tkinter as tk
from tkinter import ttk


class CustomEntry(ttk.Entry):
  """a Entry binding width up & down key to crease or increse number, placeholder """
  def __init__(self, root, **kw): #, placeholder=''
    ttk.Entry.__init__(self, root, width=7, font=(None, 11),**kw) #, foreground="gray"

    self.bind("<Up>", self.handleUp)
    self.bind("<Down>", self.handleDown)

    # self.bind('<FocusIn>',self.focus_in)
    # self.bind('<FocusOut>',self.focus_out)

    # self.set(placeholder)
    # self.placeholder = placeholder


  def handleUp(self, event):
    if not self.get().isdigit() : self.set(0)
    self.set(int(self.get()) + 1)


  def handleDown(self, event):
    if not self.get().isdigit() : self.set(0)
    if int(self.get()) == 0: return
    self.set(int(self.get()) - 1)
    

  def focus_in(self, event):
    if self.get() == self.placeholder:
      self.set(0)
    self.configure(foreground='black')


  def focus_out(self, event):
    if self.get() == '':
      self.configure(foreground='gray')
      self.set(self.placeholder)


  def set(self, value):
    # # to provide error msg
    # # _tkinter.TclError: expected floating-point number but got ""
    # # the problem is th entry must be not empty
    # # so, i insert next value first, then delete previous value
    l = len(str(self.get()))
    self.insert(tk.END, value)   
    self.delete(0,l)
    return



if __name__ == "__main__":
  root = tk.Tk()
  text = tk.IntVar()
  text.set(3)
  entry1 = CustomEntry(root, textvariable=text, placeholder="top")
  entry1.pack(padx=20, pady=20)
  root.mainloop()
