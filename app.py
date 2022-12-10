import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from mvc import View, Controler
import functions
import widgets

#TODO if selected pgae bigger th lenght pdf 


def str_to_list(string:str)-> list[int|tuple]:
  """like 1,4, 6, 20-33"""

  result = []
  string_filtred = "".join(filter(lambda char: char in  "0123456789-,", string))
  for item in string_filtred.split(","):
    if '-' in item:
      x, y = item.split('-')
      result.append((int(x), int(y)+1))
    else:
      if item:
        result.append(int(item))
  return result


def last_in_list(string:str)-> int:
  string = string.replace("-", ",")
  string_filtred = "".join(filter(lambda char: char in  "0123456789,", string))
  str_list = string_filtred.split(",")
  str_list = list(filter(None, str_list))
  if not str_list: return 0
  return  int(str_list[-1])



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





class App(Controler):

  def __init__(self, parent, View, Model):
    super().__init__(parent, View, Model)

    self.thread = self.view.thread


  @property
  def filepath(self):
    return self.model.filepath
  

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

      self.show_preview(1)
      self.view.tree.insert('', tk.END, values=(filepath,))


  def multi_browse(self):
    filespath = filedialog.askopenfilenames(title="Choose PDFs", filetypes=(('pdf files','*.pdf'),  ("all files","*.*")))
    if filespath:
      for filepath in filespath:
        self.view.tree.insert('', tk.END, values=(filepath,))


  def show_preview(self, page=1):
    img = functions.page_thumbnails(self.filepath, page=page-1)
    self.view.canvas.show_image(img)
  



  def split(self):
    if not self.filepath or not self.model.selected_for_split.get():
      return
    selected_pages = str_to_list(self.model.selected_for_split.get())
    
    self.thread(functions.split, args=(self.filepath, selected_pages))


  def merge(self):
    if len(self.filespath)<2:
      return
    self.thread(functions.merge, args=(self.filespath,))


  def crop(self):
    if not self.filepath or not any(self.margins):
      return
    selected_pages = str_to_list(self.model.selected_for_crop.get())
    self.thread(functions.crop, args=(self.filepath, *self.margins, selected_pages))


  def convert(self):
    if not self.filepath:
      return
    selected_pages = str_to_list(self.model.selected_for_images.get())
    if self.extract_images:
      self.thread(functions.extract_images, args=(self.filepath, selected_pages))
    else:
      self.thread(functions.to_images, args=(self.filepath, selected_pages, self.zoom_images))


  def rotate(self):
    if not self.model.filepath:
      return
    degree = self.model.rotate.get()
    selected_pges = str_to_list(self.model.selected_for_rotate.get())
    self.thread(functions.merge, args=(self.model.filepath, degree, selected_pges))




class TabedView(View):


  def setup(self, controler, model):
    super().setup(controler, model)

    self.progressbar = ttk.Progressbar(self.parent, orient='horizontal', mode='determinate', maximum=20)
  
    notebook = ttk.Notebook(self.parent, padding=0)

    notebook.add(self.frame_split(notebook), text="split file")
    notebook.add(self.frame_crop(notebook), text="crop margins")
    notebook.add(self.frame_merge(notebook), text="merge files")
    notebook.add(self.frame_rotate(notebook), text="rotate pages")
    notebook.add(self.frame_image(notebook), text="convert to images")
    
    canvas = widgets.Canvas(self.parent, self.controler.model)
  
    notebook.grid(row=0, column=0)
    canvas.grid(row=0, column=1, rowspan=3, padx=10, pady=10)

    self.notebook = notebook
    self.canvas = canvas

    self.model.selected_for_split.trace('w', self.on_change_entry)
    self.model.selected_for_crop.trace('w', self.on_change_entry)
    self.model.selected_for_rotate.trace('w', self.on_change_entry)
    self.model.selected_for_images.trace('w', self.on_change_entry)


  def frame_split(self, parent):

    _f = ttk.Frame(parent, padding=15)

    ttk.Label(_f, text="select name: ").grid(row=0, column=0, pady=20)
    ttk.Entry(_f, textvariable=self.model.filepath, state='readonly', width=40).grid(row=0, column=1, padx=5)
    ttk.Button(_f, text='browse', command=self.controler.browse).grid(row=0, column=2)

    ttk.Label(_f, text='select pages:').grid(row=1, column=0, pady=(20,0))
    ttk.Entry(_f, width=40, textvariable=self.model.selected_for_split).grid(row=1, column=1)

    ttk.Label(_f, text='like 2,7, 9-10, 56', foreground='gray').grid(row=2, column=1, sticky='nw', pady=(0,20))
    ttk.Label(_f, text='NB: you can use this widgte to rerrange file,\nlike:"3,2,1"', foreground='gray').grid(row=3, column=0, columnspan=2, sticky='nw')

    ttk.Button(_f, text='Split file', command=self.controler.split, style="Accent.TButton").grid(row=4, column=2, sticky='sw')
    _f.rowconfigure(4,weight=1)
    return _f


  def frame_rotate(self, parent):
    _f = ttk.Frame(parent, padding=15)
    
    ttk.Label(_f, text="select name: ").grid(row=0, column=0, pady=20)
    ttk.Entry(_f, textvariable=self.model.filepath, state='readonly', width=40).grid(row=0, column=1, padx=5)
    ttk.Button(_f, text='browse', command=self.controler.browse).grid(row=0, column=2)

    ttk.Label(_f, text='select pages:').grid(row=1, column=0, pady=(20,0))
    ttk.Entry(_f, width=40, textvariable=self.model.selected_for_rotate).grid(row=1, column=1)
    ttk.Label(_f, text='like 2,7, 9-10, 56\nemprty = all pages', foreground='gray').grid(row=2, column=1, sticky='w')

    ttk.Label(_f, text='rotate degree:').grid(row=3, column=0, pady=20)
    ttk.OptionMenu(_f, self.model.rotate, '90', '90', '180', '270').grid(row=3, column=1, sticky='w', ipadx=10)

    ttk.Button(_f, text='rotate pages', command=self.controler.rotate,style="Accent.TButton").grid(row=4, column=2, sticky='sw')
    _f.rowconfigure(4,weight=1)

    return _f


  def frame_image(self, parent):

    _f = ttk.Frame(parent, padding=15)
 
    ttk.Label(_f, text="select name: ").grid(row=0, column=0, pady=20)
    ttk.Entry(_f, textvariable=self.model.filepath, state='readonly', width=40).grid(row=0, column=1, padx=5)
    ttk.Button(_f, text='browse', command=self.controler.browse).grid(row=0, column=2)

    ttk.Label(_f, text='select pages: ').grid(row=1, column=0, pady=10)
    ttk.Entry(_f, width=40, textvariable=self.model.selected_for_images).grid(row=1, column=1)
    ttk.Label(_f, text='like 2,7, 9-10, 56\napplly on all pages if is empty', foreground='gray').grid(row=2, column=1, sticky='w')

    ttk.Label(_f, text='zoom level:').grid(row=3, column=0, sticky='w', pady=(20,0))
    ttk.OptionMenu(_f, self.model.zoom_images, '1', '2', '3', '4', '5', '6', '7').grid(row=3, column=1, ipadx=10, sticky='w',pady=(20,0))
    ttk.Label(_f, text='make image bigger or smaller, noraml=3', foreground='gray').grid(row=4, column=0, sticky='w', columnspan=3)

    ttk.Checkbutton(_f, text='Dont convert full pages, just extract image', variable=self.model.extract_images, style="Switch.TCheckbutton").grid(row=5, column=0, columnspan=2, sticky='w', pady=(20,0))
    ttk.Button(_f, text='Convert file', command=self.controler.convert,style="Accent.TButton").grid(row=6, column=2, sticky='sw')
    _f.rowconfigure(6,weight=1)

    return _f


  def frame_crop(self, parent):

    _f = ttk.Frame(parent, padding=15)

    ttk.Label(_f, text="select name: ").grid(row=0, column=0, pady=20)
    ttk.Entry(_f, textvariable=self.model.filepath, state='readonly', width=40).grid(row=0, column=1, columnspan=4, padx=5)
    ttk.Button(_f, text='browse', command=self.controler.browse).grid(row=0, column=5)

    ttk.Label(_f, text='select pages: ').grid(row=1, column=0, pady=10, sticky='w')
    ttk.Entry(_f, width=40, textvariable=self.model.selected_for_crop).grid(row=1, column=1, columnspan=4)
    ttk.Label(_f, text='like 2,7, 9-10, 56\napplly on all pages if is empty', foreground='gray').grid(row=2, column=1, sticky='w', columnspan=3, pady=(0,20))

    ttk.Label(_f, text='top: ').grid(row=3, column=0)
    ttk.Spinbox(_f, from_=0, to=200, textvariable=self.model.top, width=4).grid(row=3, column=1, pady=8, padx=(0,30))
    ttk.Label(_f, text='bottom: ').grid(row=3, column=2)
    ttk.Spinbox(_f, from_=0, to=200, textvariable=self.model.bottom, width=4).grid(row=3, column=3, pady=8, padx=(0,30))

    ttk.Label(_f, text='left: ').grid(row=4, column=0)
    ttk.Spinbox(_f, from_=0, to=200, textvariable=self.model.left, width=4).grid(row=4, column=1, pady=8, padx=(0,30))
    ttk.Label(_f, text='right: ').grid(row=4, column=2)
    ttk.Spinbox(_f, from_=0, to=200, textvariable=self.model.right, width=4).grid(row=4, column=3, pady=8, padx=(0,30))

    ttk.Button(_f, text='Crop file', command=self.controler.crop ,style="Accent.TButton").grid(row=5, column=5, sticky='e')
    _f.rowconfigure(5,weight=1)

    return _f


  def frame_merge(self, parent):

    _f = ttk.Frame(parent, padding=15)
    _f.columnconfigure(0, weight=1)

    tree = ttk.Treeview(_f, show='headings')
    tree["columns"]=("files")
    tree.heading("#0", text="files")

    ttk.Button(_f, text="add files", command=self.controler.multi_browse ,style="Accent.TButton").grid(row=0, column=0, sticky='w')
    ttk.Button(_f, text="clear all", command=self.clear).grid(row=0, column=1)
    ttk.Button(_f, text="del selected", command=self.delete).grid(row=0, column=2)
    ttk.Button(_f, text="move up", command=self.move_up).grid(row=0, column=3)
    ttk.Button(_f, text="move down", command=self.move_down).grid(row=0, column=4)

    tree.grid(row=1, column=0, columnspan=5, sticky='snew')

    ttk.Button(_f, text="merge files", command=self.controler.merge ,style="Accent.TButton").grid(row=5, column=4, sticky='ne', pady=10)
    _f.rowconfigure(5,weight=1)
    tree.bind('<ButtonRelease-1>', self.on_select_item)
    
    self.tree = tree
    return _f


  def on_select_item(self, *args):
    selections = self.tree.selection()
    if not selections: return
    
    selected = selections[0]
    path = self.tree.item(selected)['values'][0]
      
    self.model.filepath = path
    self.controler.show_preview()


  def delete(self):
    selected = self.tree.selection()[0]
    self.tree.delete(selected)
    self.canvas.clean()


  def clear(self):
    for item in self.tree.get_children():
      self.tree.delete(item)
    self.canvas.clean()


  def move_up(self):
    leaves = self.tree.selection()
    for i in leaves:
        self.tree.move(i, self.tree.parent(i), self.tree.index(i)-1)
    print('move up...')


  def move_down(self):
    leaves = self.tree.selection()
    for i in reversed(leaves):
        self.tree.move(i, self.tree.parent(i), self.tree.index(i)+1)
    print('move down...')


  def on_change_entry(self, *args, **kwargs):
    if not self.model.filepath: return
    tab_dict = {
      'split':self.model.selected_for_split,
      'crop':self.model.selected_for_crop,
      'image':self.model.selected_for_images,
      'rotate':self.model.selected_for_rotate,
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
      # print(f'this file has {self.model.pages}')
      return

    self.controler.show_preview(last_page)


  def thread(self, target, args=(), kwargs={}):
    """ use this methode for make progress bar update"""

    thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    thread.start()

    self.parent.update()
    self.progressbar.place(x=0, y=1, width=(self.parent.winfo_width()), height=10)
    self.progressbar.start()

    # checks whether thread is alive #
    while thread.is_alive():
        self.parent.update()
        pass


    self.progressbar.stop()
    self.progressbar['value'] = 100

    self.parent.after(3000, self.progressbar.place_forget)

