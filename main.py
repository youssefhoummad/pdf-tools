import tkinter as tk, queue, os, subprocess
import fitz

from gui import AppGui
from src.win10toast import ToastNotifier
from src.utils import threaded
from src.constant import *
from src import func


toaster = ToastNotifier()

class ThreadedApp(object):
  """
  Launch the main part of the GUI and the worker thread. periodic_call()
  and end_application() could reside in the GUI part, but putting them
  here means that you have all the thread controls in a single place.
  """
  def __init__(self, master):
    """
    Start the GUI and the asynchronous threads.  We are in the main
    (original) thread of the application, which will later be used by
    the GUI as well.  We spawn a new thread for the worker (I/O).
    """
    self.master = master
    # Create the queue
    self.queue = queue.Queue()

    # Set up the GUI part
    self.gui = AppGui(master, self.queue, self.split, self.merge, self.crop, self.extract, self.to_pdf, self.init_doc)
    self.gui.pack(expand=True, fill='both', side=START_DIR)
    # Set up the thread to do asynchronous I/O
    # More threads can also be created and used, if necessary
    # self.running = True
    
    # Start the periodic call in the GUI to check the queue
    self.periodic_call()


  def periodic_call(self):
    """ Check every 200 ms if there is something new in the queue. """
    self.master.after(200, self.periodic_call)
    self.gui.processIncoming()
    # if not self.running:
    #   # This is the brutal stop of the system.  You may want to do
    #   # some cleanup before actually shutting it down.
    #   import sys
    #   self.master.destroy()
    #   sys.exit(1)


  def init_doc(self):
    return fitz.open(self.gui.file_path.get())


  @threaded
  def split(self):

    file = self.gui.file_path.get()
    pages_range = [self.gui.start_page, self.gui.end_page]
    pages_range = [item.get() for item in pages_range]

    # if entry has no value or string so is 1
    pages_range = [int(item) if item.isdigit() else 1 for item in pages_range]

    @self.sanirize
    def do_split(*args):
      func.split(*args)
    
    do_split(file, *pages_range)


  @threaded
  def merge(self):
    
    file1 = self.gui.file_path.get()
    file2 = self.gui.file_path2.get()

    if not file2: return

    @self.sanirize
    def do_merge(*args):
      func.merge(*args)

    do_merge(file1, file2)


  @threaded
  def crop(self):

    file = self.gui.file_path.get()
    # if settings.get('DIR') == 'rtl':
    
    margins = [self.gui.top, self.gui.right, self.gui.bottom, self.gui.left ]
    margins = [item.get() for item in margins]
    # if entry has no value or string so is 0
    margins = [int(item) if item.isdigit() else 0 for item in margins]

    # multi marging * zoom
    margins = [marg*self.gui.zoom for marg in margins]
    
    # no margin croped
    if sum(margins) < 1: return

    @self.sanirize
    def do_crop(*args):
      func.crop(*args)

    do_crop(file, *margins)


  @threaded
  def extract(self):
    
    file = self.gui.file_path.get()

    @self.sanirize
    def do_extract(*args):
      func.extract(*args)
    
    @self.sanirize
    def do_to_images(*args):
      func.to_images(*args)
    
    if self.gui.to_single_pages.get():
      do_to_images(self.gui.doc, file)
    else:
      do_extract(file)


  @threaded
  def to_pdf(self):
    
    images = self.gui.files_path.get()
    # convert String to List
    images = list(images[1:-2].replace("'", "").split(', '))

    @self.sanirize
    def convert_to_pdf(*args):
      func.to_pdf(*args)

    convert_to_pdf(*images)


  def sanirize(self, callback):
    """ Disable buttons and show loading spring while process not completed
        and show notificatio after process succefully.
    """
    def function_wrapper(*args, **kwargs):

      if not args[0]: return # if no pdf selected

      self.gui.disable_btn_show_loading()

      callback(*args, **kwargs)
      
      self.gui.unable_btn_hide_loading()

      self.show_notify()

    return function_wrapper


  def show_notify(self):
    # show system notification 
    msg = settings.get('last_func')
    path = settings.get('last_file')

    toaster.show_toast(
      PROCESS_COMPLETE,
      str(path),
      icon_path=r'img\\icon.ico',
      callback_on_click= self.open_path,
      duration=10,
      threaded=True
        )


  def open_path(self):
    "open path on windows explore"
    path = settings.get('last_file')

    if os.path.isfile(path):
      subprocess.Popen(r'explorer /select,"{}"'.format(path))
    elif os.path.isdir(path):
      os.startfile(path)
    else:
      print('Oops!')


  def end_application(self):
    import sys
    self.master.destroy()
    sys.exit(1)



if __name__ == '__main__':


  root = tk.Tk()
  root.title("Pdf tools")
  root.resizable(width=False, height=False)
  root.geometry("750x520")
  root.iconbitmap(r'img\\icon.ico')
  # root.attributes('-transparentcolor', 'white')

  App = ThreadedApp(root)

  root.mainloop()
