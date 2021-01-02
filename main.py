import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import os
import sys

from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger



def get_number_of_pages(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f, strict=False)
        number_of_pages = pdf.getNumPages()
        # print(number_of_pages)
        return number_of_pages


def split(pdf_file, start_page, end_page):
    start_page, end_page = int(start_page), int(end_page)
    input_pdf = PdfFileReader(open(pdf_file, 'rb'), strict=False)
    output_pdf = PdfFileWriter()
    # name it
    new_name = rename_file(pdf_file, '_splited')
    # creat blank file
    new_file = open(new_name, 'wb')
    # insert pages in blank file
    while start_page <= end_page:
        output_pdf.addPage(input_pdf.getPage(start_page))
        output_pdf.write(new_file)
        start_page += 1
    # close it
    new_file.close()


def merge(pdf_file1, pdf_file2):
    pdf_merger = PdfFileMerger(strict=False)
    pdf_merger.append(pdf_file1)
    pdf_merger.append(pdf_file2)

    new_file = rename_file(pdf_file1, '_merged')
    with open(new_file, 'wb') as fileobj:
        pdf_merger.write(fileobj)


def crop(pdf_file, top, right, bottom, left):
    input_pdf = PdfFileReader(open(pdf_file, 'rb'),strict=False)
    output_pdf = PdfFileWriter()
    top, right, bottom, left = int(top), int(right), int(bottom), int(left)

    new_name = rename_file(pdf_file, '_croped')
    new_file = open(new_name, 'wb')

    num_pages = input_pdf.getNumPages()

    for i in range(num_pages):
        page = input_pdf.getPage(i)

        page.mediaBox.upperRight = (page.mediaBox.getUpperRight_x() - right, page.mediaBox.getUpperRight_y() - top)
        page.mediaBox.lowerLeft  = (page.mediaBox.getLowerLeft_x()  + left,  page.mediaBox.getLowerLeft_y()  + bottom)

        output_pdf.addPage(page)
        output_pdf.write(new_file)
    
    new_file.close()


def extract_images(pdf_file):
    with open(pdf_file,"rb") as file:
        file.seek(0)
        pdf = file.read()

    path = '/'.join(pdf_file.split('/')[:-1])+'/images_extracted/'
    try:
        os.mkdir(path)
    except:
        path = '/'.join(pdf_file.split('/')[:-1])+'/'

    startmark = b"\xff\xd8"
    startfix = 0
    endmark = b"\xff\xd9"
    endfix = 2
    i = 0

    njpg = 0
    while True:
        istream = pdf.find(b"stream", i)
        if istream < 0:
            break
        istart = pdf.find(startmark, istream, istream + 20)
        if istart < 0:
            i = istream + 20
            continue
        iend = pdf.find(b"endstream", istart)
        if iend < 0:
            raise Exception("Didn't find end of stream!")
        iend = pdf.find(endmark, iend - 20)
        if iend < 0:
            raise Exception("Didn't find end of JPG!")

        istart += startfix
        iend += endfix
        # print("JPG %d from %d to %d" % (njpg, istart, iend))
        jpg = pdf[istart:iend]
        with open(path + "jpg%d.jpg" % njpg, "wb") as jpgfile:
            jpgfile.write(jpg)

        njpg += 1
        i = iend


def rename_file(pdf_file, refrain):
    """ return new name width _splited
        >>> rename_file(file.pdf, "_splited") -> file_splited.pdf
        if file_splited.pdf existe -> file_splited_1.pdf
        ....
    """
    new_name = pdf_file[:-4] + f"{refrain}.pdf"
    i = 1
    while os.path.isfile(new_name):
        new_name = pdf_file[:-4] + f"{refrain}_{i}.pdf"
        i +=1
    return new_name




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

        # widget inits
        self.init_widget(**kw)
    

    def init_widget (self, **kw):
        r"""
            widget's main inits;
        """
        # main window inits
        self.title("Pdf tools")
        self.resizable(width=False, height=False)
        self.geometry("400x300")
        self.iconbitmap(r"C:\Users\youssef\AppData\Local\Programs\Python\Python37\DLLs\icon.ico")
        # look'n'fell
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
        s.configure('Custom.TNotebook.Tab', padding=[10, 5])
        s.configure(self ,background='white')
        # inits
        box = ttk.Notebook(self, width=400, height=300, style='Custom.TNotebook')
        s.configure(box ,background='white')

        self.tab_split = ttk.Frame(self)
        self.tab_merge = ttk.Frame(self)
        self.tab_crop = ttk.Frame(self)
        self.tab_images = ttk.Frame(self)
        self.tab_about = ttk.Frame(self)

        box.add(self.tab_split, text="split pdf")
        box.add(self.tab_merge, text="merge pdfs")
        box.add(self.tab_crop, text="crop pdf")
        box.add(self.tab_images, text="exract images")
        box.add(self.tab_about, text="about")

        box.pack(side=tk.TOP, padx=5, pady=5)

        self.init_split_tab()
        self.init_merge_tab()
        self.init_crop_tab()
        self.init_images_tab()
        self.init_about_tab()


    def init_split_tab(self):
      ttk.Label(self.tab_split, text="SPLIT PDF", font = "sans 16 bold", foreground="#6200EA").grid(row=0, column=0, columnspan=2, pady=30)
      
      ttk.Entry(self.tab_split,state=tk.DISABLED, textvariable=self.file1, width=48).grid(padx=5, row=1, column=0)
      ttk.Button(self.tab_split, text='browse', command=self.brows_file1).grid(row=1, column=1)
      
      _f = ttk.Frame(self.tab_split)
      _f.grid(row=2, columnspan=2, pady=20)
      ttk.Label(_f, text="from:").grid(row=0, column=0)
      ttk.Entry(_f, textvariable=self.start_page).grid(row=0, column=1, padx=10)
      ttk.Label(_f, text="to:").grid(row=0, column=2)
      ttk.Entry(_f, textvariable=self.end_page).grid(row=0, column=3, padx=10)

      ttk.Button(self.tab_split, text='split', command=self.split_function).grid(row=3, columnspan=2, pady=30)

    
    def init_merge_tab(self):
      ttk.Label(self.tab_merge, text="MERGE PDFs", font = "sans 16 bold", foreground="#6200EA").grid(row=0, column=0, columnspan=2, pady=30)
      
      ttk.Entry(self.tab_merge,state=tk.DISABLED, textvariable=self.file1, width=48).grid(padx=5, row=1, column=0)
      ttk.Button(self.tab_merge, text='browse', command=self.brows_file1).grid(row=1, column=1)
      
      ttk.Entry(self.tab_merge,state=tk.DISABLED, textvariable=self.file2, width=48).grid(padx=5, row=2, column=0)
      ttk.Button(self.tab_merge, text='browse', command=self.brows_file2).grid(row=2, column=1)
      
      ttk.Button(self.tab_merge, text='merge', command=self.merge_function).grid(row=3, columnspan=2, pady=30)


    def init_crop_tab(self):
      ttk.Label(self.tab_crop, text="CROP PDF", font = "sans 16 bold", foreground="#6200EA").grid(row=0, column=0, columnspan=2, pady=30)
      
      ttk.Entry(self.tab_crop,state=tk.DISABLED, textvariable=self.file1, width=48).grid(row=1, column=0, padx=5)
      ttk.Button(self.tab_crop, text='browse', command=self.brows_file1).grid(row=1, column=1)
      
      _f = ttk.Frame(self.tab_crop)
      _f.grid(row=2, columnspan=2, pady=20)
      ttk.Label(_f, text="top:").grid(row=0, column=0)
      ttk.Entry(_f, textvariable=self.top).grid(row=0, column=1, padx=10)
      ttk.Label(_f, text="bottom:").grid(row=0, column=2)
      ttk.Entry(_f, textvariable=self.bottom).grid(row=0, column=3, padx=10)
      ttk.Label(_f, text="right:").grid(pady=10,row=1, column=0)
      ttk.Entry(_f, textvariable=self.right).grid(row=1, column=1, padx=10)
      ttk.Label(_f, text="left:").grid(row=1, column=2)
      ttk.Entry(_f, textvariable=self.left).grid(row=1, column=3, padx=10)

      ttk.Button(self.tab_crop, text='crop', command=self.crop_function).grid(row=3, columnspan=2)


    def init_images_tab(self):
      ttk.Label(self.tab_images, text="EXTRACT IMAGES", font = "sans 16 bold", foreground="#6200EA").grid(row=0, column=0, columnspan=2, pady=30)
      
      ttk.Entry(self.tab_images,state=tk.DISABLED, textvariable=self.file1, width=48).grid(padx=5, row=1, column=0)
      ttk.Button(self.tab_images, text='browse', command=self.brows_file1).grid(row=1, column=1)
      
      ttk.Button(self.tab_images, text='images', command=self.images_function).grid(row=3, columnspan=2, pady=30)
    
    
    def init_about_tab(self):
      ttk.Label(self.tab_about, text="ABOUT", font = "sans 16 bold", foreground="#6200EA").pack(pady=30)
      ttk.Label(self.tab_about, text="pdf tools by:", font="sans 10 bold").pack()
      ttk.Label(self.tab_about, text="").pack()
      ttk.Label(self.tab_about, text="@youssefhoummad").pack()
      ttk.Label(self.tab_about, text="www.github/youssefhoummad", foreground="blue").pack(pady=2)
      ttk.Label(self.tab_about, text="youssef.hoummad@outlook.com").pack()


    def brows_file1(self):
        file = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
        self.file1.set(file)
        num_pages = get_number_of_pages(file)
        self.start_page.set(1)
        self.end_page.set(num_pages)


    def brows_file2(self):
        file = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
        self.file2.set(file)

    
    def split_function(self):
      if not self.file1.get():
        self.showinfo("PDFs ??", "Need to select pdf file")
        return

      if not self.end_page.get():
        self.showinfo("End Page ??", "Last page must be great then 0")
        return
      split(self.file1.get(), self.start_page.get(), self.end_page.get())
      self.showinfo("Nice", "the file splited")
      # print("splited...")


    def merge_function(self):
      if not self.file1.get() or not self.file2.get():
        self.showinfo("PDFs ??", "Need to select two pdf")
        return
      merge(self.file1.get(), self.file2.get())
      self.showinfo("Merged", "two files pdf merged in one")
      # print("merged...")


    def crop_function(self):
      if not self.file1.get():
        self.showinfo("PDF ??", "Need to select pdf")
        return
      crop(self.file1.get(), self.top.get()*10, self.right.get()*10, self.bottom.get()*10, self.left.get()*10)
      self.showinfo("GOOD", "pdf file cropded")

      # print("croped...")


    def images_function(self):
      if not self.file1.get():
        self.showinfo("PDF ??", "Need to select  pdf")
        return
      extract_images(self.file1.get())
      self.showinfo("GOOD", "all image exrtacted from pdf")
      # print("images...")

    def showinfo(self, title, message):
      top = tk.Toplevel(self)
      top.details_expanded = False
      top.title(title)
      top.geometry("400x100+{}+{}".format(self.winfo_x(), self.winfo_y()))
      top.resizable(False, False)
      top.rowconfigure(0, weight=0)
      top.rowconfigure(1, weight=1)
      top.columnconfigure(0, weight=1)
      top.columnconfigure(1, weight=1)
      tk.Label(top, image="::tk::icons::information").grid(row=0, column=0, pady=(7, 0), padx=(7, 7), sticky="e")
      tk.Label(top, text=message).grid(row=0, column=1, columnspan=2, pady=(7, 7), sticky="w")
      ttk.Button(top, text="OK", command=top.destroy).grid(row=1, column=2, padx=(7, 7), sticky="e")


        
        



# end class AppGUI


if __name__ == "__main__":
    AppGUI().mainloop()
