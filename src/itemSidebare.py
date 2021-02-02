from tkinter import Frame, Label
from .imageLabel import ImageLabel
from .constant import *



class ItemSidebare(Frame):
  def __init__(self, parent, text, icon=None, command=None):
    super().__init__(parent)

    self.active = False

    self.text = text
    self.command= command


    self._bg = '#F2F2F2'
    self._bgHover = '#DEDEDE'
    self._bgPress = '#CFCFCF'

    self.config(bg=self._bg)

    self.border = Frame(self, bg=self._bg, width=4, height=24)

    if icon:
      self.imageLabel = ImageLabel(self, image_path=icon, bg=self._bg,  width=28, height=28)

    self.textLabel = Label(self, text=text, bg=self._bg, font=('Calibri',12,"bold"))
    
    self.border.pack(side=START_DIR)
    if icon:
      self.imageLabel.pack(side=START_DIR, pady=8, padx=START_PADDING_24)
    self.textLabel.pack(side=START_DIR, padx=END_PADDING_10)

    if not icon: 
      self.imageLabel.pack(padx=0)
      self.textLabel.pack(padx=START_PADDING_24)


    self.bind("<ButtonPress-1>", self.on_press)
    self.bind("<ButtonRelease-1>", self.on_release)
    self.bind("<Enter>", self.on_hover)
    self.bind("<Leave>", self.on_leave)

    self.textLabel.bind("<ButtonPress-1>", self.on_press)
    self.textLabel.bind("<ButtonRelease-1>", self.on_release)
    self.textLabel.bind("<Enter>", self.on_hover)
    self.textLabel.bind("<Leave>", self.on_leave)

    self.imageLabel.bind("<ButtonPress-1>", self.on_press)
    self.imageLabel.bind("<ButtonRelease-1>", self.on_release)
    self.imageLabel.bind("<Enter>", self.on_hover)
    self.imageLabel.bind("<Leave>", self.on_leave)
  
  def on_hover(self, e):
    self.config(bg=self._bgHover)
    self.textLabel.config(bg=self._bgHover)
    self.imageLabel.config(bg=self._bgHover)
    if not self.active:
      self.border.config(bg=self._bgHover)
  
  def on_press(self, e):
    self.config(bg=self._bgPress)
    self.textLabel.config(bg=self._bgPress)
    self.imageLabel.config(bg=self._bgPress)
    if not self.active:
      self.border.config(bg=self._bgPress)

  def on_leave(self, e):
    self.config(bg=self._bg)
    self.textLabel.config(bg=self._bg)
    self.imageLabel.config(bg=self._bg)
    if not self.active:
      self.border.config(bg=self._bg)

  def on_release(self, e):
    self.on_hover(e=None)
    self.command()

  def on_active(self):
    self.active = True
    self.border.config(bg='#FF9F43')

  def on_disactive(self):
    self.active = False
    self.border.config(bg=self._bg)

