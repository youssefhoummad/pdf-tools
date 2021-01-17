import tkinter as tk
from tkinter import ttk
from threading import Thread

from PIL import Image, ImageTk

from src.constant import *
from src.itemSidebare import ItemSidebare
from src.cardFrame import CardFrame
from src.button import Button
from src.imageLabel import ImageLabel
from src.browseForm import BrowseForm
from src.linkLabel import LinkLabel
from src.entry import NumEntry
from src.gif import GifLabel

from src import func

# how to collect image by PyInstaller
# https://stackoverflow.com/a/63723292

#TODO: lastPages


class AppGui(tk.Tk):
  """
  docstring
  """
  def __init__ (self, **kw):
    # super class inits
    tk.Tk.__init__(self)

    self.title("Pdf tools")
    self.resizable(width=False, height=False)
    self.geometry("750x520")
    self.iconbitmap(r'img\\icon.ico')

    self.current_screen = None
    self.thread = None 
    self.zoom = 1
    # sidebar
    self.sidebar = tk.Frame(self, width=200, height=500, relief='flat', borderwidth=2)
    self.sidebar.pack(side=START_DIR, anchor=NW, fill='both')
    # main content area
    self.mainarea = tk.Frame(self, bg='white', width=550, height=500)
    self.mainarea.pack(expand=True, fill='both', side=END_DIR)

    self.file_path = tk.StringVar()
    self.file_path2 = tk.StringVar()

    self.file_path.trace('w', self.on_change_file)

    # vars for SPLIT Function
    self.start_page = tk.StringVar()
    self.end_page = tk.StringVar()


    # var for CROP Function
    self.top = tk.StringVar()
    self.bottom = tk.StringVar()
    self.right = tk.StringVar()
    self.left = tk.StringVar()

    self.top.trace('w', self.on_change_line_top)
    self.bottom.trace('w', self.on_change_line_bottom)
    self.right.trace('w', self.on_change_line_right)
    self.left.trace('w', self.on_change_line_left)

    self.init_sidebar()

    self.screens = [
      self.split_screen(),
      self.merge_screen(),
      self.crop_screen(),
      self.extract_screen(),
      self.images_screen(),
      self.about_screen(),
     ]

    self.show_current_sceen(0)


  def init_sidebar(self):
    menu = [
      {'title':SPLIT_TITLE,'icon':r'img\cut.png', 'index':0},
      {'title':MERGE_TITLE,'icon':r'img\merge.png', 'index':1 },
      {'title':CROP_TITLE,'icon':r'img\crop.png', 'index':2 },
      {'title':EXTRACT_TITLE,'icon':r'img\image.png', 'index':3 },
      # {'title':IMAGES_TITLE,'icon':r'img\images.png', 'index':4 },
      ]
    CardFrame(self.sidebar, 'PDF tools', MAIN_DESC).pack()
    for item in menu:
      ItemSidebare(self.sidebar, item['title'], icon=item['icon'], command=lambda x=item['index']:self.show_current_sceen(x)).pack(fill='x')
    
    ItemSidebare(self.sidebar, ABOUT_TITLE, icon=r'img\\info.png', command=lambda x=5:self.show_current_sceen(x)).pack(side='bottom', fill='x')
  

  ## init sceens

  def split_screen(self):

    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    header = ImageLabel(_f, r'img\\split_header.png',width=550, height=180)
    header.pack()

    CardFrame(_f, SPLIT_TITLE, SPLIT_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)

    _n = tk.Frame(_f, bg=_f['bg'])
    NumEntry(_n,  placeholder='start page', textvariable=self.start_page, _min=1).pack(side=START_DIR, padx=END_PADDING_10, fill='x', expand=True)
    NumEntry(_n, placeholder='last page', textvariable=self.end_page, _min=1).pack(side=START_DIR, fill='x', expand=True)
    _n.pack(padx=START_PADDING_24, fill='x', expand=True, pady=(10,0))

    Button(_f, text="Split file", command=self.split_function).pack(side=START_DIR,padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f


  def merge_screen(self):
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    header = ImageLabel(_f, r'img\\merge_header.png',width=550, height=180)
    header.pack()

    CardFrame(_f, MERGE_TITLE, MERGE_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)
    BrowseForm(_f, self.file_path2).pack(padx=START_PADDING_24, pady=(10,0), anchor=NW, fill='x', expand=True)
    
    Button(_f, text="Merge files", command=self.merge_function).pack(side=START_DIR, padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f
    
  
  def crop_screen(self):
    
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    CardFrame(_f, CROP_TITLE, CROP_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)


    _n = tk.Frame(_f, bg=_f['bg'])
    _n.grid_columnconfigure((0, 1, 2), weight=1)
    _n.pack(pady=20)

    NumEntry(_n, textvariable=self.top, placeholder='top').grid(row=0, column=1)
    NumEntry(_n, textvariable=self.right, placeholder='right').grid(row=1, column=0)
    self.canvas = tk.Canvas(_n, width=CANVAS_W, height=CANVAS_H)
    self.canvas.grid(row=1, column=1, padx=5, pady=5)
    NumEntry(_n, textvariable=self.left, placeholder='left').grid(row=1, column=2)
    NumEntry(_n, textvariable=self.bottom, placeholder='bottom').grid(row=2, column=1)

    self.line_top = self.canvas.create_line(0, 0, CANVAS_W, 0, fill="red")
    self.line_bottom = self.canvas.create_line(0, CANVAS_H, CANVAS_W, CANVAS_H, fill="red")
    self.line_left = self.canvas.create_line(0, 0, 0, CANVAS_H, fill="red")
    self.line_right = self.canvas.create_line(CANVAS_W, 0, CANVAS_W, CANVAS_H, fill="red")
    
    Button(_f, text="Crop files", command=self.crop_function).pack(side=START_DIR,padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f


  def extract_screen(self):
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    header = ImageLabel(_f, r'img\\extract_header.png',width=550, height=180)
    header.pack()

    CardFrame(_f, EXTRACT_TITLE, EXTRACT_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)
    Button(_f, text="Extract images", command=self.extract_function).pack(side=START_DIR,padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f


  def images_screen(self):
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    header = ImageLabel(_f, r'img\\images_header.png',width=550, height=180)
    header.pack()

    CardFrame(_f, IMAGES_TITLE, IMAGES_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)
    Button(_f, text="Convert file", command=self.to_images_function).pack(side=START_DIR,padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f


  def about_screen(self):
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    CardFrame(_f, "About", ABOUT_DESC).pack(fill='both', pady=(0, 0))
    LinkLabel(_f, text="github/youssefhoummad", link="https://github.com/youssefhoummad").pack(fill='x', padx=START_PADDING_24 ,pady=(0,10))
    tk.Label(_f, bg="white", text="Or you can contact me by email:",  fg='gray', anchor=NW, font=('Calibri',12,"normal")).pack(fill='both', padx=START_PADDING_24)
    LinkLabel(_f, text="youssef.hoummad@outlook.com", link="mailto:youssef.hoummad@outlook.com").pack(fill='x', padx=START_PADDING_24)
    tk.Label(_f, bg="white", text="icons from: icons8.com",  fg='gray', anchor=NW, font=('Calibri',12,"normal")).pack(fill='both', padx=START_PADDING_24, pady=34)

    return _f


  def show_current_sceen(self, index):
    if index == None: return
    for screen in self.screens:
      try:
        screen.pack_forget()
      except:
        pass
    self.current_screen = self.screens[index]
    self.current_screen.pack(fill='both')



  # # some function to pass function in thread



  def split_function(self):

    file = self.file_path.get()
    pages_range = [self.start_page, self.end_page]
    pages_range = [item.get() for item in pages_range]

    # if entry has no value or string so is 1
    pages_range = [int(item) if item.isdigit() else 1 for item in pages_range]

    @self.sanirize
    def function(*args):
      func.split(*args)

    self.thread = Thread(target=function, args=(file, *pages_range))
    self.thread.start()

  
  def merge_function(self):
    
    file1 = self.file_path.get()
    file2 = self.file_path2.get()

    if not file2: return

    @self.sanirize
    def function(*args):
      func.merge(*args)

    self.thread = Thread(target=function, args=(file1, file2,))
    self.thread.start()

  
  def crop_function(self):

    file = self.file_path.get()
    
    margins = [self.top, self.right, self.bottom, self.left ]
    margins = [item.get() for item in margins]
    # if entry has no value or string so is 0
    margins = [int(item) if item.isdigit() else 0 for item in margins]

    # multi marging * zoom
    margins = [marg*self.zoom for marg in margins]
    
    # no margin croped
    if sum(margins) < 1: return

    @self.sanirize
    def function(*args):
      func.crop(*args)

    self.thread = Thread(target=function, args=(file, *margins))
    self.thread.start()

  
  def extract_function(self):
    
    file = self.file_path.get()

    @self.sanirize
    def function(*args):
      func.extract(*args)

    self.thread = Thread(target=function, args=(file,))
    self.thread.start()

  
  def to_images_function(self):
    
    file = self.file_path.get()

    @self.sanirize
    def function(*args):
      func.to_images(*args)

    self.thread = Thread(target=function, args=(file,))
    self.thread.start()


  def sanirize(self, callback):

    def function_wrapper(*args, **kwargs):

      if not args[0]: return # if no pdf selected

      self.disable_btn_show_loading()

      callback(*args, **kwargs)

      self.thread = None
      
      self.unable_btn_hide_loading()

      self.bell()

    return function_wrapper


  def show_thumbnail(self):
    global CANVAS_H, CANVAS_W

    img = func.first_page_to_image(self.file_path.get())
    org_w,org_h = img.width, img.height
    img.thumbnail((CANVAS_W , CANVAS_H), Image.ANTIALIAS)
    self.cover = ImageTk.PhotoImage(img)

    CANVAS_H = img.height
    CANVAS_W = img.width

    self.zoom = org_w / img.width

    self.canvas.config(width=img.width, height=img.height)

    self.thumbnail = self.canvas.create_image(img.width/2, img.height/2, image=self.cover)
    self.canvas.tag_lower(self.thumbnail)
    

  def on_change_file(self, var, indx, mode):

      if not self.file_path.get():
        # last screen about has'nt button 
        for screen in self.screens[:-1]:
          screen.pack_slaves()[-2].on_disable()
        return

      # self.show_thumbnail()
      t = Thread(target=self.show_thumbnail)
      t.start()

      for screen in self.screens[:-1]:
        screen.pack_slaves()[-2].on_unable()

      # TODO:get num pages of pdf


  def on_change_line_top(self, *args):
    if self.top.get().isdigit():
      self.canvas.coords(self.line_top, 0, self.top.get(), CANVAS_W, self.top.get())


  def on_change_line_bottom(self, var, indx, mode):
    if self.bottom.get().isdigit():
      bottom = CANVAS_H - int(self.bottom.get())
      self.canvas.coords(self.line_bottom, 0, bottom, CANVAS_W, bottom)


  def on_change_line_left(self, var, indx, mode):
    if self.left.get().isdigit():
      left = CANVAS_W-int(self.left.get())
      self.canvas.coords(self.line_left, left, 0, left, CANVAS_H)


  def on_change_line_right(self, var, indx, mode):
    if self.right.get().isdigit():
      right = int(self.right.get())
      self.canvas.coords(self.line_right, right, 0, right, CANVAS_H)

  
  def disable_btn_show_loading(self):
    # disbale button
      self.current_screen.pack_slaves()[-2].on_disable()
      # show loading spinner
      self.current_screen.pack_slaves()[-1].load()


  def unable_btn_hide_loading(self):
    # disbale button
      self.current_screen.pack_slaves()[-2].on_unable()
      # show loading spinner
      self.current_screen.pack_slaves()[-1].unload()

  

if __name__ == "__main__":
  
  app = AppGui()
  app.mainloop()