import os
import io
import threading
import queue
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from abc import ABC, abstractmethod

from PIL import Image, ImageTk
import fitz
from tkinterdnd2 import *


# TODO.. translate gui
class Lang:
  def __init__(self, lang='en') -> None:
     pass


# functions to muniplate pdf docs

def save_path(filepath:str ,refain:str):
    save_path:str = "{}_{}ed.pdf".format(filepath[:-4], refain)
    if not os.path.isfile(save_path):
        return save_path
    
    count:int = 0
    while os.path.isfile(save_path):
        count += 1
        save_path = "{}_{}ed_{}.pdf".format(filepath[:-4], refain,count)
    
    return save_path


def save_dir(filepath:str):
    path:str = '/'.join(filepath.split('/')[:-1])+r'/images/'
    try:
        os.mkdir(path)
    except:
        pass
    return path


def iter_over_pages(function, doc, pages):
    if not pages:
        for page in doc:
            function(page)
    else:
        for item in pages:
            if isinstance(item, int):
                page = doc[item-1]
                function(page)
            else:
                map(function, doc.pages(start=item[0]-1, stop=item[1]+1))
    

def page_thumbnails(filepath:str, page:int):
    doc = fitz.open(filepath)  # type: ignore

    p = doc[page]
    pix = p.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # type: ignore

    return img


def pages(filepath:str):
    with fitz.open(filepath) as doc:
        return doc.page_count


def to_images(filepath:str, pages=None, zoom=2, *args)-> None:
    dist:str = save_dir(filepath)

    doc = fitz.open(filepath)  # type: ignore
    mat = fitz.Matrix(zoom, zoom)

    def convert_page(page):
        pix = page.get_pixmap(matrix = mat)  # render page to an image
        pix.save(f"{dist}page-{page.number+1}.png")  # store image as a PN
    
    iter_over_pages(convert_page, doc, pages)       

    messagebox.showinfo(title="Success", message=f"the file :\n{filepath}\n conveted avec succss to images in some folder")
    os.startfile(dist)


def crop(filepath:str, top:int, bottom:int, left:int, right:int, pages=None, *args):
    save: str = save_path(filepath, 'crop')

    src = fitz.open(filepath)  # type: ignore

    def crop_page(page):
        page.set_cropbox(page.rect + (left, top, -right, -bottom))

    iter_over_pages(crop_page, src, pages)

    src.save(save)
    messagebox.showinfo(title="Success", message=f"the  file:\n{filepath}\ncroped in some folder")
    os.startfile(save)


def rotate(filepath:str, degree=90, pages=None):
    save: str = save_path(filepath, 'rotated')
    src = fitz.open(filepath)  # type: ignore

    def rotate_page(page):
        page.set_rotation(degree)
        
    iter_over_pages(rotate_page, src, pages)

    src.save(save)
    os.startfile(save)    


def merge(filespath:list[str], *args):

    filepath = filespath.pop(0)
    print(filepath)
    save: str = save_path(filepath, 'merg')

    src = fitz.open(filepath)  # type: ignore

    # todo... map over multi files
    for path in filespath:
        doc = fitz.open(path)   # type: ignore
        src.insert_pdf(doc)

    src.save(save)
    messagebox.showinfo(title="Success", message=f"the  files:\nmerged in some folder")
    os.startfile(save)


def split(filepath:str, list_pages:list, *args, **kwargs):
    save: str = save_path(filepath, 'split')

    src = fitz.open(filepath)  # type: ignore
    doc = fitz.open()  # type: ignore # empty output PDF

    if src.page_count==1:
        print('this file contient one page')

    for p in list_pages:
        if isinstance(p, tuple):
            doc.insert_pdf(src, from_page=p[0]-1, to_page=p[1]-1)
        else:
            doc.insert_pdf(src, from_page=p-1, to_page=p-1)


    doc.save(save)
    messagebox.showinfo(title="Success", message=f"the  file:\n{filepath}\nsplited in some folder")
    os.startfile(save)


def extract_images(filepath:str, pages=None, *args):
    dist:str = save_dir(filepath)

    doc = fitz.open(filepath)  # type: ignore

    def save_image_page(page):
        for image_index, img in enumerate(page.get_images(), start=1):
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            # avoide balck image
            if image.convert("L").getextrema() != (0,0):
                # save it to local disk
                image.save(open(f"{dist}{page.number+1}_{image_index}.{image_ext}", "wb"))

    iter_over_pages(save_image_page, doc, pages)
    messagebox.showinfo(title="Success", message=f"all images from:\n{filepath}\nextracted in some folder")
    os.startfile(dist)




# MCV model to inherit

class Model:
    def __init__(self, parent) -> None:
        """pass parent args if you want to use tkinter variable"""
        self.parent = parent



class Controler(ABC):
  """
  Launch the main part of the GUI and the worker thread. periodic_call()
  and end_application() could reside in the GUI part, but putting them
  here means that you have all the thread controls in a single place.
  """
  def __init__(self, parent, View, Model):
    """
    Start the GUI and the asynchronous threads.  We are in the main
    (original) thread of the application, which will later be used by
    the GUI as well.  We spawn a new thread for the worker (I/O).
    """
    self.parent = parent
    # Create the queue
    self.queue = queue.Queue()

    # Set up the GUI part
    self.model = Model(self.parent) # for normal case remove all args
    self.view = View(self.parent, controler=self, model=self.model,  queue=self.queue)
    self.view.setup(self, self.model)
    # Set up the thread to do asynchronous I/O
    # More threads can also be created and used, if necessary
    self.running = True
    
    # Start the periodic call in the GUI to check the queue
    self.periodic_call()


  def periodic_call(self):
    """ Check every 200 ms if there is something new in the queue. """
    self.parent.after(200, self.periodic_call)
    self.view.processIncoming()
    # if not self.running:
    # #   # This is the brutal stop of the system.  You may want to do
    # #   # some cleanup before actually shutting it down.
  

  def mainloop(self):
    # self.view.setup(self, self.model)
    self.parent.mainloop()


  
  def end_application(self):
    import sys
    self.parent.destroy()
    sys.exit(1)



class View(ABC):


    def __init__(self, parent, controler, model, queue):
        self.parent = parent
        self.queue = queue

        self.controler = controler
        self.model = model
    

    def processIncoming(self):
        """ Handle all messages currently in the queue, if any. """
        while self.queue.qsize():
            try:
                msg = self.queue.get_nowait()
                # Check contents of message and do whatever is needed. As a
                # simple example, let's print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                print(msg)
            except self.queue.Empty:
                # just on general principles, although we don't expect this
                # branch to be taken in this case, ignore this exception!
                pass

    @abstractmethod
    def setup(self, controler, model):
      self.controler = controler
      self.model = model
      # add here ui widgtes...


    def thread(self, target, args=(), kwargs={}):
        """ use this methode for make progress bar update with threading task"""

        thread = threading.Thread(target=target, args=args, kwargs=kwargs)

        # starts thread #
        thread.start()

        # defines indeterminate progress bar (used while thread is alive) #
        # pb1 = ttk.Progressbar(self.parent, orient='horizontal', mode='determinate', maximum=20)

        # checks whether thread is alive #
        while thread.is_alive():
            self.parent.update()
            pass

        # pb1.stop()
        # pb1['value'] = 100

        # self.parent.after(3000, pb1.place_forget)

        # retrieves object from queue #
        # work = self.queue.get()
      
        return #work



# Custom Canvas has rect lignes

class Canvas(tk.Canvas):
    def __init__(self, master, model, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.model = model

        self.height = kwargs.get('height', 400)
        self.width = kwargs.get('width', 294)

        self.config(highlightthickness=0, bd=0, bg='white', width=self.width, height=self.height)

        self.model.top.trace('w', self.on_change_line_top)
        self.model.bottom.trace('w', self.on_change_line_bottom)
        self.model.right.trace('w', self.on_change_line_right)
        self.model.left.trace('w', self.on_change_line_left)

        self._textpreview = self.create_text(self.width//2, self.height//2, text="P R E V I E W", font='bold',fill='gray')


    # def create_line(self)
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

        org_w, org_h = img.width, img.height # memorize origine width
        ratio = org_w/org_h
        self.height = self.width / ratio
        img.thumbnail((self.width , self.height), Image.Resampling.LANCZOS)

        self.model.zoom_thumbnail = org_w / img.width

        self.config(height=self.height)
        # self.height = img.height

        self.cover = ImageTk.PhotoImage(img)
        self.thumbnail = self.create_image(self.width/2, self.height/2, image=self.cover)
        self.tag_lower(self.thumbnail)
        self.tag_lower(self._textpreview)
        self.on_change_line_bottom()
    
    def clean(self):
        self.delete(self.thumbnail)



# just utils function

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
    self.pages = pages(value)


# the real app inherit from <Controller> abstract

class App(Controler):

  def __init__(self, parent, View, Model):
    super().__init__(parent, View, Model)

    self.thread = self.view.thread


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
    img = page_thumbnails(self.model.filepath, page=page-1)
    self.view.canvas.show_image(img)
  



  def split(self):
    if not self.model.filepath or not self.model.selected_for_split.get():
      return
    selected_pages = str_to_list(self.model.selected_for_split.get())
    
    self.thread(split, args=(self.model.filepath, selected_pages))


  def merge(self):
    if len(self.filespath)<2:
      return
    self.thread(merge, args=(self.filespath,))


  def crop(self):
    if not self.model.filepath or not any(self.margins):
      return
    selected_pages = str_to_list(self.model.selected_for_crop.get())
    self.thread(crop, args=(self.model.filepath, *self.margins, selected_pages))


  def convert(self):
    if not self.model.filepath:
      return
    selected_pages = str_to_list(self.model.selected_for_images.get())
    if self.extract_images:
      self.thread(extract_images, args=(self.model.filepath, selected_pages))
    else:
      self.thread(to_images, args=(self.model.filepath, selected_pages, self.zoom_images))


  def rotate(self):
    if not self.model.filepath:
      return
    degree = self.model.rotate.get()
    selected_pges = str_to_list(self.model.selected_for_rotate.get())
    self.thread(merge, args=(self.model.filepath, degree, selected_pges))


# tkinter Gui inherit from <View> abstract

class TabedView(View):


  def setup(self, controler, model):
    super().setup(controler, model)

    self.progressbar = ttk.Progressbar(self.parent, orient='horizontal', mode='determinate', maximum=20)
  
    notebook = ttk.Notebook(self.parent, padding=0)

    notebook.add(self.frame_split(notebook), text="split file")
    notebook.add(self.frame_crop(notebook), text="crop margins")
    notebook.add(self.frame_merge(notebook), text="merge files")
    notebook.add(self.frame_rotate(notebook), text="rotate pages")
    notebook.add(self.frame_image(notebook), text="to images")
    notebook.add(self.frame_about(notebook), text="about")
    
    canvas = Canvas(self.parent, self.controler.model)
  
    notebook.grid(row=0, column=0, sticky='nw')
    canvas.grid(row=0, column=1, rowspan=3, padx=10, pady=10)

    self.notebook = notebook
    self.canvas = canvas

    self.model.selected_for_split.trace('w', self.on_change_entry)
    self.model.selected_for_crop.trace('w', self.on_change_entry)
    self.model.selected_for_rotate.trace('w', self.on_change_entry)
    self.model.selected_for_images.trace('w', self.on_change_entry)


  def frame_about(self, parent):

    _f = ttk.Frame(parent, padding=15)

    ttk.Label(_f, text="App: pdf tools").grid(row=0, column=0, pady=8, sticky='w')
    ttk.Label(_f, text="Discreption: ....").grid(row=1, column=0, pady=8, sticky='w')
    ttk.Label(_f, text="devlopper: youssef HOUMMAD").grid(row=2, column=0, pady=8, sticky='w')
    ttk.Label(_f, text="twitter: @youssefhoummad").grid(row=3, column=0, pady=8, sticky='w')

    return _f


  def frame_split(self, parent):

    _f = ttk.Frame(parent, padding=15)

    ttk.Label(_f, text="select name: ").grid(row=0, column=0, pady=20)
    ttk.Entry(_f, textvariable=self.model._filepath, state='readonly', width=40).grid(row=0, column=1, padx=5)
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
    ttk.Entry(_f, textvariable=self.model._filepath, state='readonly', width=40).grid(row=0, column=1, padx=5)
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
    ttk.Entry(_f, textvariable=self.model._filepath, state='readonly', width=40).grid(row=0, column=1, padx=5)
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
    ttk.Entry(_f, textvariable=self.model._filepath, state='readonly', width=40).grid(row=0, column=1, columnspan=4, padx=5)
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
    tree.bind('<<TreeviewSelect>>', self.on_select_item)

    tree.drop_target_register(DND_ALL)
    tree.dnd_bind("<<Drop>>", self.on_drop_files)

    
    self.tree = tree
    return _f

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


  def move_down(self):
    leaves = self.tree.selection()
    for i in reversed(leaves):
        self.tree.move(i, self.tree.parent(i), self.tree.index(i)+1)


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



def main():

  root = TkinterDnD.Tk() # work with drog and drop

  root.title("Pdf tools")
  root.geometry('872x500')
  # root.iconbitmap(r"icon.ico") # not work with pynsist
  root.resizable(width=False, height=False)

  app = App(root, TabedView, Model)
  style = ttk.Style()
  style.configure('TNotebook.Tab',padding=(8,2)) # tabposition='wn' option to change position of tab


  app.mainloop()

if __name__ == '__main__':
  main()