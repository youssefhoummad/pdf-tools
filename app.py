from configparser import ConfigParser
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from functools import partial

from tkinterdnd2 import *

import functions
import languages
from utils import *


config = ConfigParser()

if not os.path.exists('config.ini'):
  import locale
  locale_lang = locale.getdefaultlocale()[0][0:2]
  lang = 'en'
  if locale_lang in ('ar', 'fr'):
    lang = locale_lang

  config['main'] = {'lang': lang, 'open_doc': True}
  config.write(open('config.ini', 'w'))

config.read('config.ini')

# setting
lang = config.get('main', 'lang')
open_doc = config.getboolean('main', 'open_doc')


# constants
left = 'left'
right = 'right'
w = 'w'
e = 'e'

if lang == 'ar':
  left, right = right, left
  w, e = e, w

# language translator
_ = partial(languages.gettext, lang=lang)


# store all data here

class Model:
  def __init__(self, parent) -> None:
    self.parent = parent

    self._filepath = tk.StringVar()

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
    self.pages = functions.pages(value)


# the real app inherit from <Controller> abstract

class App(Controler):

  def __init__(self, parent, View, Model):
    super().__init__(parent, View, Model)

  
  def thread(self, target, args=(), kwargs={}):
    """ use this methode for make progress bar update"""

    thread = ThreadWithResult(target=target, args=args, kwargs=kwargs)
    thread.log_thread_status = False
    thread.start()
    thread.join()

    self.parent.update()
    self.view.progressbar.place(relx=0, rely=0, width=(self.parent.winfo_width()), height=10)
    self.view.progressbar.start()

    # checks whether thread is alive #
    while thread.is_alive():
        self.parent.update()
        pass
    
    self.view.progressbar.stop()
    self.view.progressbar['value'] = 100


    if open_doc:
      os.startfile(thread.result)

    self.parent.after(3000, self.view.progressbar.place_forget)

  def need_file_flash(self):
    # Messagebox.ok(_("no file selected"))
    print('select a file..')


  @property
  def filespath(self):
    return list(self.view.tree.set(item,0) for item in self.view.tree.get_children())

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
  
  
  def browse(self):
    filepath = filedialog.askopenfilename(title="Choose PDFs", filetypes=(('pdf files','*.pdf'),  ("all files","*.*")))
    if filepath:
      self.model.filepath = filepath
      self.view.tree.insert('', tk.END, values=(filepath,))

      self.show_preview(1)


  def multi_browse(self):
    filespath = filedialog.askopenfilenames(title="Choose PDFs", filetypes=(('pdf files','*.pdf'),  ("all files","*.*")))
    if filespath:
      for filepath in filespath:
        self.view.tree.insert('', tk.END, values=(filepath,))
    
    self.model.filepath = self.filespath[-1]
    self.show_preview()


  def show_preview(self, page=1):
    img = functions.page_thumbnails(self.model.filepath, page=page-1)
    self.view.canvas.show_image(img)
  

  def split(self):
    if not self.model.filepath or not self.model.selected_for_split.get():
      self.need_file_flash()
      return
    selected_pages = str_to_list(self.model.selected_for_split.get())
    
    self.thread(functions.split, args=(self.model.filepath, selected_pages))


  def merge(self):
    if len(self.filespath)<2:
      self.need_file_flash()
      return
    self.thread(functions.merge, args=(self.filespath,))


  def crop(self):
    if not self.model.filepath or not any(self.margins):
      self.need_file_flash()
      return
    selected_pages = str_to_list(self.model.selected_for_crop.get())
    self.thread(functions.crop, args=(self.model.filepath, *self.margins, selected_pages))


  def convert(self):
    if not self.model.filepath:
      self.need_file_flash()
      return
    selected_pages = str_to_list(self.model.selected_for_images.get())
    if self.extract_images:
      self.thread(functions.extract_images, args=(self.model.filepath, selected_pages))
    else:
      self.thread(functions.to_images, args=(self.model.filepath, selected_pages, self.zoom_images))


  def rotate(self):
    if not self.model.filepath:
      self.need_file_flash()
      return
    degree = self.model.rotate.get()
    selected_pages = str_to_list(self.model.selected_for_rotate.get())
    print(f"{degree}, {selected_pages}")
    self.thread(functions.rotate, args=(self.model.filepath, int(degree), selected_pages))


# tkinter Gui inherit from <View> abstract

class tkView(View):


  def setup(self, controler, model):
    super().setup(controler, model)
    global lang
    
    style_ttk(self.parent)

    self.progressbar = ttk.Progressbar(self.parent, orient='horizontal', mode='determinate', maximum=20)
  
    notebook = ttk.Notebook(self.parent, padding=0)
    
    canvas = Canvas(self.parent, self.controler.model, text_preview=_("P R E V I E W"))
    canvas.drop_target_register(DND_ALL)
    canvas.dnd_bind("<<Drop>>", self.on_drop_file)


    if lang == 'ar':
      notebook.add(self.frame_about(notebook), text=_("about"))
      notebook.add(self.frame_image(notebook), text=_("to images"))
      notebook.add(self.frame_crop(notebook), text=_("crop margins"))
      notebook.add(self.frame_rotate(notebook), text=_("rotate pages"))
      notebook.add(self.frame_merge(notebook), text=_("merge files"))
      notebook.add(self.frame_split(notebook), text=_("split"))
      notebook.select(5)
      notebook.grid(row=0, column=1, sticky='ne', pady=10)
      canvas.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky='nw')
    else:
      notebook.add(self.frame_split(notebook), text=_("split"))
      notebook.add(self.frame_crop(notebook), text=_("crop margins"))
      notebook.add(self.frame_merge(notebook), text=_("merge files"))
      notebook.add(self.frame_rotate(notebook), text=_("rotate pages"))
      notebook.add(self.frame_image(notebook), text=_("to images"))
      notebook.add(self.frame_about(notebook), text=_("about"))
      notebook.grid(row=0, column=0, sticky='nw', pady=10, padx=10)
      canvas.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky='ne')

    self.notebook = notebook
    self.canvas = canvas

    self.model.selected_for_split.trace('w', self.on_change_entry)
    self.model.selected_for_crop.trace('w', self.on_change_entry)
    self.model.selected_for_rotate.trace('w', self.on_change_entry)
    self.model.selected_for_images.trace('w', self.on_change_entry)

    style_ttk(self.parent)



  def frame_about(self, parent):
    lang_ch = tk.StringVar(value=lang)
    open_ch = tk.BooleanVar(value=open_doc)

    def save_change():
      global lang, open_doc, _

      _ = partial(languages.gettext, lang=lang_ch.get())

      save_config('lang', lang_ch.get())
      save_config('open_doc', open_ch.get())

      open_doc = open_ch.get()
      # if language change  reload all view app
      if lang_ch.get()!=lang:
        lang = lang_ch.get()
        self.controler.reload()
        style_root(self.parent)
      
    _f = ttk.Frame(parent, padding=15)
    ttk.Label(_f, text=_("Every tool you need to use PDFs! Merge, split, convert, rotate with just a few clicks."), wraplength=500, justify=left).pack(side='top', anchor=w, pady=12)
    ttk.Label(_f, text="@youssefhoummad", justify=left).pack(side='top', anchor=w, pady=(8,20))

    _g = ttk.Frame(_f)
    ttk.Label(_g, text=_('Choose language:')).pack(side=left, anchor=w, padx=5)
    ttk.OptionMenu(_g, lang_ch, lang, 'en', 'ar', 'fr').pack(side=left, padx=10)
    _g.pack(side='top', anchor=w, pady=12)

    ttk.Checkbutton(_f,text=_('open pdf after operation is finished'), variable=open_ch).pack(side='top', anchor=w, pady=12)

    ttk.Button(_f, text='save', command=save_change).pack(side='bottom', anchor=e)


    return _f
  

  def frame_browse_pages(self, parent, textvariable): 
    _f = ttk.Frame(parent)
    

    if lang == 'ar':
      ttk.Label(_f, text=_("select a file:")).grid(row=0, column=2, sticky=w, pady=(0,25))
      ttk.Entry(_f, textvariable=self.model._filepath, state='readonly', width=40).grid(row=0, column=1, padx=5, pady=(0,25))
      ttk.Button(_f, text=_('browse'), command=self.controler.browse).grid(row=0, column=0, pady=(0,25))

      ttk.Label(_f, text=_("select pages:")).grid(row=2, column=2, sticky=w)
      ttk.Entry(_f, textvariable=textvariable, width=40, justify='right').grid(row=2, column=1, padx=5)
      ttk.Label(_f, text=_('like 2,7, 9-20, 56'), foreground='gray').grid(row=3, column=1, sticky=w)
    else:
      ttk.Label(_f, text=_("select a file:")).grid(row=0, column=0, pady=(0,25))
      ttk.Entry(_f, textvariable=self.model._filepath, state='readonly', width=40).grid(row=0, column=1, padx=5, pady=(0,25))
      ttk.Button(_f, text=_('browse'), command=self.controler.browse).grid(row=0, column=2, pady=(0,25))

      ttk.Label(_f, text=_("select pages:")).grid(row=2, column=0, sticky=w)
      ttk.Entry(_f, textvariable=textvariable, width=40).grid(row=2, column=1)
      ttk.Label(_f, text=_('like 2,7, 9-20, 56'), foreground='gray').grid(row=3, column=1, sticky=w)

    _f.drop_target_register(DND_ALL)
    _f.dnd_bind("<<Drop>>", self.on_drop_file)

    return _f


  def frame_split(self, parent):

    _f = ttk.Frame(parent, padding=15)
    ttk.Label(_f, text=_("Separate one page or a whole set for easy conversion into independent PDF files."), wraplength=500, justify=left).grid(row=0, column=0, columnspan=3, pady=10, sticky=w)
    self.frame_browse_pages(_f, self.model.selected_for_split).grid(row=1, column=0, columnspan=3, pady=(20,0))

    ttk.Button(_f, text=_('Split file'), command=self.controler.split).grid(row=3, column=0, columnspan=3, sticky=e+'s')
    _f.rowconfigure(3,weight=1)
    return _f


  def frame_rotate(self, parent):
    _f = ttk.Frame(parent, padding=15)
    ttk.Label(_f, text=_("Rotate your PDFs the way you need them. You can even rotate multiple PDFs at once!"), wraplength=500, justify=left).grid(row=0, column=0, columnspan=3, pady=10, sticky=w)
    self.frame_browse_pages(_f, self.model.selected_for_rotate).grid(row=1, column=0, columnspan=3, pady=20)

    _g = ttk.Frame(_f)

    ttk.Label(_g, text=_('rotate degree:')).pack(side=left)
    ttk.OptionMenu(_g, self.model.rotate, '90', '90', '180', '270').pack(side=left, padx=10, ipadx=10)

    _g.grid(row=2, column=0, columnspan=3, sticky=w)

    ttk.Button(_f, text=_('Rotate pages'), command=self.controler.rotate).grid(row=3, column=0, columnspan=3, sticky=e+'s')
    _f.rowconfigure(3,weight=1)

    return _f


  def frame_image(self, parent):

    _f = ttk.Frame(parent, padding=15)
    ttk.Label(_f, text=_("Convert each PDF page into a JPG or extract all images contained in a PDF."), wraplength=500, justify=left).grid(row=0, column=0, columnspan=3, pady=10, sticky=w) 
    self.frame_browse_pages(_f, self.model.selected_for_images).grid(row=1, column=0, columnspan=3, pady=20)

    _g = ttk.Frame(_f)
    ttk.Label(_g, text=_('zoom level:')).pack(side=left, anchor=w)
    ttk.OptionMenu(_g, self.model.zoom_images, '1', '2', '3', '4', '5', '6', '7').pack(side=left, padx=10)
    _g.grid(row=2, column=0, columnspan=3, sticky=w)

    ttk.Checkbutton(_f,text=_('Dont convert full pages, just extract images'), variable=self.model.extract_images).grid(row=3, column=0, columnspan=3, sticky=w, pady=(20,0))
    
    ttk.Button(_f, text=_('Convert file'), command=self.controler.convert).grid(row=6, column=0, columnspan=3, sticky=e+'s')
    _f.rowconfigure(6,weight=1)

    return _f


  def frame_crop(self, parent):

    _f = ttk.Frame(parent, padding=15)
    ttk.Label(_f, text=_("Crop your PDF's margins the way you need them. You can even crop spesific pages"), wraplength=500, justify=left).grid(row=0, column=0, columnspan=5, pady=10, sticky=w) 


    self.frame_browse_pages(_f, self.model.selected_for_crop).grid(row=1, column=0, columnspan=5, pady=20)

    if lang == "ar":
      ttk.Label(_f, text=_('top:'), justify=left).grid(row=3, column=3, sticky=e)
      ttk.Spinbox(_f, from_=0, to=400, textvariable=self.model.top, width=4).grid(row=3, column=2, pady=8, padx=(0,30), sticky=w)
      ttk.Label(_f, text=_('bottom:'), justify=left).grid(row=3, column=1, sticky=e)
      ttk.Spinbox(_f, from_=0, to=400, textvariable=self.model.bottom, width=4).grid(row=3, column=0, pady=8, padx=(0,30), sticky=w)

      ttk.Label(_f, text=_('left:'), justify=left).grid(row=4, column=3, sticky=e)
      ttk.Spinbox(_f, from_=0, to=400, textvariable=self.model.left, width=4).grid(row=4, column=2, pady=8, padx=(0,30), sticky=w)
      ttk.Label(_f, text=_('right:'), justify=left).grid(row=4, column=1, sticky=e)
      ttk.Spinbox(_f, from_=0, to=400, textvariable=self.model.right, width=4).grid(row=4, column=0, pady=8, padx=(0,30), sticky=w)
      
    else:
      ttk.Label(_f, text=_('top:'), justify=left).grid(row=3, column=0, sticky=e)
      ttk.Spinbox(_f, from_=0, to=400, textvariable=self.model.top, width=4).grid(row=3, column=1, pady=8, padx=(0,30), sticky=w)
      ttk.Label(_f, text=_('bottom:'), justify=left).grid(row=3, column=2, sticky=e)
      ttk.Spinbox(_f, from_=0, to=400, textvariable=self.model.bottom, width=4).grid(row=3, column=3, pady=8, padx=(0,30), sticky=w)

      ttk.Label(_f, text=_('left:'), justify=left).grid(row=4, column=0, sticky=e)
      ttk.Spinbox(_f, from_=0, to=400, textvariable=self.model.left, width=4).grid(row=4, column=1, pady=8, padx=(0,30), sticky=w)
      ttk.Label(_f, text=_('right:'), justify=left).grid(row=4, column=2, sticky=e)
      ttk.Spinbox(_f, from_=0, to=400, textvariable=self.model.right, width=4).grid(row=4, column=3, pady=8, padx=(0,30), sticky=w)

    ttk.Button(_f, text=_('Crop file'), command=self.controler.crop ).grid(row=5, column=0, columnspan=5, sticky=e+'s')
    _f.rowconfigure(5,weight=1)

    return _f


  def frame_merge(self, parent):

    _f = ttk.Frame(parent, padding=15)
    ttk.Label(_f, text=_("Combine PDFs in the order you want with the easiest PDF merger available."), wraplength=500, justify=left).grid(row=0, column=0, columnspan=5, pady=(10, 20), sticky=w) 


    _f.columnconfigure(1, weight=1)
    tree = ttk.Treeview(_f, show='')
    tree["columns"]=("files")
    tree.heading("#0", text="files")

    ttk.Button(_f, text="add files", command=self.controler.multi_browse).grid(row=1, column=0, sticky=w)

    ttk.Button(_f, text="clear all", command=self.clear).grid(row=1, column=1, sticky='e')
    ttk.Button(_f, text="del selected", command=self.delete).grid(row=1, column=2, padx=2)
    ttk.Button(_f, text="move up", command=self.move_up).grid(row=1, column=3)
    ttk.Button(_f, text="move down", command=self.move_down).grid(row=1, column=4, padx=2)

    tree.grid(row=2, column=0, columnspan=5, sticky='snew', pady=4)

    ttk.Button(_f, text=_("Merge files"), command=self.controler.merge ).grid(row=5, column=0,columnspan=5, sticky=e+'s', pady=10)
    _f.rowconfigure(5,weight=1)

    tree.bind('<ButtonRelease-1>', self.on_select_item)
    tree.bind('<<TreeviewSelect>>', self.on_select_item)

    tree.drop_target_register(DND_ALL)
    tree.dnd_bind("<<Drop>>", self.on_drop_files)    

    self.tree = tree
    return _f


  def on_drop_file(self, event):

    # transform string  like:"{path1} {path2}" to list of string like:['path1', 'path2']
    filespath = event.data.replace("} {", ",").replace('{','').replace('}', '').split(',')
  
    for filepath in filespath:
      if filepath.lower().endswith('.pdf'):
        self.tree.insert('', tk.END, values=(filepath,))
        self.model.filepath = filepath
        self.controler.show_preview()

        return


  def on_drop_files(self, event):

    # transform string  like:"{path1} {path2}" to list of string like:['path1', 'path2']
    filespath = event.data.replace("} {", ",").replace('{','').replace('}', '').split(',')
  
    for filepath in filespath:
      if filepath.lower().endswith('.pdf'):
        self.tree.insert('', tk.END, values=(filepath,))
    

  def on_select_item(self, *args):
    selections = self.tree.selection()
    if not selections: return
    
    selected = selections[0]
    path = self.tree.item(selected)['values'][0]
      
    self.model.filepath = path
    self.controler.show_preview()


  def delete(self):
    elements =  self.tree.selection()
    if not elements:
      return 
    selected = elements[0]
    self.tree.delete(selected)
    self.canvas.clean()


  def clear(self):
    if not self.tree.get_children():
      return
    for item in self.tree.get_children():
      self.tree.delete(item)
    self.canvas.clean()


  def move_up(self):
    leaves = self.tree.selection()
    for i in leaves:
        self.tree.move(i, self.tree.parent(i), self.tree.index(i)-1)


  def move_down(self):
    leaves = self.tree.selection()
    for i in reversed(leaves):
        self.tree.move(i, self.tree.parent(i), self.tree.index(i)+1)


  def on_change_entry(self, *args, **kwargs):

    if not self.model.filepath:
      # self.int_entry.state(["!invalid"])
      return
    tab_dict = {
      _('split'):self.model.selected_for_split,
      _('crop margins'):self.model.selected_for_crop,
      _('to images'):self.model.selected_for_images,
      _('rotate pages'):self.model.selected_for_rotate,
    }

    tab = self.notebook.tab(self.notebook.select(), "text")
    variable = None
    for tab_text in tab_dict:
      if tab_text in tab:
        variable = tab_dict[tab_text]
  

    last_page = last_in_list(variable.get())

    if not last_page:
      return

    if last_page>self.model.pages:
      return

    self.controler.show_preview(last_page)



def style_root(root):
  # from tkinter import font
  import tempfile

  # transparent icon
  ICON = (b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
          b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
          b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
          b'\x00\x01\x00\x00\x00\x01') + b'\x00'*1282 + b'\xff'*64

  _, ICON_PATH = tempfile.mkstemp()
  with open(ICON_PATH, 'wb') as icon_file:
      icon_file.write(ICON)

  # theme = config.get('main', 'theme')

  # sv_ttk.set_theme(theme)
  # font.nametofont("SunValleyBodyFont").configure(family="Segoe UI")
  # font.nametofont("SunValleyBodyStrongFont").configure(family="Segoe UI Black", weight="bold")
  root.iconbitmap(default=ICON_PATH)
  root.configure( background="#EEF4F9")


def style_ttk(root):
  global right, left, w, e
  left = 'left'
  right = 'right'
  w = 'w'
  e = 'e'

  style = ttk.Style(root)
  style.configure('TNotebook.Tab',padding=(8,3)) # tabposition='wn' option to change position of tab
  style.configure('Accent.TButton', padding=(4, 2))
  style.configure('TNotebook', tabposition='nw')

  if lang == 'ar':
    right, left = left, right
    w, e = e, w
    style.configure('TNotebook', tabposition='ne')

  style.layout('TCheckbutton',
      [('Checkbutton.padding', {'sticky': 'nswe', 'children': [
          ('Checkbutton.focus', {
            'side': right, 'sticky': w,'children': [('Checkbutton.label', {'sticky': 'nswe'})]
          }),
          ('Checkbutton.indicator', {'side': right, 'sticky': ''})
      ]})]
    )


  for Tstyle in ('TFrame', 'TLabel', 'TNotebook', 'TCheckbutton', 'TMenubutton'):
    style.configure(Tstyle, background="#EEF4F9")

  
def save_config(variable:str, value)->None:
  config = ConfigParser()
  config.read('config.ini')
  config.set('main', variable, str(value))
  with open('config.ini', 'w') as configfile:
    config.write(configfile) 



def main():
  root = TkinterDnD.Tk() # work with drog and drop

  root.title("Pdf tools")
  # root.geometry('872x500')
  style_root(root)
  # style_ttk(root)

  root.resizable(width=False, height=False)

  app = App(root, tkView, Model)

  app.mainloop()


if __name__ == '__main__':
  main()