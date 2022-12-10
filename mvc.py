"""
Tkinter MVC width safe threading


how to use

inherit from class <Controler> and impliment your methode widthout __init__
inherit from class <View> and impliment <setup> method widthout __init__
you can use <Model> or impliment your model class


create a root tkinter or any gui
> root = tk.Tk()

creat an instance from your controler and pass class name for view and model in controler
> app = MyControler(root, MyView, MyModel)

run the app
> app.mainloop()

when you need to call a method from view from controller use:
> self.view.method()

to get data from model 
> self.model.data

to call method from controller use:
> self.controler.method()



NB: if you have a progressbar in your <MyView> you can impliment a methode call <thread>
    copy it from <View> abc and  follow the instructions
    this method for avoid the freezing progressbar
"""

import queue
import threading
from abc import ABC, abstractmethod




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



