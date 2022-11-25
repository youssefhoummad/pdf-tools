
import os

from PyPDF2 import PdfReader, PdfWriter, PdfFileMerger, PdfFileReader, PdfFileWriter

from tkinter import messagebox


def save_path(filepath:str ,func:str)-> str: 
    save_path:str = filepath[:-4] +f'__{func}ed.pdf'
    if not os.path.isfile(save_path):
        return save_path
    
    count:int = 0
    while os.path.isfile(save_path):
        count += 1
        save_path = filepath[:-4] +f'__{func}ed_{count}.pdf'
    
    return save_path


def save_dir(filepath:str)-> str:
    ...



def to_images(filepath:str, *args)-> None:
    print(filepath)


def crop(filepath:str, top:int, bottom:int, left:int, right:int, *args):
    save: str = save_path(filepath, 'crop')

    with open(filepath, "rb") as in_f:
        input1 = PdfFileReader(in_f)
        output = PdfFileWriter()


        for page in input1.pages:
            page.mediaBox.upperRight = (page.mediaBox.getUpperRight_x() - right, page.mediaBox.getUpperRight_y() - top)
            page.mediaBox.lowerLeft  = (page.mediaBox.getLowerLeft_x()  + left,  page.mediaBox.getLowerLeft_y()  + bottom)
            output.addPage(page)    

        with open(save, "wb") as out_f:
            output.write(out_f)
    messagebox.showinfo(title="Success", message=f"the file :\n{filepath}\n croped avec succss in some folder")  # type: ignore



def merge(filepath:str, filepath2:str, *args):
    save: str = save_path(filepath, 'merg')

    merger = PdfFileMerger()
    merger.append(fileobj=open(filepath, 'rb'))
    merger.append(fileobj=open(filepath2, 'rb'))
    
    with open(save, 'wb') as out_pdf:
        merger.write(out_pdf)
    messagebox.showinfo(title="Success", message=f"the files merged avec succss in some folder")  # type: ignore


 
def split(filepath:str, page_range, *args):
    save: str = save_path(filepath, 'split')

    with open(filepath, 'rb') as in_pdf:
        reader = PdfFileReader(in_pdf)
        writer = PdfFileWriter()

        if type(page_range)==int:
            writer.addPage(reader.getPage(page_range))
        else:
            [writer.addPage(reader.getPage(p)) for p in page_range]

        with open(save, 'wb') as outfile:
            writer.write(outfile)
    
    messagebox.showinfo(title="Success", message=f"the file :\n{filepath}\n splited avec succss in some folder")  # type: ignore


def extract_images(filepath:str, *args):
    reader = PdfReader(filepath)
    count:int = 0

    for page in reader.pages:
        for image_file_object in page.images:
            with open(str(count) + image_file_object.name, "wb") as fp:
                fp.write(image_file_object.data)
                count += 1
    print('extracting...')
    

    # !! save path 

def compress(filepath:str, remove_image:bool=False, *args):
    save:str = save_path(filepath, 'compress')

    reader = PdfReader(filepath)
    writer = PdfWriter()
    
    if remove_image:
        writer.remove_images() # remove all image
    
    # [page.compress_content_streams() for page in reader.pages ]
    map(lambda p: p.compress_content_streams, reader.pages)
    map(lambda p: p.writer.add_page, reader.pages)
    # [writer.add_page(page) for page in reader.pages ]
    
    writer.add_metadata(reader.metadata) 

    with open(save, "wb") as fp:
        writer.write(fp)
    
    messagebox.showinfo(title="Success", message=f"the file :\n{filepath}\n compressed avec succss in some folder")  # type: ignore

