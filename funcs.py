import configparser
from pathlib import Path
import re
from tkinter import ttk
import tkinter.font as tkfont
from typing import Optional

from PIL import Image, ImageTk



def save_settings(file_path, settings):
    config = configparser.ConfigParser()
    for section, values in settings.items():
        config[section] = values
    with open(file_path, 'w') as configfile:
        config.write(configfile)



def load_settings(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    settings = {}
    for section in config.sections():
        settings[section] = dict(config.items(section))
    return settings



def styling_tkinter(window, rtl=False):
    background =  '#F9F9F9'# "#EFF4F9" #'#EFF4F9'

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=9)
    style = ttk.Style()


    for widget in ["Ttk", "Tk", "TFrame", "TLabelFrame", "TRadiobutton", "TEntry", "TButton", "TLabel", "TScale", "TCombobox"]:
        style.configure(widget,  background=background)
 

    style.configure('TEntry', padding=4)
    style.configure('TCombobox', padding=5)
    style.configure('TButton', padding=3)

    style.configure('TNotebook.Tab', padding=(15, 2), font=('Segoe UI', 9))
    style.map("TNotebook.Tab", background=[("selected", 'red')], foreground=[("selected", "#0078d7"), ("!selected", "gray")])

    style.configure('Content.TLabel', font=('Segoe UI', 9))
    style.map("TNotebook.Tab", foreground=[("!selected", "gray")])


    if rtl:
        # window_dwm.toggle_rtl_layout(window, enabled=True)

        window.option_add('*Ttk*direction', 'rtl')
        window.option_add('*TLabel*justify', 'right')
        window.option_add('*TLabel*anchor', 'e')
        window.option_add('*TEntry*justify', 'right')

        style.configure('TNotebook.Tab', tabposition='ne') # option to change position of tab
        style.configure('TNotebook',height=40, width=80, tabposition='ne')
        
        for widget in ["Ttk", "Tk", "TLabelFrame", "TRadiobutton", "TEntry", "TButton", "TLabel", "TScale"]:
            window.option_add(f'*{widget}*direction', "rtl")  # تعيين الاتجاه لجميع عناصر ttk
            window.option_add(f'*{widget}*justify', 'right')  # تعيين الاتجاه لجميع عناصر ttk
            window.option_add(f'*{widget}*anchor', 'e')  # تعيين الاتجاه لجميع عناصر ttk

    
        style.layout('TRadiobutton',
            [('Radiobutton.padding', {'sticky': 'nswe', 'children': [
                ('Radiobutton.indicator', {'side': 'right', 'sticky': ''}),
                ('Radiobutton.focus', {'side': 'right', 'sticky': '', 'children': [
                    ('Radiobutton.label', {'sticky': ''})
                ]})
            ]})]
        )

        style.layout('TCombobox', [
        ('Combobox.field', {'sticky': 'nswe', 'children': [
            ('Combobox.downarrow', {'side': 'left', 'sticky': 'ns'}),
            ('Combobox.padding', {'expand': '1', 'sticky': 'nswe', 'children': [
                ('Combobox.textarea', {'sticky': 'nswe'})
                ]})
            ]})
        ])



def set_output_file(pdf_path:str ,refain:str):
    base_path = Path(pdf_path)
    output_path = base_path.with_stem(f"{base_path.stem}_{refain}ed")

    i = 0
    while output_path.is_file():
        i += 1
        output_path = base_path.with_stem(f"{base_path.stem}_{refain}ed_{i}")
    
    return output_path.with_suffix('.pdf') # prefix = output_path / stem



def set_output_dir(pdf_path:str)-> str:
    path = Path(pdf_path).parent.joinpath('images')
    path.mkdir(parents=True, exist_ok=True)
    return path



def parse_range(astr:str)-> list[int]:
    "simple function that provides a PageRange object typically used in printing."
    if not astr: return []
    result=set()
    astr = astr.rstrip(',').rstrip('-').rstrip(' ')
    # astr = "".join(filter(lambda char: char in  "0123456789-,", astr))
    for part in astr.split(','):
        x=part.split('-')
        result.update(range(int(x[0])-1,int(x[-1])))
    return sorted(result)



def pdf_split(pdf, astr_split, astr_delete, writer):
    pages_split = parse_range(astr_split)
    pages_split = pages_split if pages_split else range(0, len(pdf))
    pages_delete = parse_range(astr_delete)
    pages_selected = sorted(list(filter(lambda x: x not in pages_delete, pages_split)))

    writer.import_pages(pdf, pages_selected)



def pdf_rotate(pdf, astr_rotate, degree):
    pages_selected = parse_range(astr_rotate)
    degree = int(degree)
    list(map(lambda page_index: pdf[page_index].set_rotation(degree), pages_selected))



def pdf_images(pdf, astr:str, zoom:int, output_dir:str):

    pages_selected = parse_range(astr)

    def one_page(index):
        page = pdf[index]  # load a page
        bitmap = page.render(
            scale = zoom,    # 72dpi resolution
            rotation = 0, # no additional rotation
            # ... further rendering options
        )
        pil_image = bitmap.to_pil()
        pil_image.save(Path(output_dir,  f"page-{index+1}.png"))

    list(map(lambda index: one_page(index), pages_selected))



def images_pdfs(images_path:list, output_path:str):
    images = [Image.open(path) for path in images_path]
    images[0].save(output_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:])



def extract_page_number(text: Optional[str], default: int = 1) -> int:
    """استخراج آخر رقم من النص، وإرجاع default إذا لم يُعثر على أرقام."""
    if not text:
        return default
    digits = re.findall(r'\d+', text)
    return int(digits[-1]) if digits else default



def render_page_to_tkimage(page_obj, target_width: int = 400):
    """تحويل صفحة PDF إلى كائن PhotoImage الخاص بـ Tkinter."""
    scale = target_width / page_obj.get_width()
    bitmap = page_obj.render(scale=scale, rotation=0)
    pil_image = bitmap.to_pil()
    return ImageTk.PhotoImage(pil_image)