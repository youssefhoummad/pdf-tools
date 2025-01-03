import configparser
import ctypes
from pathlib import Path
import sys
from tkinter import ttk


sys.path.append('./libs') # pip install --target=./libs -r requirements.txt

from PIL import Image



def flash_titlebar(master, count=3, interval=0.5):
    """
    Flash the titlebar using Win32 API
    
    :param master: Tkinter master or any GUI window reference (used to identify the handle)
    :param count: Number of times to flash
    :param interval: Time between flashes (in seconds)
    """
    # Get the window handle
    hwnd = ctypes.windll.user32.GetForegroundWindow()

    # FLASHW_ALL: Flash both the window caption and taskbar button
    FLASHW_ALL = 0x00000003

    # Struct to pass flash parameters
    class FLASHWINFO(ctypes.Structure):
        _fields_ = [
            ('cbSize', ctypes.c_uint),
            ('hwnd', ctypes.c_void_p),
            ('dwFlags', ctypes.c_uint),
            ('uCount', ctypes.c_uint),
            ('dwTimeout', ctypes.c_uint)
        ]
    
    # Create flash info structure
    flash_info = FLASHWINFO()
    flash_info.cbSize = ctypes.sizeof(flash_info)
    flash_info.hwnd = hwnd
    flash_info.dwFlags = FLASHW_ALL
    flash_info.uCount = count
    flash_info.dwTimeout = int(interval * 1000)  # Convert to milliseconds
    
    # Call the FlashWindowEx function
    ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))



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


def styling_svttk(window):
    from tkinter import font

    font.nametofont("SunValleyBodyFont").configure(family="Segoe UI")
    font.nametofont("SunValleyBodyStrongFont").configure(family="Segoe UI", weight="bold")
    
    background = '#E7E7E7'
    window.config(background="#E7E7E7")
    style = ttk.Style()
    
    # style.configure('TLabelframe.Label', font=('Segoe UI', 10, 'bold'))
    # style.configure('TNotebook.Tab', background="red")
    style.configure('TFrame', background="white")
    style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'), background="white")
    style.configure('TLabelframe', padding=12, background="white")


    style.configure('Desc.TLabel', background=background, foreground="gray", font='italic')


def styling_tkinter(window):
    background =  'white'# "#EFF4F9" #'#EFF4F9'

    # for widget in ["Ttk", "Tk", "TLabelFrame", "TRadiobutton", "TEntry", "TButton", "TLabel", "TScale", "TNotebook", "TNotebook.Tab"]:
    #     window.option_add(f'*{widget}*direction', 'rtl')  # تعيين الاتجاه لجميع عناصر ttk
    #     window.option_add(f'*{widget}*justify', 'right')  # تعيين الاتجاه لجميع عناصر ttk
    #     window.option_add(f'*{widget}*anchor', 'e')  # تعيين الاتجاه لجميع عناصر ttk


    style = ttk.Style()
    window.config(background="#F0F0F0")
    style.configure('TEntry', padding=4)
    style.configure('TCombobox', padding=4)
    style.configure('TButton', padding=3)
    style.configure('TFrame', background=background)
    style.configure('TRadiobutton', background=background)
    style.configure('TLabel', background=background)
    style.configure('Desc.TLabel', background=background, foreground="gray", font='italic')
    style.configure('TScale', background=background)
    style.configure('TLabelframe', padding=6, background=background)
    style.configure('Content.TLabelframe', padding=6, background=background)
    style.configure('TLabelframe.Label', font=('Segoe UI', 10, 'bold'), background=background)
    style.configure('TNotebook.Tab', padding=(15, 2), font=('Segoe UI', 9))
    style.map("TNotebook.Tab", background=[("selected", 'red')], foreground=[("selected", "#0078d7"), ("!selected", "gray")])

    style.configure('Content.TLabel', font=('Segoe UI', 9))
    style.configure('Content.TButton', font=('Segoe UI', 9))
    style.configure('Content.TEntry', font=('Segoe UI', 9))
    # style.map("TNotebook.Tab", foreground=[("!selected", "gray")])


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


def validate_input(astr:str) -> bool: # add arg=max:int
    if astr[-2:] in ['  ', '--', ',,', '-,', ',-']:
        return False
    if astr[-3:] in ['- -', ', ,', '- ,', ', -']:
        return False
    
    # if last digit > max: return False
    return all(char.isdigit() or char in '-, ' for char in astr)






def pdf_split(pdf, astr_split, astr_delete, writer):
    pages_split = parse_range(astr_split)
    pages_split = pages_split if pages_split else range(0, len(pdf))
    pages_delete = parse_range(astr_delete)
    pages_selected = sorted(list(filter(lambda x: x not in pages_delete, pages_split)))

    writer.import_pages(pdf, pages_selected)



def pdf_rotate(pdf, astr_rotate, degree):
    pages_selected = parse_range(astr_rotate)
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



