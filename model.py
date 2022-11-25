
import os
import tkinter as tk

from PyPDF2 import PdfFileReader


class PDFinfo:
    def __init__(self, filepath) -> None:
        self._filepath = filepath
    

    @property
    def pages(self) -> int:
        with open(self._filepath, 'rb') as in_pdf:
            pdf_handler = PdfFileReader(in_pdf)
            return pdf_handler.getNumPages()
    
    
    @property
    def filesize(self) -> str:
        size_in_bytes = os.path.getsize(self._filepath)
        return str(f"{round(size_in_bytes/1024/1024,2)} mb")
    
    @property
    def filepath(self):
        return r"{}".format(self._filepath)
    

    @property
    def basename(self):
        return os.path.basename(self._filepath)


    @property
    def filename(self) -> str:
        max_length = 30
        concat_filename = f'{self.basename[0:max_length]}'
        if len(self.basename) > max_length:
            concat_filename += '…'
        return str(concat_filename)
    

    def __bool__(self):
        return True if self._filepath else False
    


class Model:
    def __init__(self, parent) -> None:
        self.parent = parent

        self._pdf1 = None
        self._pdf2 = None


        self.filename = tk.StringVar(parent, name='filename')
        self.filesize = tk.StringVar(parent, name='filesize')
        self.pages = tk.IntVar(parent, value=0, name='pages')

        self.filepath2 = tk.StringVar(parent, name='filepath2')

        self.start =tk.IntVar(parent, name='start', value=1)
        self.end =tk.IntVar(parent, name='end')

        self.top =tk.IntVar(parent, name='top')
        self.bottom =tk.IntVar(parent, name='bottom')
        self.left =tk.IntVar(parent, name='left')
        self.right =tk.IntVar(parent, name='right')

        self.each_page = tk.BooleanVar(parent, name="each_page") 

        self.message_flash = tk.StringVar(parent, name="message_name")

    @property
    def pdf(self):
        return self._pdf1
    
    @pdf.setter
    def pdf(self, value):
        self._pdf1 = value

        self.filename.set(value.filename)
        self.filesize.set(value.filesize)
        self.pages.set(value.pages)
        self.end.set(value.pages)
    
    pdf1 = pdf
    
    @property
    def pdf2(self):
        return self._pdf2
    
    @pdf2.setter
    def pdf2(self, value):
        self._pdf2 = value
        self.filepath2.set(value.filepath)



    
        