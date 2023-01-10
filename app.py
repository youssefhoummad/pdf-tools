# -*- coding: UTF-8 -*-

from configparser import ConfigParser
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from functools import partial

from tkinterdnd2 import *
from winotify import Notification, audio

from src.mvc_thread import View, Controler, ThreadWithResult
from src.widgets import TreeFiles, CanvasCrop, Entry, WrappingLabel
from src.sidebook import Sidebook
import src.functions as functions
from src.utils import *



config = ConfigParser()

if not os.path.exists('config.ini'):
  import locale
  locale_lang = locale.getdefaultlocale()[0][0:2]

  lang = 'en'
  if locale_lang in ('ar', 'fr'):
    lang = locale_lang

  config['main'] = {'lang': lang, 'open_doc': False}
  config.write(open('config.ini', 'w'))

config.read('config.ini')

# setting
lang = config.get('main', 'lang')
open_doc = config.getboolean('main', 'open_doc')

# constants
is_win11 = True if (sys.getwindowsversion().build > 20000) else False
FONT_ICONS = 'Segoe Fluent Icons'  if  is_win11 else 'Segoe MDL2 Assets'

left, right = 'left', 'right'
w, e = 'w', 'e'


if lang == 'ar':
  left, right = right, left
  w, e = e, w

# language translator
_ = partial(gettext, lang=lang)


# store all data here

class Model:
  def __init__(self, parent) -> None:
    self.parent = parent

    self._filepath = tk.StringVar()

    self.selected_image = tk.StringVar()
    

    self.pages = 0

    self.rotate = tk.StringVar(value='90')

    # selected pages
    self.selected_for_split = tk.StringVar(value="")
    self.selected_for_images = tk.StringVar(value="")
    self.selected_for_rotate = tk.StringVar(value="")
    self.selected_for_crop = tk.StringVar(value="")


    # images
    self.zoom_images = tk.IntVar(value=2)
    self.extract_images = tk.BooleanVar(value=False)
    self.dimensions = tk.StringVar()

    # margins     
    self.top = tk.IntVar(value=0)
    self.bottom = tk.IntVar(value=0)
    self.left = tk.IntVar(value=0)
    self.right = tk.IntVar(value=0)
    self.zoom_thumbnail = 1

  @property
  def filepath(self):
    return self._filepath.get()
  

  @filepath.setter
  def filepath(self, value):
    self._filepath.set(value)
    if value:
      self.pages = functions.pages(value)
    else:
      self.pages = 0


# the real app inherit from <Controller> abstract

class App(Controler):

  def __init__(self, parent, View, Model):
    super().__init__(parent, View, Model)

  
  def thread(self, target, args=(), kwargs={}):
    """ use this methode for make progress bar update"""
    # gui staf before starting thread
    self.view.before_operation()

    thread = ThreadWithResult(target=target, args=args, kwargs=kwargs)
    thread.log_thread_status = False
    thread.start()
    thread.join()

    # checks whether thread is alive #
    while thread.is_alive():
        self.parent.update()
        pass
    
    # gui staf after finish thread
    self.view.after_operation(thread.result)
    

  @property
  def filespath(self):
    return self.view.tree_pdfs.values()

  @property
  def extract_images(self):
    return self.model.extract_images.get()

  @property
  def zoom_images(self):
    return self.model.zoom_images.get()
  
  @property
  def margins(self):
    margins = [self.model.top.get(), self.model.bottom.get(), self.model.left.get(), self.model.right.get()]
    return [margin*self.model.zoom_thumbnail for margin in margins]
  

  def show_preview(self, page=1):
    img = functions.page_thumbnails(self.model.filepath, page=page-1)
    self.view.canvas.show_image(img)


  def on_change_entry(self, *args, **kwargs):
    # TODO fix some tabs not exist or variable is None
    if not self.model.filepath:
      return
  
    tab_dict = {
      _('split'):self.model.selected_for_split,
      _('crop margins'):self.model.selected_for_crop,
      _('to images'):self.model.selected_for_images,
      _('rotate pages'):self.model.selected_for_rotate,
    }

    variable = None
    tab = self.view.notebook.text(self.view.notebook.current())
    for tab_text in tab_dict:
      if tab_text in tab:
        variable = tab_dict[tab_text]  

    last_page = last_in_list(variable.get())

    if not last_page: return
    if last_page > self.model.pages: return

    self.show_preview(last_page)


  def on_change_filepath(self, *args):
    if self.model.filepath:
      # pages = functions.pages(self.model.filepath)
      self.show_preview()
    else:
      self.view.canvas.clean()
  

  def on_select_image(self, *args):
    if self.model.selected_image.get():
      self.view.canvas.show_picture(self.model.selected_image.get())
    else:
      self.view.canvas.clean()


  def split(self):
    if not self.model.filepath or not self.model.selected_for_split.get():
      self.view.need_file_flash()
      return
    if ":" in self.model.selected_for_split.get():
      return
    # this line is assert the textvariable not a placeholder 
    selected_pages = str_to_list(self.model.selected_for_split.get())
    if not selected_pages:
      return
    
    self.thread(functions.split, args=(self.model.filepath, selected_pages))


  def merge(self):
    if len(self.filespath)<2:
      self.view.need_file_flash()
      return
    self.thread(functions.merge, args=(self.filespath,))


  def crop(self):
    if not self.model.filepath or not any(self.margins):
      self.view.need_file_flash()
      return
    selected_pages = str_to_list(self.model.selected_for_crop.get())
    self.thread(functions.crop, args=(self.model.filepath, *self.margins, selected_pages))


  def convert(self):
    if not self.model.filepath:
      self.view.need_file_flash()
      return
    selected_pages = str_to_list(self.model.selected_for_images.get())
    if self.extract_images:
      self.thread(functions.extract_images, args=(self.model.filepath, selected_pages))
    else:
      self.thread(functions.to_images, args=(self.model.filepath, selected_pages, self.zoom_images))


  def to_pdf(self):
    images = self.view.tree_images.values()
    if not images: return

    is_a4 = self.model.dimensions.get() == 'A4'

    self.thread(functions.to_pdf, args=(images, is_a4))


  def rotate(self):
    if not self.model.filepath:
      self.view.need_file_flash()
      return
    degree = self.model.rotate.get()
    if not degree: return
    selected_pages = str_to_list(self.model.selected_for_rotate.get())
    self.thread(functions.rotate, args=(self.model.filepath, int(degree), selected_pages))


# tkinter Gui inherit from <View> abstract

class Page(tk.Frame):
  def __init__(self, master=None, title:str="", image=None, discription="", bg="#EFF4F8"):
    super().__init__(master, bg=bg, width=200)
    # TITLE lABEL
    tk.Label(self, text=title, font=('Segoe UI',16, 'bold'), justify=left, bg=self['bg']).pack(anchor=w, pady=10)
    # IMAGE
    _f = tk.Frame(self, bg=self['bg'])
    if image:
      if isinstance(image, str):
        _img = tk.PhotoImage(file=image)
        label_image = tk.Label(_f, image=_img, bg=self['bg'])
        label_image.image = _img
      else:
        label_image = tk.Label(_f, image=image, bg=self['bg'])
    else:
      label_image = tk.Label(_f, text="", bg=self['bg'])
    label_image.pack(side=left, pady=(0,10))
    WrappingLabel(_f, bg=self['bg'], justify=left, text=discription).pack(side=left, anchor='nw', pady=10, padx=10)
    
    _f.pack(fill='x')




# TODO flash msg when succed or faild

class tkView(View):


  def setup(self, controler, model):
    super().setup(controler, model)

    style_ttk(self.parent, lang=='ar')

    self.notebook = Sidebook(self.parent, justify=left, width=700)
    self.canvas = CanvasCrop(self.parent, self.controler.model, width=294, height=460)

    tabs = [
    ('split', self.frame_split, r'img\icons8-cut-24.png', False),
    ('crop margins', self.frame_crop,r'img\icons8-crop-24.png', False),
    ('rotate pages', self.frame_rotate,r'img\icons8-rotate-24.png', False),
    ('to images', self.frame_image,r'img\icons8-picture-24.png', False),
    ('merge files', self.frame_merge,r'img\icons8-merge-24.png', False),
    ('to pdf', self.frame_to_pdf,r'img\icons8-pdf-24.png', False),
    ('about', self.frame_about, r'img\icons8-settings-24.png', True),
    ]

    for name, frame, icon, bottom in tabs:
      self.notebook.add(frame(), text=_(name), icon=icon, at_bottom=bottom)
    self.notebook.select(0) 

    self.notebook.pack(side=left, anchor='nw', fill='y')
    self.canvas.pack(side=right, anchor='n', padx=10, pady=10)

    self.model.selected_for_split.trace('w', self.controler.on_change_entry)
    self.model.selected_for_crop.trace('w', self.controler.on_change_entry)
    self.model.selected_for_rotate.trace('w', self.controler.on_change_entry)
    self.model.selected_for_images.trace('w', self.controler.on_change_entry)
    self.model._filepath.trace('w', self.controler.on_change_filepath)
    self.model.selected_image.trace('w', self.controler.on_select_image)


  def frame_browse(self, parent, textvariable, discription="Leave blank to include all pages"): 
    
    def add_pdf():
      filepath = filedialog.askopenfilename(title=_("choose PDFs"), filetypes=(('pdf files','*.pdf'),  ("all files","*.*")))
      if filepath:
        self.model.filepath = filepath
        self.tree_pdfs.insert('', tk.END, values=(filepath,))
        self.controler.show_preview(1)
    
    def on_drop_file(event):
      # transform string  like:"{path1} {path2}" to list of string like:['path1', 'path2']
      filespath = event.data.replace("} {", ",").replace('{','').replace('}', '').split(',')
    
      for filepath in filespath:
        if filepath.lower().endswith('.pdf'):
          self.tree_pdfs.insert('', tk.END, values=(filepath,))
          self.model.filepath = filepath
          self.controler.show_preview()
    

    _f = ttk.Frame(parent)

    _g = tk.Frame(_f, bg="#FDFBFA", padx=10, highlightthickness=1, highlightcolor="#ddd", highlightbackground="#ddd")
    tk.Label(_g, text=_("select a file:"), bg=_g['bg']).pack(side=left)
    ttk.Entry(_g, textvariable=self.model._filepath, state='readonly').pack(side=left, padx=10, pady=20, fill='x', expand=True, ipady=1)
    ttk.Button(_g, text=u'', style='icons.TButton', command=add_pdf, width=8).pack(side=right)
    _g.drop_target_register(DND_ALL)
    _g.dnd_bind("<<Drop>>", on_drop_file)
    _g.pack(fill='x')

    ttk.Separator(_f).pack(pady=6)

    _h = ttk.Frame(_f)
    c = [0,1] if lang!='ar' else [1,0]
    ttk.Label(_h, text=_("select pages:")).grid(row=0, column=c[0], sticky=w, padx=(10, 10))
    Entry(_h, textvariable=textvariable, placeholder=_('example: 2,7, 9-20, 56'), justify=left).grid(row=0, column=c[1], sticky='we',ipady=1)
    ttk.Label(_h, text=_(discription), foreground='gray', justify=left).grid(row=1, column=c[1], sticky=w)
    _h.columnconfigure(c[1], weight=1)
   
    _h.pack(fill='x')

    return _f


  def frame_split(self):

    p = Page(title=_("split").capitalize(), 
                image=r"img\icons8-cut-96.png", 
                discription=_("Separate one page or a whole set for easy conversion into independent PDF files."))

    self.frame_browse(p, self.model.selected_for_split, discription="").pack(anchor=w, fill='x')
    ttk.Button(p, text=_('Split file'), command=self.controler.split).pack(anchor=e, pady=(20,0))
  
    return p


  def frame_rotate(self):
    p = Page(title=_("rotate pages").capitalize(), 
          image=r"img\icons8-rotate-96.png", 
          discription=_("Rotate your PDFs the way you need them. You can even rotate multiple PDFs at once!"))

    self.frame_browse(p, self.model.selected_for_rotate).pack(anchor=w, fill='x')

    _g = ttk.Frame(p)
    ttk.Label(_g, text=_('rotate degree:')).pack(side=left)
    # TODO ... change rotation in previw
    ttk.OptionMenu(_g, self.model.rotate, None, '90', '180', '270').pack(side=left, padx=10, ipadx=10)
    _g.pack(anchor=w, pady=(16,0))

    WrappingLabel(p, text=_('90: rotate to right, 180: rotate to left, 270: flip page'), font=('Segoe UI', 10),justify=left, fg='gray', bg=self.parent['bg']).pack(anchor=w)
    ttk.Button(p, text=_('Rotate pages'), command=self.controler.rotate).pack(anchor=e, pady=(20,0))

    return p


  def frame_image(self):
    p = Page(title=_("to images").capitalize(), 
          image=r"img\icons8-picture-96.png", 
          discription=_("Convert each PDF page into a JPG or extract all images contained in a PDF."))


    self.frame_browse(p, self.model.selected_for_images).pack(anchor=w, fill='x')

    _g = ttk.Frame(p)
    tk.Label(_g, text='', font=(FONT_ICONS, 20), fg='gray', bg=self.parent['bg']).pack(side=left, anchor='center')
    ttk.Label(_g, text=_('zoom level:')).pack(side=left, anchor='n', padx=10)
    ttk.OptionMenu(_g, self.model.zoom_images, '1', '1', '2', '3', '4', '5', '6', '7').pack(side=left, ipadx=10, anchor='n')
    _g.pack(anchor=w, pady=16)

    ttk.Checkbutton(p,text=_('Dont convert full pages, just extract images'), variable=self.model.extract_images).pack(anchor=w)
    
    ttk.Button(p, text=_('Convert file'), command=self.controler.convert).pack(anchor=e, pady=(20,0))

    return p


  def frame_crop(self):
    p = Page(title=_("crop margins").capitalize(),
          image=r"img\icons8-crop-96.png", 
          discription=_("Crop your PDF's margins the way you need them. You can even crop spesific pages"))


    self.frame_browse(p, self.model.selected_for_crop).pack(anchor=w, fill='x')

    _g = ttk.Frame(p)

    ttk.Spinbox(_g, from_=0, to=400, textvariable=self.model.top, width=4).grid(row=0, column=2)
    ttk.Label(_g, text=u'', font=(FONT_ICONS,16), justify=left).grid(row=1, column=2)

    ttk.Spinbox(_g, from_=0, to=400, textvariable=self.model.left, width=4).grid(row=2, column=0)
    ttk.Label(_g, text=u'', font=(FONT_ICONS,16), justify=left).grid(row=2, column=1)

    tk.Label(_g, text=u'', font=(FONT_ICONS,24), foreground='purple').grid(row=2, column=2)

    ttk.Label(_g, text=u'', font=(FONT_ICONS,16), justify=left).grid(row=2, column=3)
    ttk.Spinbox(_g, from_=0, to=400, textvariable=self.model.right, width=4).grid(row=2, column=4)

    ttk.Spinbox(_g, from_=0, to=400, textvariable=self.model.bottom, width=4).grid(row=4, column=2)
    ttk.Label(_g, text=u'', font=(FONT_ICONS,16), justify=left).grid(row=3, column=2)

    _g.pack(anchor='center', pady=(10,0))

    ttk.Button(p, text=_('Crop file'), command=self.controler.crop ).pack(anchor=e, pady=(20,0))
    
    return p


  def frame_merge(self):
    
    def add_pdfs():
      filespath = filedialog.askopenfilenames(title="Choose PDFs", filetypes=(('pdf files','*.pdf'),  ("all files","*.*")))
      if filespath:
        for filepath in filespath:
          self.tree_pdfs.insert('', tk.END, values=(filepath,))
          self.tree_pdfs.update()
      
      self.model.filepath = filespath[-1]
      self.controler.show_preview()


    p = Page(title=_("merge files").capitalize(), 
          image=r"img\icons8-merge-96.png", 
          discription=_("Combine PDFs in the order you want with the easiest PDF merger available."))


    self.tree_pdfs = TreeFiles(p, add_files_command=add_pdfs, variable=self.model._filepath, extension=('.pdf'), justify=left)
    self.tree_pdfs.pack(fill='x')

    ttk.Button(p, text=_("Merge files"), command=self.controler.merge ).pack(anchor=e, pady=(20,0))
    return p


  def frame_to_pdf(self):

    def add_images():
      imagespath = filedialog.askopenfilenames(title=_("choose images"), 
                    filetypes=(('images files',('*.jpg', '*.jpeg', '*.png')),  ("all files","*.*")))
      if imagespath:
        for imagepath in imagespath:
          self.tree_images.insert('', tk.END, values=(imagepath,))
          self.tree_images.update()

    p = Page(title=_("create pdf").capitalize(), 
          image=r"img\icons8-pdf-96.png", 
          discription=_("Creat PDF from images in the order you want with the easiest way."))

    self.tree_images = TreeFiles(p, add_files_command=add_images, variable=self.model.selected_image, extension=('.jpg', '.jpeg', '.png'),justify=left)
    self.tree_images.pack(fill='x')

    _g = ttk.Frame(p)
    tk.Label(_g, text=u'', fg='gray', font=(FONT_ICONS, 24), bg=self.parent['bg']).pack(side=left)
    ttk.Label(_g, text=_('pages dimensions:')).pack(side=left, anchor=w)
    ttk.OptionMenu(_g, self.model.dimensions, 'A4' ,'A4',_('dimensions of image')).pack(side=left, padx=10)
    _g.pack(anchor=w, pady=(16,0))
    WrappingLabel(p, text=_('All pages are the size of A4 or each page is the size of the original image'), justify=left, fg='gray', bg=self.parent['bg']).pack(anchor=w)


    ttk.Button(p, text=_("convert to pdf"), command=self.controler.to_pdf).pack(anchor=e, pady=(20,0))
    return p


  def frame_about(self):
    # lang_ch = tk.StringVar(value=self.lang)
    lang_ch = tk.StringVar(value=lang)
    open_ch = tk.BooleanVar(value=open_doc)
    # save_ch = tk.StringVar(value='same dir')

    def save_change():
      global lang, open_doc, _

      _ = partial(gettext, lang=lang_ch.get())
      open_doc = open_ch.get()

      save_config('lang', lang_ch.get())
      save_config('open_doc', open_ch.get())

      if lang_ch.get()!=lang:
        lang = lang_ch.get()
        self.controler.reload()

    p = Page(title=_("settings").capitalize(), 
                image=r"img\icons-pdf-96.png", 
                discription=_("Every tool you need to use PDFs! Merge, split, convert, rotate with just a few clicks."))
    
    settings_frame = tk.Frame(p, bg="#FDFBFA", padx=10, pady=10, highlightthickness=1, highlightcolor="#ddd", highlightbackground="#ddd")
    settings_frame.pack(anchor=w, fill='x', pady=(0, 40))

    _g = ttk.Frame(settings_frame)
    tk.Label(_g, text=u"", font=(FONT_ICONS, 18), fg='gray', bg=self.parent['bg']).pack(side=left, anchor=w)
    ttk.Label(_g, text=_('Choose language:')).pack(side=left, anchor=w, padx=10)
    ttk.OptionMenu(_g, lang_ch, lang, 'en', 'ar', 'fr').pack(side=left, ipadx=5)
    _g.pack(fill='x')
  
    _h = ttk.Frame(settings_frame)
    tk.Label(_h, text=u"", font=(FONT_ICONS, 18), fg='gray', bg=self.parent['bg']).pack(side=left, anchor=w)
    ttk.Checkbutton(_h, text=_('open pdf after operation is finished'), variable=open_ch).pack(side=left,anchor=w, padx=(10,5))
    _h.pack(fill='x', pady=(10,0))

    _j = ttk.Frame(p)
    tk.Label(_j, text=u"", font=(FONT_ICONS, 16), fg='gray', bg=self.parent['bg']).pack(side=left, anchor=w)
    ttk.Label(_j, text="https://icons8.com", foreground='gray',justify=left).pack(side=left,anchor=w, padx=10)
    _j.pack(fill='x', pady=4)

    _i = ttk.Frame(p)
    tk.Label(_i, text=u"", font=(FONT_ICONS, 16), fg='gray', bg=self.parent['bg']).pack(side=left, anchor=w)
    ttk.Label(_i, text="@youssefhoummad", foreground='gray',justify=left).pack(side=left,anchor=w, padx=10)
    _i.pack(fill='x', pady=4)

    ttk.Button(p, text=_('save'), command=save_change).pack(expand=True, anchor=e, pady=(30,0))
    return p


  def before_operation(self):
    print('processing...')


  def after_operation(self, result=None):
    print('done')
    try:
      if open_doc:
        os.startfile(result)
      toast = Notification(app_id='pdf tools', title=_("done"), msg=result, icon=os.path.abspath(r"img/icon.ico"))
      toast.add_actions(label=_("open"), launch=result)
      toast.set_audio(audio.Default, loop=False)
      toast.show()

    except:
      toast = Notification(app_id='pdf-tools', title=_("operation failed"), msg=result)
      toast.add_actions(label=_("open"), launch=result)
      toast.set_audio(audio.Default, loop=False)
      toast.show()
      print('error')


  def need_file_flash(self):
    print('pick a file..')




def style_ttk(root, rtl=False):
  global right, left, w, e
  left, right = 'left', 'right'
  w, e = 'w', 'e'

  if rtl:
    right, left = left, right
    w, e = e, w
  
  style = ttk.Style(root)
  style.layout('TCheckbutton',
      [('Checkbutton.padding', {'sticky': 'nswe', 'children': [
          ('Checkbutton.focus', {
            'side': right, 'sticky': w,'children': [('Checkbutton.label', {'sticky': 'nswe'})]
          }),
          ('Checkbutton.indicator', {'side': right, 'sticky': ''})
      ]})]
    )

  style.configure('TButton', padding=(4, 2))
  style.configure('Accent.TButton', padding=(4, 2))
  style.configure('icons.TButton', font=(FONT_ICONS, 12), padding=2)


  for Tstyle in ('TFrame', 'TLabel', 'TNotebook', 'TCheckbutton', 'TMenubutton'):
    style.configure(Tstyle, background="#EEF4F9")




  
def save_config(variable:str, value)->None:
  # config = ConfigParser()
  config.read('config.ini')
  config.set('main', variable, str(value))
  with open('config.ini', 'w') as configfile:
    config.write(configfile) 



def main():
  try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
  except:
      pass
  # import pyglet
  # pyglet.font.add_file('file.ttf')
  
  root = TkinterDnD.Tk() # work with drog and drop

  root.title("Pdf tools")
  root.minsize(800, 560)  
  root.iconbitmap(default=r'img\icon.ico')
  root.configure( background="#EEF4F9")
  # root.resizable(width=False, height=False)

  app = App(root, tkView, Model)
  app.mainloop()


if __name__ == '__main__':
  main()