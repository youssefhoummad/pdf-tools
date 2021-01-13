import sys
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from PIL import Image, ImageTk

import src.func as func
from src.entry import CustomEntry as Entry
from src.imageLabel import ImageLabel
from src.linkLabel import LinkLabel
from src.traceThread import TraceThread
from src.constant import *
from src.messageBox import Showinfo
from src.progress import Progress


# TODO: fix crop exact 


class AppGUI (tk.Tk):

    def __init__ (self, **kw):
        # super class inits
        tk.Tk.__init__(self)

        self.file1 = tk.StringVar()
        self.file2 = tk.StringVar()
        # vars for SPLIT
        self.start_page = tk.IntVar()
        self.end_page = tk.IntVar()

        #var for CROP
        self.top = tk.IntVar()
        self.bottom = tk.IntVar()
        self.right = tk.IntVar()
        self.left = tk.IntVar()

        self.top.set(0)
        self.bottom.set(0)
        self.right.set(0)
        self.left.set(0)

        self.zoom_x = 1
        self.zoom_y = 1

        self.buttons = [] # this is for disable all button while prog function

        self.init_widget(**kw)
        self.top.trace('w', self.redraw_line)
        self.bottom.trace('w', self.redraw_line)
        self.right.trace('w', self.redraw_line)
        self.left.trace('w', self.redraw_line)
    
    
    def init_widget (self, **kw):
        r"""
            widget's main inits;
        """
        self.title("Pdf tools")
        self.resizable(width=False, height=False)
        self.geometry("500x520")
        self.protocol('WM_DELETE_WINDOW', self.close_app)
        self.iconbitmap(ICON)

        box = ttk.Notebook(self, width=500, height=500)
        self.tab_split = ttk.Frame(self)
        self.tab_merge = ttk.Frame(self)
        self.tab_crop = ttk.Frame(self)
        self.tab_extract_images = ttk.Frame(self)
        self.tab_to_images = ttk.Frame(self)
        self.tab_about = ttk.Frame(self)

        box.add(self.tab_split, text="split pdf")
        box.add(self.tab_merge, text="merge pdfs")
        box.add(self.tab_crop, text="crop pdf")
        box.add(self.tab_to_images, text="pdf to images")
        box.add(self.tab_extract_images, text="exract images")
        box.add(self.tab_about, text="about")

        box.pack(side=tk.TOP, padx=5, pady=5)

        self.init_split_tab()
        self.init_merge_tab()
        self.init_crop_tab()
        self.init_extract_images_tab()
        self.init_to_images_tab()
        self.init_about_tab()

        self.config_widgets()


    def close_app(self):
      try:
        self.thread.kill()
      except :
        pass
      self.destroy()
      sys.exit()


    def config_widgets(self):
      s = ttk.Style()
      s.layout("Tab",
      [('Notebook.tab', {'sticky': 'nswe', 'children':
          [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
              #[('Notebook.focus', {'side': 'top', 'sticky': 'nswe', 'children':
                  [('Notebook.label', {'side': 'top', 'sticky': ''})],
              #})],
          })],
      })]
      )
      s.configure('TNotebook.Tab', padding=[10, 5],background='white')
      s.configure('TFrame',background='white')
      s.configure('TLabel',background='white')
      s.configure('TButton',background='white')

      s.configure('PRIMARY.TButton',background='white', font=(FONT_1, 11, tk.NORMAL))
      # s.map('.', background=[('active', S_COLOR)])
      s.configure('TEntry', selectbackground=P_COLOR, highlightbackground=S_COLOR, highlightcolor=S_COLOR)
      self.canvas.configure( highlightthickness=0, background='white', width=CANVAS_W, height=CANVAS_H)
 

    def init_split_tab(self):

      self.title_label(self.tab_split, text="SPLIT PDF")
      self.browse_frame(self.tab_split)

      _f = ttk.Frame(self.tab_split)
      _f.pack(pady=5)
      ttk.Label(_f, text="from:").grid(row=0, column=0)
      ttk.Label(_f, text="to:").grid(row=0, column=1)
      Entry(_f, textvariable=self.start_page).grid(row=1, column=0, padx=10)
      Entry(_f, textvariable=self.end_page).grid(row=1, column=1, padx=10)

      self.primary_button(self.tab_split, text="split", command=self.split_function)
    

    def init_merge_tab(self):
      self.title_label(self.tab_merge, text="MERGE PDFs")
      self.browse_frame(self.tab_merge)
      self.browse_frame(self.tab_merge, second=True)

      self.primary_button(self.tab_merge, text='merge', command=self.merge_function)


    def init_crop_tab(self):
      self.title_label(self.tab_crop, text="CROP PDF")
      self.browse_frame(self.tab_crop)

      _f = ttk.Frame(self.tab_crop)
      _f.grid_columnconfigure((0, 1, 2), weight=1)
      _f.pack(pady=20)

      self.canvas = tk.Canvas(_f)

      Entry(_f, textvariable=self.top).grid(row=0, column=1)
      Entry(_f, textvariable=self.right).grid(row=1, column=0)
      self.canvas.grid(row=1, column=1, padx=5, pady=5)
      Entry(_f, textvariable=self.left).grid(row=1, column=2)
      Entry(_f, textvariable=self.bottom).grid(row=2, column=1)

      self.primary_button(self.tab_crop, text='crop', command=self.crop_function)


    def init_extract_images_tab(self):
      self.title_label(self.tab_extract_images, text="EXTRACT IMAGE FROM PDF")
      self.browse_frame(self.tab_extract_images)

      self.primary_button(self.tab_extract_images, text='extract', command=self.extract_images_function)
    

    def init_to_images_tab(self):
      self.title_label(self.tab_to_images, text="PDF TO IMAGES")
      self.browse_frame(self.tab_to_images)

      self.primary_button(self.tab_to_images, text='convert', command=self.to_images_function)


    def init_about_tab(self):
      self.title_label(self.tab_about, text="ABOUT")

      ImageLabel(self.tab_about, image_path=ICON).pack()

      ttk.Label(self.tab_about, text="pdf tools by:", font="sans 10 bold").pack()
      ttk.Label(self.tab_about, text="").pack()
      ttk.Label(self.tab_about, text="youssefhoummad").pack()
      LinkLabel(self.tab_about, text="github/youssefhoummad", link="https://github.com/youssefhoummad").pack(pady=3)
      ttk.Label(self.tab_about, text="youssef.hoummad@outlook.com").pack()


    def brows_file1(self):
        file = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
        if file == "": return
        self.file1.set(file)

        @self.disable_btn_while_thread
        def function():
          global CANVAS_H, CANVAS_W
          num_pages = func.get_number_of_pages(file)
          self.start_page.set(1)
          self.end_page.set(num_pages)

          img = func.first_page_to_image(self.file1.get())
          org_w,org_h = img.width, img.height
          img.thumbnail((CANVAS_W , CANVAS_H), Image.ANTIALIAS)
          print('thmbnail size is: ', img.width, img.height)
          self.cover = ImageTk.PhotoImage(img)

          CANVAS_H = img.height
          CANVAS_W = img.width

          self.zoom_x = org_w / img.width
          self.zoom_y = org_h / img.height

          self.canvas.config(width=img.width, height=img.height)

          self.image = self.canvas.create_image(img.width/2, img.height/2, image=self.cover)
          self.canvas.tag_lower(self.image)

          self.line_top = self.canvas.create_line(0, self.top.get(), CANVAS_W, self.top.get(), fill="red")
          self.line_bottom = self.canvas.create_line(0, CANVAS_H-self.bottom.get(), CANVAS_W, CANVAS_H- self.bottom.get(), fill="red")
          self.line_left = self.canvas.create_line(self.left.get(), 0, self.left.get(), CANVAS_H, fill="red")
          self.line_right = self.canvas.create_line(CANVAS_W-self.right.get(), 0, CANVAS_W-self.right.get(), CANVAS_H, fill="red")
          
          self.thread = None



        self.thread = TraceThread(target=function)
        self.thread.start()


    def brows_file2(self):
        file = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
        self.file2.set(file)

    
    def split_function(self):
      # self.btn_split.configure(state="disabled")

      if not self.file1.get():
        Showinfo(self, "PDFs ??", "Need to select pdf file")
        return

      if not self.end_page.get():
        Showinfo(self, "End Page ??", "Last page must be great then 0")
        # self.btn_split.configure(state="normal")
        return

      @self.disable_btn_while_thread
      def function():
        func.split(self.file1.get(), self.start_page.get(), self.end_page.get())
        Showinfo(self, "Nice", "the file splited")


      self.thread = TraceThread(target=function)
      self.thread.start()


    def merge_function(self):
      if not self.file1.get() or not self.file2.get():
        Showinfo(self, "PDFs ??", "Need to select two pdf")
        return
      
      @self.disable_btn_while_thread
      def function():
        func.merge(self.file1.get(), self.file2.get())
        Showinfo(self, "Merged", "two files pdf merged in one")
      


      self.thread = TraceThread(target=function)  
      self.thread.start()


    def crop_function(self):
      from tkinter import messagebox

      if not self.file1.get():
        Showinfo(self, "PDF ??", "Need to select pdf")
        # messagebox.Showinfo('foo', 'bar!', parent=self)
        return
        #TODO

      top = self.top.get() * self.zoom_y
      bottom = self.bottom.get() * self.zoom_x
      right = self.right.get() * self.zoom_x
      left = self.left.get() * self.zoom_y

      @self.disable_btn_while_thread
      def function():
        func.crop(self.file1.get(),top, right, bottom, left)
        Showinfo(self, "GOOD", "pdf file cropded")

      self.proc = TraceThread(target=function)
      self.proc.start()
   

    def extract_images_function(self):
      if not self.file1.get():
        Showinfo(self, "PDF ??", "Need to select  pdf")
        return

      @self.disable_btn_while_thread
      def function():
        func.extract_images(self.file1.get())
        Showinfo(self, "GOOD", "all image exrtacted from pdf")
        self.thread = None

      self.self.thread = TraceThread(target=function)
      self.thread.start()


    def to_images_function(self):
      if not self.file1.get():
        Showinfo(self, "PDF ??", "Need to select  pdf")
        return
  
      @self.disable_btn_while_thread
      def function():
        func.to_images(self.file1.get())
        Showinfo(self, "GOOD", "pdf to jpg completed")

      self.thread = TraceThread(target=function)  
      self.thread.start()
    

    def redraw_line(self, var, indx, mode):
      self.canvas.coords(self.line_top, 0, self.top.get(), CANVAS_W, self.top.get())
      self.canvas.coords(self.line_bottom, 0, CANVAS_H-self.bottom.get(), CANVAS_W, CANVAS_H-self.bottom.get())
      self.canvas.coords(self.line_right,self.right.get(), 0, self.right.get(), CANVAS_H)
      self.canvas.coords(self.line_left,CANVAS_W-self.left.get(), 0,CANVAS_W- self.left.get(), CANVAS_H)


    def title_label(self,parent, text):
      ttk.Label(parent, text=text, font =(FONT, 20, "bold"), foreground=P_COLOR).pack(pady=30)


    def browse_frame(self, parent, second=False):
      textvariable = self.file1 if not second else self.file2
      command = self.brows_file1 if not second else self.brows_file2

      _f = ttk.Frame(parent)
      ttk.Entry(_f, textvariable=textvariable, width=62).grid(padx=5, row=0, column=0)
      ttk.Button(_f, text='browse', command=command).grid(row=0, column=1)
      _f.pack(pady=5, padx=5)
      

    def primary_button(self, parent, text, command):
      self.buttons.append(ttk.Button(parent, text=text, command=command, style="PRIMARY.TButton"))
      self.buttons[-1].pack(pady=(10, 3))
    

    def disable_btn_while_thread(self, callback):
      def function_wrapper(*args, **kwargs):
        for btn in self.buttons:
          btn.configure(state="disabled")
        
        progress = Progress(self, color=P_COLOR, width=6)
        progress.place(x=0, y=0, width=500, height=8)
        
        callback(*args, **kwargs)

        self.thread = None
        progress.place_forget()

        for btn in self.buttons:
          btn.configure(state="normal")
      
      return function_wrapper
      



if __name__ == "__main__":
    AppGUI().mainloop()
