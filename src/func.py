import os
import io
import string
import tempfile

from PIL import Image, ImageOps
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from PyPDF2.generic import FloatObject

import fitz
try:
    from .constant import *
except:
    from constant import *

def makeSafeFilename(inputFilename):
    # Set here the valid chars
    safechars = string.printable
    try:
        r = list(filter(lambda c: c in safechars, inputFilename))
        return r
    except:
        return ""
    pass 



def get_number_of_pages(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f, strict=False)
        number_of_pages = pdf.getNumPages()
        # print(number_of_pages)
        return number_of_pages


def split(pdf_file, start_page, end_page):

    assert pdf_file != ""
    try:
        start_page, end_page = int(start_page) - 1, int(end_page)-1
    except:
        raise "start_page and end_page must be digit"
    
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
    settings.setsave('last_file', new_name)
    # settings.setsave('last_func', SPLITING_MSG)

    
def merge(pdf_file1, pdf_file2):
    pdf_merger = PdfFileMerger(strict=False)
    pdf_merger.append(pdf_file1)
    pdf_merger.append(pdf_file2)

    new_file = rename_file(pdf_file1, '_merged')
    with open(new_file, 'wb') as fileobj:
        pdf_merger.write(fileobj)

    settings.setsave('last_file', new_file)
    # settings.setsave('last_func', MERGING_MSG)


def crop(pdf_file, top, right, bottom, left):
    # POINT_MM = 25.4 / 72.0
    
    input_pdf = PdfFileReader(open(pdf_file, 'rb'),strict=False)
    output_pdf = PdfFileWriter()
    top, right, bottom, left = int(top), int(right), int(bottom), int(left)

  

    new_name = rename_file(pdf_file, '_croped')
    new_file = open(new_name, 'wb')

    num_pages = input_pdf.getNumPages()

    for i in range(num_pages):
        page = input_pdf.getPage(i)

        page.mediaBox.upperRight = (
            page.mediaBox.getUpperRight_x() - FloatObject(right),
            page.mediaBox.getUpperRight_y() - FloatObject(top)
        )
        page.mediaBox.lowerLeft = (
            page.mediaBox.getLowerLeft_x() + FloatObject(left),
            page.mediaBox.getLowerLeft_y() + FloatObject(bottom)
        )
        output_pdf.addPage(page)
        output_pdf.write(new_file)
    
    new_file.close()

    settings.setsave('last_file', new_name)
    # settings.setsave('last_func', CROPING_MSG)


def extract(pdf_file):
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

    settings.setsave('last_file', path)
    # settings.setsave('last_func', EXTRACTING_MSG)


def to_images(doc, pdf_file, start_page=None, end_page=None):
    # https://stackoverflow.com/a/55480474
    # doc = fitz.open(pdf_file)
    pages = doc.pageCount

    path = '/'.join(pdf_file.split('/')[:-1])+'/pdf_to_images/'
    try:
        os.mkdir(path)
    except:
        path = '/'.join(pdf_file.split('/')[:-1])+'/'
    
    zoom_x = 2.0  # horizontal zoom
    zomm_y = 2.0  # vertical zoom
    mat = fitz.Matrix(zoom_x, zomm_y)  # zoom factor 2 in each dimension
    
    if pages == 1:
        p = doc.loadPage(0)
        pix = p.getPixmap(matrix = mat)
        output = f"{path}outfile.png"
        pix.writePNG(output)
        return

    for page in range(0,pages-1):
        p = doc.loadPage(page) 
        pix = p.getPixmap(matrix = mat)
        output = f"{path}outfile_{page}.png"
        pix.writePNG(output)
    
    settings.setsave('last_file', path)


def to_pdf(*images):
    listImages = []

    for path_img in images:
        image = Image.open(path_img)
        image = image.convert('RGB')
        # fix rotation
        image = ImageOps.exif_transpose(image)
    
        listImages.append(image)

    new_name = os.path.normpath(images[0][:-4]+'.pdf')

    listImages[0].save(new_name, save_all=True, append_images=listImages[1:])

    
    settings.setsave('last_file', new_name)
    # settings.setsave('last_func', TOPDF_MSG)


def page_to_image(doc, page=0):

    p = doc.loadPage(page) 
    pix = p.getPixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


def remove_text_watermark(wm_text, inputFile, outputFile):
  # https://stackoverflow.com/a/57410205
  pass


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
    # new_name = makeSafeFilename(new_name)
    # print(new_name)
    new_name = os.path.realpath(new_name)
    return  new_name



if __name__ == "__main__":
    p = r"C:\Users\youssef\AppData\Local\Packages\38833FF26BA1D.UnigramPreview_g9c9v27vpyspw\LocalState\0\documents\مقدمات مكثف (4).pdf"
    # o = r"C:\\Users\\youssef\\Downloads\\3.txt"
    # d = fitz.open(p)
    to_txt(p)
    
