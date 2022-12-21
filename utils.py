import threading
import queue
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod

from PIL import Image, ImageTk




class ThreadWithResult(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)

        super().__init__(group=group, target=function, name=name, daemon=daemon)

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
    # threading.Thread(target=self.view.setup, args=(self, self.model))
    self.view.setup(self, self.model)
    # Set up the thread to do asynchronous I/O
    # More threads can also be created and used, if necessary
    self.running = True
    
    # Start the periodic call in the GUI to check the queue
    self.periodic_call()


  def thread(self, target, args=(), kwargs={}):
    """ use this methode for make progress bar update with threading task"""
    thread = ThreadWithResult(target=target, args=args, kwargs=kwargs)

    thread.log_thread_status = False

    thread.start()
    thread.join()

    # defines indeterminate progress bar (used while thread is alive) #
    # pb1 = ttk.Progressbar(self.parent, orient='horizontal', mode='determinate', maximum=20)

    # checks whether thread is alive #
    while thread.is_alive():
        self.parent.update()
        pass
    
    print(thread.result) # result of thred

    # pb1.stop()
    # pb1['value'] = 100

    # self.parent.after(3000, pb1.place_forget)

    # retrieves object from queue #
    # work = self.queue.get()
  
    return #work
  

 

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

  def reload(self):
    for w in self.parent.winfo_children():
      w.destroy()

    self.view.setup(self, self.model)
  


  
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






# Custom Canvas has rect lignes

class Canvas(tk.Canvas):
    def __init__(self, master, model, text_preview="P R E V I E W", *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.model = model

        self.height = kwargs.get('height', 400)
        self.width = kwargs.get('width', 294)

        self.config(highlightthickness=0, bd=0, bg='white', width=self.width, height=self.height)

        self.model.top.trace('w', self.on_change_line_top)
        self.model.bottom.trace('w', self.on_change_line_bottom)
        self.model.right.trace('w', self.on_change_line_right)
        self.model.left.trace('w', self.on_change_line_left)

        self._textpreview = self.create_text(self.width//2, self.height//2, text=text_preview, font='bold',fill='gray')


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



class Entry(ttk.Entry):

    def __init__(self, master, textvariable, *args, **kwargs):

        self.last_valid_value = ""
        self.text = textvariable
   
        super().__init__(master, *args, textvariable=self.text, **kwargs)

        self.vcmd = self.register(self.validate)
        self.ivcmd = self.register(self.invalidate)
        self['validate'] = 'key'
        self['validatecommand'] = self.vcmd, '%P',
        self['invalidcommand'] = self.ivcmd,

    def validate(self, inp):
        for char in inp:
          if char not in '0123456789,-':
            return False
        self.last_valid_value = inp
        return True

    def invalidate(self):
        self.text.set(self.last_valid_value)

    def get(self):
      result = []
      for item in super().get().split(","):
        if '-' in item:
          x, y = item.split('-')
          result.append((int(x), int(y)+1))
        else:
          if item:
            result.append(int(item))
      return result

    def get_last(self):
      if not self.get():
        return None
      last = self.get()[-1]
      if isinstance(last, tuple):
        return last[-1]
      return last




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

