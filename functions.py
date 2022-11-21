
import os
import io

import fitz
from PIL import Image


def save_path(filepath:str ,refain:str)-> str:
    # new_name = filepath[:-4] + f"{refain}.pdf"
    # i = 1
    # while os.path.isfile(new_name):
    #     new_name = filepath[:-4] + f"{refain}_{i}.pdf"
    #     i +=1
    # # new_name = makeSafeFilename(new_name)
    # # print(new_name)
    # new_name = os.path.realpath(new_name)
    # return  new_name


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
    doc = fitz.open()
    for i, f in enumerate(imagespath):
        img = fitz.open(os.path.join(dist, f))  # open pic as document

        rect = img[0].rect  # pic dimension
        pdfbytes = img.convert_to_pdf()  # make a PDF stream
        img.close()  # no longer needed
        imgPDF = fitz.open("pdf", pdfbytes)  # open stream as PDF
        page = doc.new_page(width = rect.width,  # new page with ...
                        height = rect.height)  # pic dimension
        page.show_pdf_page(rect, imgPDF, 0)  # image fills the page

    doc.save(save)


def to_images(filepath:str, *args)-> None:
    dist:str = save_dir(filepath)

    doc = fitz.open(filepath)  # open document
    for page in doc:  # iterate through the pages
        pix = page.get_pixmap()  # render page to an image
        pix.save(f"{dist}page-%i.png" % page.number)  # store image as a PNG



def crop(filepath:str, top:int, bottom:int, left:int, right:int, *args):
    save: str = save_path(filepath, 'crop')

    # with open(filepath, "rb") as in_f:
    #     input1 = PdfFileReader(in_f)
    #     output = PdfFileWriter()


    #     for page in input1.pages:
    #         page.mediaBox.upperRight = (page.mediaBox.getUpperRight_x() - right, page.mediaBox.getUpperRight_y() - top)
    #         page.mediaBox.lowerLeft  = (page.mediaBox.getLowerLeft_x()  + left,  page.mediaBox.getLowerLeft_y()  + bottom)
    #         output.addPage(page)    

    #     with open(save, "wb") as out_f:
    #         output.write(out_f)


def merge(filepath:str, filepath2:str, *args):
    save: str = save_path(filepath, 'merg')

    src = fitz.open(filepath)
    doc = fitz.open(filepath2) 

    src.insert_pdf(doc)
    src.save(save)

 
def split(filepath:str, from_page:int,to_page:int, *args):
    save: str = save_path(filepath, 'split')

    src = fitz.open(filepath)
    doc = fitz.open()  # empty output PDF

    doc.insert_pdf(src, from_page=from_page, to_page=to_page)
    doc.save(save)


def extract_images(filepath:str, *args):
    dist:str = save_dir(filepath)
    doc = fitz.open(filepath)

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


def compress(filepath:str, *args):

    doc = fitz.open(filepath)
    save:str = save_path(filepath, 'compress')
    doc.save(save,
            garbage=3,  # eliminate duplicate objects
            deflate=True,  # compress stuff where possible
    )
