import os
import io

import fitz
from PIL import Image



def save_path(filepath:str ,refain:str):
    save_path:str = "{}_{}ed.pdf".format(filepath[:-4], refain)
    if not os.path.isfile(save_path):
        return save_path
    
    count:int = 0
    while os.path.isfile(save_path):
        count += 1
        save_path = "{}_{}ed_{}.pdf".format(filepath[:-4], refain,count)
    
    return save_path


def save_dir(filepath:str):
    path:str = '/'.join(filepath.split('/')[:-1])+r'/images/'
    try:
        os.mkdir(path)
    except:
        pass
    return path


def iter_over_pages(function:callable, doc, pages:list):
    if not pages:
        [function(page) for page in doc]
        return

    for item in pages:
        if isinstance(item, int):
            function(doc[item-1])
        else:
            [function(doc[i]) for i in range(item[0]-1, item[1]-1)]
            # map(function, doc.pages(start=item[0]-1, stop=item[1]+1))
    

def page_thumbnails(filepath:str, page:int):
    doc = fitz.open(filepath)  # type: ignore

    p = doc[page]
    pix = p.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # type: ignore

    return img


def pages(filepath:str):
    with fitz.open(filepath) as doc:
        return doc.page_count


def to_pdf(imagespath:list[str], A4=True):
    save:str = save_path(imagespath[0], 'creat')
    doc = fitz.open()  # type: ignore
    # TODO make all page in some dimension
    
    for imagepath in imagespath:
        img = fitz.open(imagepath)  # open pic as document
        if A4:
            width, height = fitz.paper_size("a4")
            print(width, height)
            rect = fitz.Rect(0, 0, width, height)
        else:
            rect = img[0].rect  # pic dimension
        page = doc.new_page(width = rect.width, height = rect.height)  # pic dimension
        pdfbytes = img.convert_to_pdf()  # make a PDF stream
        img.close()  # no longer needed
        imgPDF = fitz.open("pdf", pdfbytes)  # open stream as PDF
        page.show_pdf_page(rect, imgPDF, 0)  # image fills the page

    doc.save(save)

    return save





def to_images(filepath:str, pages=None, zoom=2, *args)-> None:
    dist:str = save_dir(filepath)

    doc = fitz.open(filepath)  # type: ignore
    mat = fitz.Matrix(zoom, zoom)

    def convert_page(page):
        pix = page.get_pixmap(matrix = mat)  # render page to an image
        pix.save(f"{dist}page-{page.number+1}.png")  # store image as a PN
    
    iter_over_pages(convert_page, doc, pages)       

    return dist


def crop(filepath:str, top:int, bottom:int, left:int, right:int, pages=None, *args):
    save: str = save_path(filepath, 'crop')

    src = fitz.open(filepath)  # type: ignore

    def crop_page(page):
        page.set_cropbox(page.rect + (left, top, -right, -bottom))

    iter_over_pages(crop_page, src, pages)

    src.save(save)

    return save
    

def rotate(filepath:str, degree=90, pages=None):
    save: str = save_path(filepath, 'rotat')
    doc = fitz.open(filepath)  # type: ignore

    def rotate_page(page):
        page.set_rotation(degree)
        
    iter_over_pages(rotate_page, doc, pages)

    doc.save(save)

    return save


def merge(filespath:list[str], *args):

    filepath = filespath.pop(0)
    print(filepath)
    save: str = save_path(filepath, 'merg')

    src = fitz.open(filepath)  # type: ignore

    for path in filespath:
        doc = fitz.open(path)   # type: ignore
        src.insert_pdf(doc)

    src.save(save)

    return save


def split(filepath:str, pages:list, *args, **kwargs):
    save: str = save_path(filepath, 'split')

    src = fitz.open(filepath)  # type: ignore
    doc = fitz.open()  # type: ignore # empty output PDF

    if src.page_count==1:
        print('this file contient one page')
        return
    
    for p in pages:
        if isinstance(p, tuple):
            doc.insert_pdf(src, from_page=p[0]-1, to_page=p[1]-2)
        else:
            doc.insert_pdf(src, from_page=p-1, to_page=p-1)


    doc.save(save)

    return save


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

    return dist


# split(r"C:\Users\youss\Desktop\pdfs\How to Resolve the Python Pyinstaller as False Positive Trojan Virus _ 1.pdf", [(1,3)])