import time
import tkinter as tk
from tkinter import ttk
from threading import Thread, current_thread

class ThreadedMixin:
    main_thread = current_thread()
    def _forward(self, func, *args, **kwargs):
        if current_thread() != ThreadedMixin.main_thread:
            self.on_main_thread(lambda: func(*args, **kwargs))
        else:
            func(*args, **kwargs)


class Progress(tk.Frame, ThreadedMixin):
  """
  progress indeterminate
  """
  def __init__(self, parent, speed=10, color="red", **kwargs):
    tk.Label.__init__(self, parent, **kwargs)
    self.parent = parent
    # s = ttk.Style()
    # s.theme_use("default")
    # s.configure("TProgressbar", thickness=4, fg="red")
    self.speed = speed
    self.x = 0
    self.direction = 1
    self.width = kwargs.get('width', 2)
    
    # self.label = ttk.Progressbar(self,length=500, mode='indeterminate')
    self.label = tk.Label(self,width=self.width, background=color)
    self.label.place(x=0, y=0)
    # self.label.start()
    t = Thread(target=self.move)
    t.start()
  
  def config(self, *args, **kwargs):
    self._forward(super().config, args, kwargs)

  
  # def callback(self):
  #   self.on_main_thread(self.move)


  def move(self):
    if self.label.winfo_x() > self.parent.winfo_width() - self.label.winfo_width():
      self.direction = -1
    if self.label.winfo_x() < 0:
      self.direction = 1
    

    if self.direction == 1:
      self.x += 5
    else:
      self.x -= 5

    self.label.place(x=self.x, y=0)
    # time.sleep(0.2)
    self.after(self.speed, self.move)
    # self.move()
    
if __name__ == "__main__":

  root = tk.Tk()
  root.geometry("500x100")
  Progress(root).pack(fill=tk.BOTH, expand=tk.YES)
  root.mainloop()


