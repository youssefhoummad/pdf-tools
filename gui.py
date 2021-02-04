import os
import tkinter as tk
from tkinter import messagebox 
from tkinter import ttk
from threading import Thread
import subprocess

from PIL import Image, ImageTk
# import fitz

from src.constant import *
from src.itemSidebare import ItemSidebare
from src.cardFrame import CardFrame
from src.button import Button, ButtonSmall
from src.toggleSwitch import Switch
from src.imageLabel import ImageLabel
from src.browseForm import BrowseForm, BrowseForm2
from src.linkLabel import LinkLabel
from src.entry import EntryWithPlusMinus
from src.gif import GifLabel
from src import func


# how to collect image by PyInstaller
# https://stackoverflow.com/a/63723292

#TODO: lastPages


class AppGui(tk.Frame):
  """
  docstring
  """
  def __init__ (self, master, queue, *commands):
    # super class inits
    super().__init__(master)

    self.master = master

    self.queue = queue

    self.split, self.merge, self.crop, self.extract, self.to_pdf, self.init_doc = commands

    self.doc = None

    self.file_path = tk.StringVar()
    self.file_path2 = tk.StringVar()
    self.files_path = tk.StringVar()

    self.file_path.trace('w', self.on_change_file)
    self.files_path.trace('w', self.on_change_files)


    # vars for SPLIT Function
    self.start_page = tk.StringVar()
    self.end_page = tk.StringVar()


    # var for CROP Function
    self.top = tk.StringVar()
    self.bottom = tk.StringVar()
    self.right = tk.StringVar()
    self.left = tk.StringVar()
    self.zoom = 1 

    self.top.trace('w', self.on_change_line_top)
    self.bottom.trace('w', self.on_change_line_bottom)
    self.right.trace('w', self.on_change_line_right)
    self.left.trace('w', self.on_change_line_left)

    self.init_gui()


  def processIncoming(self):
    """ Handle all messages currently in the queue, if any. """
    while self.queue.qsize():
      try:
        msg = self.queue.get_nowait()
        # Check contents of message and do whatever is needed. As a
        # simple example, let's print it (in real life, you would
        # suitably update the GUI's display in a richer fashion).
        print(msg)
      except queue.Empty:
        # just on general principles, although we don't expect this
        # branch to be taken in this case, ignore this exception!
        pass


  def init_gui(self):

    self.sidebar = tk.Frame(self, width=200, height=500, bd=0)
    self.sidebar.pack(side=START_DIR, fill='both')
    self.sidebar.pack_propagate(0) # fix width
    # main content area
    self.mainarea = tk.Frame(self, bg='white', width=550, height=500, bd=0)
    self.mainarea.pack(expand=True, fill='both', side=START_DIR)

    self.init_sidebar()

    self.screens = [
      self.split_screen(),
      self.merge_screen(),
      self.crop_screen(),
      self.extract_screen(),
      self.to_pdf_screen(),
      self.about_screen(),
     ]
    
    self.current_screen = None

    self.show_current_sceen(0)


  def init_sidebar(self):
    self.btns_sidebar = []

    menu = [
      {'title':SPLIT_TITLE,'icon':r'img\cut.png', 'index':0},
      {'title':MERGE_TITLE,'icon':r'img\merge.png', 'index':1 },
      {'title':CROP_TITLE,'icon':r'img\crop.png', 'index':2 },
      {'title':EXTRACT_TITLE,'icon':r'img\image.png', 'index':3 },
      {'title':IMAGES_TITLE,'icon':r'img\images.png', 'index':4 },
      {'title':ABOUT_TITLE, 'icon':r'img\\info.png', 'index':5}
      ]
    # show top <PDF-Tools>
    CardFrame(self.sidebar, 'PDF tools', MAIN_DESC).pack()

    # add buttons sidebar to list <btns_sidebar>
    for item in menu:
      self.btns_sidebar.append(
        ItemSidebare(self.sidebar, item['title'], icon=item['icon'], command=lambda x=item['index']:self.show_current_sceen(x)))
    
    # show bouttons sidebar
    for btn in self.btns_sidebar[:-1]: btn.pack(fill='x')
    # show last boutton sidebar at bottom
    self.btns_sidebar[-1].pack(side='bottom', fill='x')
  

  ## init sceens

  def split_screen(self):

    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    header = ImageLabel(_f, r'img\\split_header.png',width=550, height=180)
    header.pack()

    CardFrame(_f, SPLIT_TITLE, SPLIT_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)

    _n = tk.Frame(_f, bg=_f['bg'])
    tk.Label(_n, bg=_f['bg'], text=FROM_TXT, font=FONT_SM).pack(side=START_DIR, padx=END_PADDING_10)
    EntryWithPlusMinus(_n, textvariable=self.start_page, _min=1).pack(side=START_DIR, padx=END_PADDING_10, fill='x')
    tk.Label(_n, bg=_f['bg'], text=TO_TXT, font=FONT_SM).pack(side=START_DIR, padx=START_PADDING_24)
    self.entry_end = EntryWithPlusMinus(_n, textvariable=self.end_page, _min=1)
    self.entry_end.pack(side=START_DIR, fill='x')
    _n.pack(padx=START_PADDING_24, fill='x', expand=True, pady=(20,0))

    Button(_f, text=SPLIT_BTN, command=self.split).pack(side=START_DIR,padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f


  def merge_screen(self):
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    header = ImageLabel(_f, r'img\\merge_header.png',width=550, height=180)
    header.pack()

    CardFrame(_f, MERGE_TITLE, MERGE_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)
    BrowseForm(_f, self.file_path2).pack(padx=START_PADDING_24, pady=(10,0), anchor=NW, fill='x', expand=True)
    
    Button(_f, text=MERGE_BTN, command=self.merge).pack(side=START_DIR, padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f
    
  
  def crop_screen(self):
    
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    CardFrame(_f, CROP_TITLE, CROP_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)

    _n = tk.Frame(_f, bg=_f['bg'], bd=0)
    _n.grid_columnconfigure((0, 1, 2), weight=1)
    _n.pack(pady=10, fill='x')

    self.canvas = tk.Canvas(_n, width=CANVAS_W, height=CANVAS_H, relief='flat',highlightthickness=0, bd=0)
    self._textpreview = self.canvas.create_text(CANVAS_W//2, CANVAS_H//2, text=PREVIEW_TEXT, fill='gray')

    self.line_top = self.canvas.create_line(0, 0, CANVAS_W, 0, fill="red")
    self.line_bottom = self.canvas.create_line(0, CANVAS_H, CANVAS_W, CANVAS_H, fill="red")
    self.line_left = self.canvas.create_line(0, 0, 0, CANVAS_H, fill="red")
    self.line_right = self.canvas.create_line(CANVAS_W, 0, CANVAS_W, CANVAS_H, fill="red")
    

    EntryWithPlusMinus(_n, textvariable=self.top, placeholder=TOP_TXT, _max=CANVAS_H).grid(row=0, column=1)
    EntryWithPlusMinus(_n, textvariable=self.left, placeholder=LEFT_TXT, _max=CANVAS_W).grid(row=1, column=0, sticky='e')
    
    self.canvas.grid(row=1, column=1, pady=5)

    EntryWithPlusMinus(_n, textvariable=self.right, placeholder=RIGHT_TXT, _max=CANVAS_W).grid(row=1, column=2, sticky='w')
    self.next = ButtonSmall(_n, text="◄", command=self.next_thumbail)
    self.next.grid(row=2, column=0)
    EntryWithPlusMinus(_n, textvariable=self.bottom, placeholder=BOTTOM_TXT, _max=CANVAS_H).grid(row=2, column=1)
    self.previous = ButtonSmall(_n, text="►", command=self.previous_thumbail)
    self.previous.grid(row=2, column=2)

    Button(_f, text=CROP_BTN, command=self.crop).pack(side=START_DIR,padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f


  def extract_screen(self):

    self.to_single_pages = tk.StringVar()


    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    header = ImageLabel(_f, r'img\\extract_header.png',width=550, height=180)
    header.pack()

    CardFrame(_f, EXTRACT_TITLE, EXTRACT_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm(_f, self.file_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)

    _c = tk.Frame(_f, bg=_f['bg'])
    Switch(_c, text=EACH_PAGE_TEXT, variable=self.to_single_pages, bg=_f['bg']).pack(side=START_DIR, anchor=NW, fill='x', expand=True)
    _c.pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True, pady=20)
    
    Button(_f, text=EXTRACT_BTN, command=self.extract).pack(side=START_DIR,padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f


  def to_pdf_screen(self):
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    header = ImageLabel(_f, r'img\\to_pdf_header.tif',width=550, height=180)
    header.pack()

    CardFrame(_f, IMAGES_TITLE, IMAGES_DESC).pack(fill='both', pady=(0, 10))

    BrowseForm2(_f, self.files_path).pack(padx=START_PADDING_24, anchor=NW, fill='x', expand=True)
    Button(_f, text=CONVERT_BTN, command=self.to_pdf).pack(side=START_DIR,padx=START_PADDING_24, pady=(30,0), anchor=NW)
    GifLabel(_f, r'img\\loading_blue.gif').pack(side=START_DIR, anchor='sw', pady=(0,2))
    return _f


  def about_screen(self):
    _f = tk.Frame(self.mainarea, bg=self.mainarea['bg'])

    CardFrame(_f, ABOUT_TITLE, ABOUT_DESC).pack(fill='both', pady=(0, 0))
    LinkLabel(_f, text="github/youssefhoummad", link="https://github.com/youssefhoummad").pack(fill='x', padx=START_PADDING_24 ,pady=(0,10))
    tk.Label(_f, bg="white", text=EMAIL_TEXT,  fg='gray', anchor=NW, font=FONT_SM).pack(fill='both', padx=START_PADDING_24)
    LinkLabel(_f, text="youssef.hoummad@outlook.com", link="mailto:youssef.hoummad@outlook.com").pack(fill='x', padx=START_PADDING_24)
    # tk.Label(_f, bg="white", text="icons from: icons8.com",  fg='gray', anchor=NW, font=('Calibri',12,"normal")).pack(fill='both', padx=START_PADDING_24, pady=34)

    _g = tk.Frame(_f, bg=_f['bg'])
    tk.Label(_g, bg="white", text=CHOOSE_LANGUAGE,  fg='gray', font=FONT_SM).pack(side=START_DIR)
    tk.Radiobutton(_g, bg='white' , bd=1, text="العربية",width=20, indicatoron=0, command=self.on_change_lang_ar, value='rtl').pack(side=START_DIR, anchor=NW, padx=START_PADDING_24)
    tk.Radiobutton(_g, bg='white' , bd=1, text="English",width=20, indicatoron=0, command=self.on_change_lang_en, value='ltr').pack(side=START_DIR, anchor=NW, padx=START_PADDING_24)
    _g.pack(fill='x', padx=START_PADDING_24, pady=(60, 0))
  

    return _f


  def show_current_sceen(self, index):

    # hide others screens
    for screen in self.screens: screen.pack_forget()
    # show this screen
    self.current_screen = self.screens[index]
    self.current_screen.pack(fill='both')

    # hide accent color from others buttons sidebar
    for btn in self.btns_sidebar: btn.on_disactive()
    # show accent color to Clicked button sidebar
    self.btns_sidebar[index].on_active()


  def show_thumbnail(self, page=1):

    self.current_page  = 0

    global CANVAS_H, CANVAS_W

    img = func.page_to_image(self.doc)
    org_w,org_h = img.width, img.height

    img.thumbnail((CANVAS_W , CANVAS_H), Image.ANTIALIAS)

    CANVAS_H = img.height
    CANVAS_W = img.width

    self.zoom = org_w / img.width


    self.canvas.config(width=img.width, height=img.height)
    self.show_image_on_canvas(img)

    self.next.on_unable()

  
  def next_thumbail(self):
    self.current_page += 1

    if self.current_page == self.doc.pageCount:
      self.next.on_disable()
      return
    

    img = func.page_to_image(self.doc, self.current_page)
    self.show_image_on_canvas(img)
    
    # img.thumbnail((CANVAS_W , CANVAS_H), Image.ANTIALIAS)
    # self.cover = ImageTk.PhotoImage(img)
    # self.thumbnail = self.canvas.create_image(img.width/2, img.height/2, image=self.cover)
    # self.canvas.tag_lower(self.thumbnail)

    self.previous.on_unable()

  
  def previous_thumbail(self):
    self.current_page -= 1
    
    if self.current_page == 0:
      self.previous.on_disable()
      
    self.next.on_unable()
    
    img = func.page_to_image(self.doc, self.current_page)
    self.show_image_on_canvas(img)

    # img.thumbnail((CANVAS_W , CANVAS_H), Image.ANTIALIAS)
    # self.cover = ImageTk.PhotoImage(img)
    # self.thumbnail = self.canvas.create_image(img.width/2, img.height/2, image=self.cover)
    # self.canvas.tag_lower(self.thumbnail)
  

  def show_image_on_canvas(self, img):
    img.thumbnail((CANVAS_W , CANVAS_H), Image.ANTIALIAS)
    self.cover = ImageTk.PhotoImage(img)
    self.thumbnail = self.canvas.create_image(img.width/2, img.height/2, image=self.cover)
    self.canvas.tag_lower(self.thumbnail)
    self.canvas.tag_lower(self._textpreview)


  def on_change_lang_ar(self):
    settings.setsave('DIR', 'rtl')
    messagebox.showinfo(title=None, message='need reboot app') 
    self.after(500, self.master.destroy)
    # self.destroy()
    

  def on_change_lang_en(self):
    settings.setsave('DIR', 'ltr')
    messagebox.showinfo(title=None, message='need reboot app')
    self.after(500, self.master.destroy)


  def on_change_file(self, var, indx, mode):

      if not self.file_path.get():
        # last screen about has'nt button 
        for screen in self.screens[:-2]:
          screen.pack_slaves()[-2].on_disable()
        return
      
      self.doc = self.init_doc()


      self.show_thumbnail()

      self.entry_end._max = self.doc.pageCount


      for screen in self.screens[:-2]:
        screen.pack_slaves()[-2].on_unable()

      # TODO:get num pages of pdf
      # self.end_page.set(self.doc.pageCount)


  def on_change_files(self, var, indx, mode):

      if not self.files_path.get():
        self.current_screen.pack_slaves()[-2].on_disable()
        return

      self.current_screen.pack_slaves()[-2].on_unable()



  def on_change_line_top(self, *args):
    if self.top.get().isdigit():
      self.canvas.coords(self.line_top, 0, self.top.get(), CANVAS_W, self.top.get())


  def on_change_line_bottom(self, var, indx, mode):
    if self.bottom.get().isdigit():
      bottom = CANVAS_H - int(self.bottom.get())
      self.canvas.coords(self.line_bottom, 0, bottom, CANVAS_W, bottom)


  def on_change_line_left(self, var, indx, mode):
    if self.left.get().isdigit():
      left = int(self.left.get())
      self.canvas.coords(self.line_left, left, 0, left, CANVAS_H)


  def on_change_line_right(self, var, indx, mode):
    if self.right.get().isdigit():
      right = CANVAS_W - int(self.right.get())
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
