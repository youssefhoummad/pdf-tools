
import os
import io

import fitz
from PIL import Image

from tkinter import messagebox


def save_path(filepath:str ,refain:str)-> str:
    save_path:str = filepath[:-4] +f'__{refain}ed.pdf'
    if not os.path.isfile(save_path):
        return save_path
    
    count:int = 0
    while os.path.isfile(save_path):
        count += 1
        save_path = filepath[:-4] +f'__{refain}ed_{count}.pdf'
    
    return save_path


def save_dir(filepath:str)-> str:
    path = '/'.join(filepath.split('/')[:-1])+'/images/'
    try:
        os.mkdir(path)
    except:
        path = '/'.join(filepath.split('/')[:-1])+'/'
    return path


def to_pdf(imagespath:list[str]):
    dist: str = '/'.join(imagespath[0].split('/')[:-1])
    save = save_path(imagespath[0], 'to_pdf')
    doc = fitz.open()   # type: ignore
    for i, f in enumerate(imagespath):
        img = fitz.open(os.path.join(dist, f))  # type: ignore # open pic as document

        rect = img[0].rect  # pic dimension
        pdfbytes = img.convert_to_pdf()  # make a PDF stream
        img.close()  # no longer needed
        imgPDF = fitz.open("pdf", pdfbytes)  # type: ignore # open stream as PDF
        page = doc.new_page(width = rect.width,  # new page with ...
                        height = rect.height)  # pic dimension
        page.show_pdf_page(rect, imgPDF, 0)  # image fills the page

    doc.save(save)
    messagebox.showinfo(title="Success", message=f"images conveted to one pdf avec succss")



def to_images(filepath:str, *args)-> None:
    dist:str = save_dir(filepath)

    doc = fitz.open(filepath)  # type: ignore # open document
    for page in doc:  # iterate through the pages
        pix = page.get_pixmap()  # render page to an image
        pix.save(f"{dist}page-%i.png" % page.number)  # store image as a PNG
    
    messagebox.showinfo(title="Success", message=f"the file :\n{filepath}\n conveted avec succss to images in some folder")



def crop(filepath:str, top:int, bottom:int, left:int, right:int, *args):
    save: str = save_path(filepath, 'crop')

    src = fitz.open(filepath)  # type: ignore

    for page in src:
        page.set_cropbox(page.rect + (top, bottom, -left, -right))
    
    src.save(save)
    messagebox.showinfo(title="Success", message=f"the  file:\n{filepath}\ncroped in some folder")


def merge(filepath:str, filepath2:str, *args):
    save: str = save_path(filepath, 'merg')

    src = fitz.open(filepath)  # type: ignore
    doc = fitz.open(filepath2)   # type: ignore

    src.insert_pdf(doc)
    src.save(save)
    messagebox.showinfo(title="Success", message=f"the  files:\nmerged in some folder")


 
def split(filepath:str, from_page:int,to_page:int, *args):
    save: str = save_path(filepath, 'split')

    src = fitz.open(filepath)  # type: ignore
    doc = fitz.open()  # type: ignore # empty output PDF

    doc.insert_pdf(src, from_page=from_page, to_page=to_page)
    doc.save(save)
    messagebox.showinfo(title="Success", message=f"the  file:\n{filepath}\nsplited in some folder")



def extract_images(filepath:str, *args):
    dist:str = save_dir(filepath)
    doc = fitz.open(filepath)  # type: ignore

    for page_index in range(len(doc)):
        # get the page itself
        page = doc[page_index]
        image_list = page.getImageList()

        for image_index, img in enumerate(page.getImageList(), start=1):
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = doc.extractImage(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            # save it to local disk
            image.save(open(f"{dist}{page_index+1}_{image_index}.{image_ext}", "wb"))

    messagebox.showinfo(title="Success", message=f"all images from:\n{filepath}\nextracted in some folder")



def compress(filepath:str, *args):

    doc = fitz.open(filepath)  # type: ignore
    save:str = save_path(filepath, 'compress')
    doc.save(save,
            garbage=3,  # eliminate duplicate objects
            deflate=True,  # compress stuff where possible
    )
    messagebox.showinfo(title="Success", message=f"the  file:\n{filepath}\ncompressed in some folder")


