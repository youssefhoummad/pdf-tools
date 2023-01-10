import tkinter as tk
from tkinter import ttk
from winreg import *

def get_accent_color():  

  """
  Return the Windows 10 accent color used by the user in a HEX format
  """
  registry = ConnectRegistry(None, HKEY_CURRENT_USER)
  key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent')
  key_value = QueryValueEx(key,'AccentColorMenu')
  accent_int = key_value[0]
  accent = accent_int-4278190080
  accent = str(hex(accent)).split('x')[1]
  accent = accent[4:6]+accent[2:4]+accent[0:2]
  return '#'+accent

default_colors = {"accent": get_accent_color(), "bg":'#EFF4F8',"hover":'#E8EBF0',"press":'#D6D9DE'}



class Sidebook(tk.Frame):
  _id = 0
  def __init__(self, master=None, width_sidebar=200, padding=[], colors=default_colors, **kw):
    # width = kw.pop('width', 200)
    self.justify = kw.pop('justify', 'left')
    width = kw.pop('width', 200)
    super().__init__(master, **kw)

    left, right = 'left', 'right'
    if self.justify == 'right':
      left, right = right, left

    self.padding = padding

    self.sidebar = tk.Frame(self, bg='#EFF4F8', width=width_sidebar)
    self.mainerea = tk.Frame(self, bg=master['bg'])
    if width: self.mainerea.config(width=width-width_sidebar)
    

    self.header = ttk.Frame(self.sidebar)
    self.header.pack(fill='x')

    self.sidebar.pack(side=left, fill='y')
    self.sidebar.pack_propagate(False)
    self.mainerea.pack(side=left, fill='both')
    self.mainerea.pack_propagate(False)


    self.tabs = {}

    self.colors =  self.set_colors(colors)

    

  
  def set_colors(self, colors):
    _colors = default_colors
    if colors:
      for key, value in colors.items():
        if value!='default':
          _colors[key] = value
    return _colors


  def add(self, widget, text, icon=None, at_bottom=False): 
    sb = SideTab(self.sidebar, text, colors=self.colors,
              command=lambda:self.show(widget),
              icon=icon, 
              justify=self.justify )
              # TODO customize padding from class kwargs 

    if not at_bottom:
      sb.pack(fill='x', padx=8, pady=3, anchor='nw')
    else:
      sb.pack(side='bottom', fill='x', padx=8, pady=3, anchor='sw')
    
    self.tabs[self._id] = sb
    self._id += 1


  def add_header(self, widget): 
    widget.pack(in_=self.header, fill='x', padx=8, pady=3, anchor='sw')


  def show(self, widget):
    # clean mainerea
    [w.forget() for w in self.mainerea.pack_slaves()]
    # pack new frame
    widget.pack(in_=self.mainerea, fill='both', anchor='n', expand=True)


  def select(self, _id:int)->None:
    tab = self.tabs.get(_id)
    if tab:
      tab.on_active()
      tab.on_release()
  

  def current(self)-> int:
    for _id, tab in self.tabs.items():
      if tab.active:
        return _id


  def text(self, _id:int):
    tab = self.tabs.get(_id)
    if tab:
      return tab.text['text']


class SideTab(tk.Frame):
  instances=set()

  def __init__(self, master, text, icon=None, colors=[], command=None, **kw):
    justify = kw.pop('justify', 'left')
    super().__init__(master, **kw)

    left, right = 'left', 'right'
    if justify == 'right':
      left, right = right, left


    self.config(bg=master['bg'])

    self.command= command
    self.colors = colors

    self.active = False

    self.border = tk.Frame(self, bg=self['bg'], width=4, height=20) # height=18
    self.text = tk.Label(self, text=text, bg=self['bg'])

    if icon:
      if isinstance(icon, str):
        _img = tk.PhotoImage(file=icon)
        self.icon = tk.Label(self, image=_img, bg=self['bg'])
        self.icon.image = _img
      else:
        self.icon = tk.Label(self, image=icon, bg=self['bg'])
    else:
      self.icon = tk.Label(self, text="", bg=self['bg'])

    self.border.pack(side=left, padx=8)
    self.icon.pack(side=left,)
    self.text.pack(side=left, fill='x', padx=8)

    for w in [self, self.border, self.icon, self.text]:
      w.bind("<ButtonPress-1>", self.on_press)
      w.bind("<ButtonRelease-1>", self.on_release)
      w.bind("<Enter>", self.on_hover)
      w.bind("<Leave>", self.on_leave)
    
    self.config(height=36)
    self.pack_propagate(False)
    type(self).instances.add(self)
  

  def on_hover(self, *args):
    if self.active:
      self.on_press()
    else:
      self.config(bg=self.colors['hover'])
      self.text.config(bg=self.colors['hover'])
      self.icon.config(bg=self.colors['hover'])
    self.text.config(fg='black')
    
  
  def on_press(self, *args):
    self.config(bg=self.colors['press'])
    self.text.config(bg=self.colors['press'], fg='gray')
    self.icon.config(bg=self.colors['press'])
    self.border.config(bg=self.colors['accent'])
    

    for btn in type(self).instances:
      try:
        btn.on_disactive()
      except:
        pass
    self.on_active()


  def on_leave(self, *args):
    if self.active:
      self.on_press()
    else:
      self.icon.config(bg=self.colors['bg'])
      self.border.config(bg=self.colors['bg'])
      self.config(bg=self.colors['bg'])
      self.text.config(bg=self.colors['bg'])
    self.text.config(fg='black')
      

  def on_release(self, *args):
    self.on_hover()
    self.command()


  def on_active(self):
    self.active = True
    self.border.config(bg=self.colors['accent'])
    self.config(bg=self.colors['press'])
    self.text.config(bg=self.colors['press'])
    self.icon.config(bg=self.colors['press'])

  def on_disactive(self):
    self.active = False
    self.border.config(bg=self.colors['bg'])
    self.config(bg=self.colors['bg'])
    self.text.config(bg=self.colors['bg'])
    self.icon.config(bg=self.colors['bg'])





if __name__ == '__main__':
  root = tk.Tk()
  root.geometry('600x400')

  sideBook = Sidebook(root, colors={"accent":"red"}, justify='right')

  button = tk.Button(text="clcik")
  button2 = tk.Button(text="second screen")
  button3 = tk.Button(text="third screen")

  sideBook.add(button, text="split file", icon=r'images\split.png')
  sideBook.add(button2, text="merge files", icon=r'images\merge.png')
  sideBook.add(button2, text="crop margins", icon=r'images\crop.png')
  sideBook.add(button2, text="rotate pages", icon=r'images\rotation.png')
  sideBook.add(button2, text="convert to images", icon=r'images\picture.png')
  sideBook.add(button3, text="settings", icon=r'images\settings.png', at_bottom=True)

  
  print(sideBook.text(1))
  sideBook.pack()
  root.mainloop()