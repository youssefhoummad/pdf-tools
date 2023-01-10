import re
import tkinter as tk
from tkinter import ttk
import sys

from PIL import Image, ImageTk
from tkinterdnd2 import *




# Custom tree width
class TreeFiles(tk.Frame):

  def __init__(self, master=None, justify='left', extension=(), variable=None, add_files_text='add files', add_files_command=None, clear_file_text="", **kw):
    super().__init__(master, **kw)

    is_win11 = True if (sys.getwindowsversion().build > 20000) else False
    FONT_ICONS = 'Segoe Fluent Icons'  if  is_win11 else 'Segoe MDL2 Assets'

    self.variable = variable
    self.extension = extension 

    left, right = 'left', 'right'
    if justify=='right': left, right = right, left
    
    self.tree = ttk.Treeview(self, show='')
    self.tree["columns"]=("files")
    self.tree.heading("#0", text="files")
    
    s = ttk.Style()
    s.configure('icons-red.TButton', font=(FONT_ICONS, 12), foreground='red')
    s.configure('icons-green.TButton', font=(FONT_ICONS, 12), foreground='green')
    s.configure('icons.TButton', font=(FONT_ICONS, 12))

    _h = ttk.Frame(master)
    ttk.Button(_h, text=u"", command=add_files_command, width=5, style='icons-green.TButton').pack(side=left)
    ttk.Button(_h, text=u"",  style='icons-red.TButton',width=5, command=self.clear).pack(side=right)
    ttk.Button(_h, text=u"",  style='icons.TButton',width=5, command=self.delete).pack(side=right)
    ttk.Button(_h,  text=u"", width=5, style='icons.TButton', command=self.move_up).pack(side=right)
    ttk.Button(_h, text=u"", width=5, style='icons.TButton', command=self.move_down).pack(side=right)
    _h.pack(fill='x')
    self.tree.pack(fill='x')

    self.tree.bind('<ButtonRelease-1>', self.on_select_item)
    self.tree.bind('<<TreeviewSelect>>', self.on_select_item)

    self.tree.drop_target_register(DND_ALL)
    self.tree.dnd_bind("<<Drop>>", self.on_drop_files)
  

  def insert(self, *args, **kw):
    self.tree.insert(*args, **kw)

      
  def on_drop_file(self, event):
    entries = re.findall(r'(\w:\/.*?\.[\w:]+)',event.data) # find all path in str
  
    for entry in entries:
      if self.extension:
        if entry.lower().endswith(self.extension):
          self.tree.insert('', tk.END, values=(entry,))
          self.variable.set(entry)
      else:
        self.tree.insert('', tk.END, values=(entry,))
        self.variable.set(entry)


  def on_drop_files(self, event):
    entries = re.findall(r'(\w:\/.*?\.[\w:]+)',event.data) # find all path in str

    for entry in entries:
      if entry.lower().endswith(self.extension):
        self.tree.insert('', tk.END, values=(entry,))
        self.variable.set(entry)


  def on_select_item(self, *args):
    selections = self.tree.selection()
    if not selections: 
      return
    selected = selections[0]
    result = self.tree.item(selected)['values'][0]
    if result:
      self.variable.set(result)


  def delete(self):
    elements =  self.tree.selection()
    if not elements:
      return 
    selected = elements[0]
    self.tree.delete(selected)
    if self.values():
      self.variable.set(self.values()[0])
      if self.tree.identify_row(0):
        self.tree.selection_set(0)
      try:
        self.tree.focus(0)
      except:
        pass
    else:
      self.variable.set("")


  def clear(self):
    if not self.tree.get_children():
      return
    for item in self.tree.get_children():
      self.tree.delete(item)
    if self.variable:
      self.variable.set("")

  def move_up(self):
    leaves = self.tree.selection()
    for i in leaves:
        self.tree.move(i, self.tree.parent(i), self.tree.index(i)-1)


  def move_down(self):
    leaves = self.tree.selection()
    for i in reversed(leaves):
        self.tree.move(i, self.tree.parent(i), self.tree.index(i)+1)


  def values(self):
    return list(self.tree.set(item,0) for item in self.tree.get_children())


# Custom Canvas has rect lignes
class CanvasCrop(tk.Canvas):
  def __init__(self, master, model, *args, **kwargs):
    super().__init__(master, *args, **kwargs)

    self.model = model

    self.height = kwargs.get('height', 460)
    self.width = kwargs.get('width', 294)

    super().config(highlightthickness=0, bd=0, bg='white', width=self.width, height=self.height)

    self.model.top.trace('w', self.on_change_line_top)
    self.model.bottom.trace('w', self.on_change_line_bottom)
    self.model.right.trace('w', self.on_change_line_right)
    self.model.left.trace('w', self.on_change_line_left)

    self.create_text(self.width//2, self.height//2, text='', font=('Segoe Fluent Icons', 80),fill='gray90', tags=('preview'))
    self.create_rectangle(20, 20, self.width-29, self.height-20, dash=True, tags=('dash'), outline='gray70')

    self.line_top = self.create_line(-1, -1, self.width,-1, fill="red")
    self.line_bottom = self.create_line(0, self.height, self.width, self.height, fill="red")
    self.line_left = self.create_line(-1, -1, -1, self.height, fill="red")
    self.line_right = self.create_line(self.width, 0, self.width, self.height, fill="red")

  
  def on_change_line_top(self, *args):
    self.coords(self.line_top, 0, self.model.top.get(), self.width, self.model.top.get())


  def on_change_line_bottom(self, *args):
    bottom = self.height - int(self.model.bottom.get())
    self.coords(self.line_bottom, 0, bottom, self.width, bottom)


  def on_change_line_left(self, *args):
    left = int(self.model.left.get())
    self.coords(self.line_left, left, 0, left, self.height)


  def on_change_line_right(self, *args):
    right = self.width - int(self.model.right.get())
    self.coords(self.line_right, right, 0, right, self.height)


  def show_image(self, img):
    self.delete('all')
    org_w, org_h = img.width, img.height # memorize origine width
    ratio = org_w/org_h
    self.height = self.width / ratio

    img.thumbnail((self.width , self.height), Image.Resampling.LANCZOS)
    self.model.zoom_thumbnail = org_w / img.width
    self.config(height=self.height)

    # self.delete('dash', 'preview', 'picture')

    self.cover = ImageTk.PhotoImage(img)
    self.create_image(self.width/2, self.height/2, image=self.cover, tags=('picture'))
    # self.tag_lower(self.thumbnail)


  def show_picture(self, path):
    self.delete('all')
    img = Image.open(path)
    org_w, org_h = img.width, img.height # memorize origine width
    ratio = org_w/org_h
    self.height = self.width / ratio

    img.thumbnail((self.width , self.height), Image.Resampling.LANCZOS)
    self.model.zoom_thumbnail = org_w / img.width

    # self.delete('dash', 'preview', 'picture')

    self.cover = ImageTk.PhotoImage(img)
    self.create_image(self.width/2, self.height/2, image=self.cover, tags=('picture'))
    # self.tag_lower(self.thumbnail)
  
  
  def clean(self):
    self.delete('all')
    self.create_text(self.width//2, self.height//2, text='', font=('Segoe Fluent Icons', 80),fill='gray90', tags=('preview'))
    self.create_rectangle(20, 20, self.width-29, self.height-20, dash=True, tags=('dash'), outline='gray70')



# Custom Entry with placeholder and validaror number and , -
class Entry(ttk.Entry):
    def __init__(self, *args, **kwargs):
      self.placeholder = kwargs.pop("placeholder", "")
      self.textvariable = kwargs.get('textvariable')
      self.last_valid_value = ""

      super().__init__(*args, **kwargs)

      style = ttk.Style()
      style.configure('gray.TEntry', foreground='gray')

      self.add_placeholder()
      self.bind("<FocusIn>", self.remove_placeholder)
      self.bind("<FocusOut>", self.add_placeholder)

      
      self.vcmd = self.register(self.validate)
      self.ivcmd = self.register(self.invalidate)
      self['validate'] = 'key'
      self['validatecommand'] = self.vcmd, '%P',
      self['invalidcommand'] = self.ivcmd,


    def validate(self, inp):
      if inp == self.placeholder:
        return True
      for char in inp:
        if char not in '0123456789,-':
          return False
      self.last_valid_value = inp
      return True

    def invalidate(self):
      self.textvariable.set(self.last_valid_value)


    def remove_placeholder(self, *args, **kw):
      """Remove placeholder text, if present"""
      if super().get() == self.placeholder:
        self.config(style='TEntry')
        self.delete(0, "end")
      else:
        self.textvariable.set(self.textvariable.get())

    def add_placeholder(self,*args, **kw):
      """Add placeholder text if the widget is empty"""
      if self.placeholder and super().get() == "":
        self.config(style='gray.TEntry')
        self.insert(0, self.placeholder)

    def get(self):
      print("in get")
      if super.get() == self.placeholder:
        print('get is placeholder')
        return ""
      return super.get()





class WrappingLabel(tk.Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

def main():
    root = tk.Tk()
    root.geometry('200x200')
    win = WrappingLabel(root, justify='left', text="As in, you have a line of text in a Tkinter window, a Label. As the user drags the window narrower, the text remains unchanged until the window width means that the text gets cut off, at which point the text should wrap.")
    win.pack(expand=True, fill=tk.X)
    root.mainloop()

if __name__ == '__main__':
    main()