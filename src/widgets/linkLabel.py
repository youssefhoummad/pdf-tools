from tkinter import Label

from webbrowser import open_new_tab


class LinkLabel(Label):
  def __init__(self, parent, text, link='', **kw):
    super().__init__(parent, **kw)
        
    self.config(cursor='hand2', text=text, bg=parent['bg'], font=('Calibri',12,"normal"))
    self.bind("<Button-1>", lambda e: open_new_tab(link))


if __name__ == "__main__":
  from tkinter import Tk
  root = Tk()
  label = LinkLabel(root, text="click me", link="www.google.com", anchor='nw', justify='right', fg='orange')
  label.pack()
  root.mainloop()