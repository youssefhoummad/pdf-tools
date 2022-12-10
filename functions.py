
import os
import io
from tkinter import messagebox

import fitz
from PIL import Image


def save_path(filepath:str ,refain:str):
    save_path:str = "{}_{}ed.pdf".foramt(filepath[:-4], refain)
    if not os.path.isfile(save_path):
        return save_path
    
    count:int = 0
    while os.path.isfile(save_path):
        count += 1
        save_path = "{}_{}ed_{}.pdf".foramt(filepath[:-4], refain,count)
    
    return save_path


def save_dir(filepath:str):
    path:str = '/'.join(filepath.split('/')[:-1])+r'/images/'
    try:
        os.mkdir(path)
    except:
        pass
    return path


def iter_over_pages(function, doc, pages):
    if not pages:
        for page in doc:
            function(page)
    else:
        for item in pages:
            if isinstance(item, int):
                page = doc[item-1]
                function(page)
            else:
                map(function, doc.pages(start=item[0]-1, stop=item[1]+1))
    

def page_thumbnails(filepath:str, page:int):
    doc = fitz.open(filepath)  # type: ignore

    p = doc[page]
    pix = p.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # type: ignore

    return img


def pages(filepath:str):
    with fitz.open(filepath) as doc:
        return doc.page_count


def to_images(filepath:str, pages=None, zoom=2, *args)-> None:
    dist:str = save_dir(filepath)

    doc = fitz.open(filepath)  # type: ignore
    mat = fitz.Matrix(zoom, zoom)

    def convert_page(page):
        pix = page.get_pixmap(matrix = mat)  # render page to an image
        pix.save(f"{dist}page-{page.number+1}.png")  # store image as a PN
    
    iter_over_pages(convert_page, doc, pages)       

    messagebox.showinfo(title="Success", message=f"the file :\n{filepath}\n conveted avec succss to images in some folder")
    os.startfile(dist)


def crop(filepath:str, top:int, bottom:int, left:int, right:int, pages=None, *args):
    save: str = save_path(filepath, 'crop')

    src = fitz.open(filepath)  # type: ignore

    def crop_page(page):
        page.set_cropbox(page.rect + (left, top, -right, -bottom))

    iter_over_pages(crop_page, src, pages)

    src.save(save)
    messagebox.showinfo(title="Success", message=f"the  file:\n{filepath}\ncroped in some folder")
    os.startfile(save)


def rotate(filepath:str, degree=90, pages=None):
    save: str = save_path(filepath, 'rotated')
    src = fitz.open(filepath)  # type: ignore

    def rotate_page(page):
        page.set_rotation(degree)
        
    iter_over_pages(rotate_page, src, pages)

    src.save(save)
    os.startfile(save)    



def merge(filespath:list[str], *args):

    filepath = filespath.pop(0)
    print(filepath)
    save: str = save_path(filepath, 'merg')

    src = fitz.open(filepath)  # type: ignore

    # todo... map over multi files
    for path in filespath:
        doc = fitz.open(path)   # type: ignore
        src.insert_pdf(doc)

    src.save(save)
    messagebox.showinfo(title="Success", message=f"the  files:\nmerged in some folder")
    os.startfile(save)


def split(filepath:str, list_pages:list, *args, **kwargs):
    save: str = save_path(filepath, 'split')

    src = fitz.open(filepath)  # type: ignore
    doc = fitz.open()  # type: ignore # empty output PDF

    if src.page_count==1:
        print('this file contient one page')

    for p in list_pages:
        if isinstance(p, tuple):
            doc.insert_pdf(src, from_page=p[0]-1, to_page=p[1]-1)
        else:
            doc.insert_pdf(src, from_page=p-1, to_page=p-1)


    doc.save(save)
    messagebox.showinfo(title="Success", message=f"the  file:\n{filepath}\nsplited in some folder")
    os.startfile(save)


def extract_images(filepath:str, pages=None, *args):
    dist:str = save_dir(filepath)

    doc = fitz.open(filepath)  # type: ignore

    def save_image_page(page):
        for image_index, img in enumerate(page.get_images(), start=1):
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            # avoide balck image
            if image.convert("L").getextrema() != (0,0):
                # save it to local disk
                image.save(open(f"{dist}{page.number+1}_{image_index}.{image_ext}", "wb"))

    iter_over_pages(save_image_page, doc, pages)
    messagebox.showinfo(title="Success", message=f"all images from:\n{filepath}\nextracted in some folder")
    os.startfile(dist)

