import tkinter as tk


from PIL import Image, ImageTk

class Button1(tk.Label):
  def __init__(self, parent, text, image1, image2=None, image3=None, image4=None, command=None, **kwargs):
    tk.Label.__init__(self, parent, text=text, **kwargs)

    self.command= command

    self.disabeld = False
    
    self._img = Image.open(image1)
    self._img.thumbnail((150 , 70), Image.ANTIALIAS)
    self._img = ImageTk.PhotoImage(self._img)

    self._imgHover = Image.open(image2)
    self._imgHover.thumbnail((150 , 70), Image.ANTIALIAS)
    self._imgHover = ImageTk.PhotoImage(self._imgHover)

    self._imgPress = Image.open(image3)
    self._imgPress.thumbnail((150 , 70), Image.ANTIALIAS)
    self._imgPress = ImageTk.PhotoImage(self._imgPress)

    self._imgDisable = Image.open(image4)
    self._imgDisable.thumbnail((150 , 70), Image.ANTIALIAS)
    self._imgDisable = ImageTk.PhotoImage(self._imgDisable)


    self.config(image=self._img)

    self.config(compound="center", bd=0, fg='white', bg=parent['background'], activeforeground='white',font=('Calibri',12,"bold"))
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
  def __init__(self, parent, text, *args, **kwargs):
    super().__init__(
        parent, text=text, 
        image1=r'img\\button1.png', 
        image2=r'img\\button2.png', 
        image3=r'img\\button3.png',
        image4=r'img\\button4.png',
        *args, **kwargs
        )
    super().on_disable()



if __name__ == "__main__":
  root = tk.Tk()
  b = Button(root, text='click me')
  b.config(state='disabled')

  b.pack(padx=20, pady=20)
  root.mainloop()