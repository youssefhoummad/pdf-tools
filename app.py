
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog

import functions as functions
from model import PDFinfo, Model
from tkview import tkView
from mvc import  Controler
from constants import PRIMARY_COLOR


class App(Controler):


  def split(self):
    pdf:PDFinfo = self.model.pdf
    from_page = self.model.start.get()-1
    to_page = self.model.end.get()-1

    if not pdf:
      self.view.flash('error', "Pick pdf first!")
      return
    
    self.view.thread(functions.split, pdf.filepath, from_page, to_page)


  def merge(self):
    pdf1:PDFinfo = self.model.pdf1
    pdf2:PDFinfo = self.model.pdf2
    if not pdf1 or not pdf2:
      self.view.flash('error', "Pick pdf first!")
      return
    self.view.thread(functions.merge, pdf1.filepath, pdf2.filepath)



  def crop(self):
    pdf:PDFinfo = self.model.pdf
    top: int = self.model.top.get()
    left: int = self.model.left.get()
    right: int = self.model.right.get()
    bottom: int = self.model.bottom.get()

    if not pdf:
      self.view.flash('error', "Pick pdf first!")

    
    if top==left==right==bottom==0: return

    self.view.thread(functions.crop, pdf.filepath, top, bottom, left, right)


  def compress(self):
    pdf:PDFinfo = self.model.pdf
    if not pdf:
      self.view.flash('error', "Pick pdf first!")
      return
    
    self.view.thread(functions.compress, pdf.filepath)
    

  def to_images(self):
    pdf:PDFinfo = self.model.pdf
    if not pdf:
      self.view.flash('error', "Pick pdf first!")
      return
      
    if self.model.each_page:
      self.view.thread(functions.to_images, pdf.filepath,)
    else:
      self.view.thread(functions.extract_images, pdf.filepath,)



  def browse(self):
    filepath = filedialog.askopenfilename(title="Choose pdf", filetypes=(('pdf files','*.pdf'),  ("all files","*.*")))
    if filepath:
      pdf = PDFinfo(filepath)
      self.model.pdf = pdf


  def browse2(self):
    filepath = filedialog.askopenfilename(title="Choose pdf", filetypes=(('pdf files','*.pdf'),  ("all files","*.*")))
    if filepath:
      pdf = PDFinfo(filepath)
      self.model.pdf2 = pdf
      self.model.filepath2.set(filepath)





def style_it(root):
   
  root.config(bg=PRIMARY_COLOR)
  ttk.Style().configure('TLabel', background="#FBFCFE", padding=(10,0))
  ttk.Style().configure('TFrame', background=PRIMARY_COLOR)
  ttk.Style().configure('TButton', padding=(0,0))
  ttk.Style().configure('TCheckbutton', background="#FBFCFE", highlightbackground="#FBFCFE")




  
def main():

  root = tk.Tk()
  root.title("Pdf tools")
  root.resizable(width=False, height=False)
  root.geometry("850x600")

  style_it(root)


  app = App(root, tkView, Model)

  app.mainloop()  

if __name__ == '__main__':
  main()

