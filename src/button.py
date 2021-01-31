import tkinter as tk


from PIL import Image, ImageTk
from .constant import FONT_MD

class Button1(tk.Label):
  def __init__(self, parent, text, images=[], command=None, size=(150, 70)):
    tk.Label.__init__(self, parent, text=text)

    self.size = size

    self.command= command

    self.disabeld = False

    while len(images) < 4:
      images.append(images[0])
    
    self._img = Image.open(images[0])
    self._img.thumbnail(self.size, Image.ANTIALIAS)
    self._img = ImageTk.PhotoImage(self._img)

    self._imgHover = Image.open(images[1])
    self._imgHover.thumbnail(self.size, Image.ANTIALIAS)
    self._imgHover = ImageTk.PhotoImage(self._imgHover)

    self._imgPress = Image.open(images[2])
    self._imgPress.thumbnail(self.size, Image.ANTIALIAS)
    self._imgPress = ImageTk.PhotoImage(self._imgPress)

    self._imgDisable = Image.open(images[3])
    self._imgDisable.thumbnail(self.size, Image.ANTIALIAS)
    self._imgDisable = ImageTk.PhotoImage(self._imgDisable)


    self.config(image=self._img)

    self.config(compound="center", bd=0, fg='white', bg=parent['background'], activeforeground='white',font=FONT_MD)
    self.config(fg="white")

    self.bind("<Enter>", self.on_enter)
    self.bind("<Leave>", self.on_leave)
    self.bind("<ButtonPress-1>", self.on_press)
    self.bind("<ButtonRelease-1>", self.on_release)



  
  def on_enter(self, event):
    if not self.disabeld:
      self.config(image=self._imgHover)
    

  def on_leave(self, event):
    if not self.disabeld:
      self.config(image=self._img)

  def on_press(self, event):
    if not self.disabeld:
      self.config(image=self._imgPress)

  def on_release(self, event):
    # if self['state']!="disabled":
    if not self.disabeld:
      self.on_enter(event=None)
      if self.command: self.command()
    
  def on_disable(self, event=None):
    self.disabeld = True
    self.config(image=self._imgDisable, fg='gray')

  def on_unable(self, event=None):
    self.disabeld = False
    self.config(image=self._img, fg='white')


class Button(Button1):
  def __init__(self, parent, text, command=None):
    super().__init__(
        parent, text=text, images=[
          r'img\\button1.png', 
          r'img\\button2.png', 
          r'img\\button3.png',
          r'img\\button4.png',
          ], command=command
        )
    super().on_disable()


class ButtonSmall(Button1):
  def __init__(self, parent, text, command=None):
    super().__init__(
        parent, text=text, images=[
          r'img\\btnBase.tif', 
          r'img\\btnHover.tif', 
          r'img\\btnPress.tif',
          r'img\\btnDisable.tif'
          ], command=command, size=(30,30)
        )
    super().on_disable()



if __name__ == "__main__":
  root = tk.Tk()
  b = Button(root, text='click me')
  b.config(state='disabled')

  b.pack(padx=20, pady=20)
  root.mainloop()