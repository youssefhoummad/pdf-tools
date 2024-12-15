
import configparser
import multiprocessing

import ctypes
import tkinter as tk
from tkinter import filedialog, ttk
import re
from pathlib import Path
import sys
from typing import Callable


sys.path.append('./libs') # pip install --target=./libs -r requirements.txt


from PIL import ImageTk, Image
import pypdfium2 as pdfium
# from winotify import Notification




class TitlebarFlasher:
    def __init__(self, master):
        self.master = master
        # Get the window handle
        self.hwnd = ctypes.windll.user32.GetForegroundWindow()
    
    def flash_titlebar(self, count=3, interval=0.5):
        """
        Flash the titlebar using Win32 API
        
        :param count: Number of times to flash
        :param interval: Time between flashes (in seconds)
        """
        # FLASHW_ALL: Flash both the window caption and taskbar button
        # FLASHW_TIMER: Flash continuously
        FLASHW_ALL = 0x00000003
        FLASHW_STOP = 0
        
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
        flash_info.hwnd = self.hwnd
        flash_info.dwFlags = FLASHW_ALL
        flash_info.uCount = count
        flash_info.dwTimeout = int(interval * 1000)  # Convert to milliseconds
        
        # Call the FlashWindowEx function
        ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))



class apply_dnd():
    """apply file drag and drop in a widget"""
    
    def __init__(self, widget: int, func: Callable, char_limit: int=260) -> None:

        hwnd = widget.winfo_id()

        GetWindowLong = ctypes.windll.user32.GetWindowLongPtrA
        SetWindowLong = ctypes.windll.user32.SetWindowLongPtrA
        typ = ctypes.c_uint64

        prototype = ctypes.WINFUNCTYPE(typ, typ, typ, typ, typ)
        WM_DROP_FILES = 0x233
        GWL_WND_PROC = -4
        create_buffer = ctypes.c_buffer
        func_DragQueryFile = (ctypes.windll.shell32.DragQueryFile)

        def py_drop_func(hwnd, msg, wp, lp):
            global files
            if msg == WM_DROP_FILES:
                count = func_DragQueryFile(typ(wp), -1, None, None)
                file_buffer = create_buffer(char_limit)
                files = []
                for i in range(count):
                    func_DragQueryFile(typ(wp), i, file_buffer, ctypes.sizeof(file_buffer))
                    drop_name = file_buffer.value.decode("utf-8")
                    files.append(drop_name)
                func(files)
                ctypes.windll.shell32.DragFinish(typ(wp))

            return ctypes.windll.user32.CallWindowProcW(
                *map(typ, (globals()[old], hwnd, msg, wp, lp))
            )

        """ Allow upto 10 widgets only to have dnd feature in one window, reduces system uses"""
        limit_num = 10
        for i in range(limit_num):
            if i + 1 == limit_num:
                raise OverflowError("DND limit reached for this session!")
            owp = f"old_wnd_proc_{i}"
            if owp not in globals():
                old, new = owp, f"new_wnd_proc_{i}"
                break

        globals()[old] = None
        globals()[new] = prototype(py_drop_func)

        ctypes.windll.shell32.DragAcceptFiles(hwnd, True)
        globals()[old] = GetWindowLong(hwnd, GWL_WND_PROC)
        SetWindowLong(hwnd, GWL_WND_PROC, globals()[new])



class Treeview(ttk.Treeview):
    def __init__(self, parent, on_select:Callable, on_drop:Callable, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bind("<<TreeviewSelect>>", self.on_row_select)
        apply_dnd(self, on_drop)

        self.on_select = on_select
    
    
    def move_up(self, *args, **kwargs):
        leaves = self.selection()
        for i in leaves:
            self.move(i, self.parent(i), self.index(i)-1)


    def move_down(self, *args, **kwargs):
        leaves = self.selection()
        for i in reversed(leaves):
            self.move(i, self.parent(i), self.index(i)+1)
    

    def remove_item(self, *args, **kwargs):
        leaves = self.selection()
        if leaves:
            self.delete(leaves[0])



    def on_row_select(self, *args, **kws):
        selected_item = self.selection()
        if selected_item:
            values = self.item(selected_item[0], 'values')
            self.on_select(values)





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


def styling_tkinter(window):
    background =  "#FDFDFD" #'#EFF4F9'

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
    style.configure("TNotebook", padding=[3, 1])
    style.configure('TNotebook.Tab', padding=(15, 2), font=('Segoe UI', 9))
    style.configure('Content.TLabel', font=('Segoe UI', 9))
    style.configure('Content.TButton', font=('Segoe UI', 9))
    style.configure('Content.TEntry', font=('Segoe UI', 9))
    style.map("TNotebook.Tab", foreground=[("!selected", "gray")])


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






################## GUI MVC ################

class Model:
    def __init__(self):
        self.PDF = None
        self.PATHS = []

        self.scale = tk.IntVar(value=1)
        self.degree = tk.IntVar(value=0)
        self.save_option = tk.IntVar(value=1)

        self.temp_location = None




class App:
    def __init__(self, parent, View, Model):
        self.parent = parent

        self.model = Model() 
        self.view = View(self.parent, controler=self, model=self.model)
        self.view.setup(self, self.model)

        save_settings = load_settings('settings.ini')
    
        if save_settings['Save']['option'] =='2':
            self.model.save_option.set(2)
            self.view.save_label.configure(text=save_settings['Save']['location'])
        else:
            self.model.save_option.set(1)


    def select_pdf(self, path):
        self.model.PDF = pdfium.PdfDocument(path)
        self.view.file_info.config(text=f"{Path(path).name}\nPages: {len(self.model.PDF)}")
        self.show_preview()


    def get_output_path(self, src_path, is_file=True):
        save_option = self.model.save_option.get()

        # Option 1: Default save location
        if save_option == 1:
            return set_output_file(src_path, 'new') if is_file else set_output_dir(src_path)

        # Option 2: Load location from settings.ini
        elif save_option == 2:
            save_location = Path(load_settings('settings.ini')['Save']['location'])
            if not is_file:
                output_dir = save_location / 'images'
                output_dir.mkdir(parents=True, exist_ok=True)
                return output_dir
            if is_file:
                return save_location / Path(src_path).name


    def clear(self):
        self.view.split_entry.delete(0, 'end')
        self.view.delete_entry.delete(0, 'end')
        self.view.rotate_entry.delete(0, 'end')
        self.view.image_entry.delete(0, 'end')

        self.view.preview_canvas.delete('picture')

        self.view.treepdf.delete(*self.view.treepdf.get_children())
        self.view.treeimage.delete(*self.view.treeimage.get_children())

        self.view.file_info.config(text=f"Non file selected \n")

        self.model.PDF = None


    def show_preview(self, event=None, astr=None):
        if not self.model.PDF: return
        page = 1 if not astr else int(re.findall(r'\d+', astr)[-1])

        if page > len(self.model.PDF) : 
            raise IndexError("Failed to load page.")
        
        self.view.preview_canvas.delete('picture')

        bitmap = self.model.PDF[page-1].render(scale=1, rotation=0)
        image  = bitmap.to_pil()
        image = image.resize((400, 520), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(image)
        self.view.preview_canvas.create_image(0, 0, anchor="nw", image=tk_image, tag='picture')
        self.view.preview_canvas.image = tk_image # for ignore garbage collection


    def apply(self):

        if self.view.notebook.index("current") == 3: # settings tab
            return
    

        if self.view.notebook.index("current") == 2: # Convert images to pdf tab
            paths_imgs = [self.view.treeimage.item(item)['values'][1] for item in self.view.treeimage.get_children()]
            if not paths_imgs: return
            
            output_path = Path(self.get_output_path(paths_imgs[0], is_file=False))
            output_path = output_path.with_suffix('.pdf')
            images_pdfs(paths_imgs, output_path) # convert func

            return
        
        
        if not self.model.PDF:
            self.view.flasher.flash_titlebar(count=3, interval=0.2)
            return
        

        writer = pdfium.PdfDocument.new()
        paths = [self.view.treepdf.item(item)['values'][0] for item in self.view.treepdf.get_children()]


        if self.view.notebook.index("current") == 0: # tools tab
            astr_image = self.view.image_entry.get()
            astr_rotate = self.view.rotate_entry.get()
            astr_delete = self.view.delete_entry.get()
            astr_split = self.view.split_entry.get()

            rotated = False
            splited = False

            if astr_image:
                output_dir = self.get_output_path(paths[-1], is_file=False)
                pdf_images(self.model.PDF, astr_image, int(self.model.scale.get()), output_dir)

            if astr_rotate:
                output_path = self.get_output_path(self.model.PDF._input)
                pdf_rotate(self.model.PDF, astr_rotate, self.model.degree.get())
                rotated = True


            if astr_split or astr_delete:
                output_path = self.get_output_path(self.model.PDF._input)

                pdf_split(self.model.PDF, astr_split, astr_delete, writer)
                splited = True


            if splited: 
                writer.save(output_path)
                return
            if rotated:
                self.model.PDF.save(output_path)
                return

        if self.view.notebook.index("current") == 1:
            if not paths: return
            output_path = self.get_output_path(paths[0])

            writer = pdfium.PdfDocument.new()
            
            for pdf_path in paths:
                writer.import_pages(
                    pdfium.PdfDocument(pdf_path)
                )
            writer.save(output_path)
            return

            # toast = Notification(app_id="pdf tools",
            #          title="Finish",
            #          msg="All files merged!",
            #          icon=Path(Path(__file__).parent.absolute()) / r'img/icon.png'
            #         )
            # toast.show()


    def change_settings(self):
        settings = {'Save': {'option': self.model.save_option.get(), 'location': ''},}
        if self.model.save_option.get() == 2:
            save_location = filedialog.askdirectory()
            if not save_location: return

            save_location = r'{}'.format(save_location) 
            settings = {'Save': {'option': self.model.save_option.get(), 'location': save_location},}
            self.view.save_label.configure(text=save_location)

        save_settings('settings.ini', settings)


    def mainloop(self):
        self.parent.mainloop()




class View:
    def __init__(self, parent, controler, model):
        self.parent = parent

        self.controler = controler
        self.model = model
        self.validate_cmd = parent.register(validate_input)

        self.flasher = TitlebarFlasher(parent)


    def setup(self, controler, model):
        self.controler = controler
        self.model = model

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(pady=(5,10), expand=True, fill='both', padx=10)

        self.notebook.add(self.tab_tools(), text=" Tools ")
        self.notebook.add(self.tab_merge(), text=" Merge ")
        self.notebook.add(self.tab_convert(), text=" Convert ")
        self.notebook.add(self.tab_settings(), text=" Settings ")

        ttk.Button(self.parent, text="Apply", command=self.controler.apply).pack(side="right", padx=15, pady=(5,20), ipadx=10)
        ttk.Button(self.parent, text="clear", command=self.controler.clear).pack(side="right", padx=5, pady=(5,20))

        self.file_info = tk.Label(self.parent, text=f"No file selected \n", fg="gray", bg="#F0F0F0", justify='left', anchor='nw', wraplength=600)
        self.file_info.pack(side="left", padx=20, pady=(5,20), anchor='nw', fill='x', expand=True)
        
    
    def tab_tools(self):
        tab_tools = ttk.Frame(self.parent) 
        frame_left = ttk.Frame(tab_tools)
        frame_right = ttk.Frame(tab_tools)
        frame_bottom = ttk.Frame(tab_tools)

        split_group = ttk.LabelFrame(frame_left, text="Split")
        split_label = ttk.Label(split_group, text="Entre the range of pages to splited")
        self.split_entry = ttk.Entry(split_group, validate='key', validatecommand=(self.validate_cmd, '%P'))
        self.split_entry.bind("<KeyRelease>", lambda astr: self.controler.show_preview(astr=self.split_entry.get())) #keyup  


        delete_group = ttk.LabelFrame(frame_left, text="Delete")
        delete_label = ttk.Label(delete_group, text="Entre the range of pages to deleted")
        self.delete_entry = ttk.Entry(delete_group, validate='key', validatecommand=(self.validate_cmd, '%P'))
        self.delete_entry.bind("<KeyRelease>", lambda astr: self.controler.show_preview(astr=self.delete_entry.get())) #keyup  


        rotate_group = ttk.LabelFrame(frame_left, text="Rotate")
        rotate_label = ttk.Label(rotate_group, text="Entre the range of pages to rotated")
        self.rotate_entry = ttk.Entry(rotate_group, validate='key', validatecommand=(self.validate_cmd, '%P'))
        self.rotate_entry.bind("<KeyRelease>", lambda astr: self.controler.show_preview(astr=self.rotate_entry.get())) #keyup  
        rotate_label2 = ttk.Label(rotate_group, text="Choose degree")
        rotate_combobox = ttk.Combobox(rotate_group, values=[0, 90, 180, 270], textvariable=self.model.degree)

        image_group = ttk.LabelFrame(frame_left, text="Image")
        image_label = ttk.Label(image_group, text="Entre the range of pages to images")
        self.image_entry = ttk.Entry(image_group, validate='key', validatecommand=(self.validate_cmd, '%P'))
        self.image_entry.bind("<KeyRelease>", lambda astr: self.controler.show_preview(astr=self.image_entry.get())) #keyup  
        image_label2 = ttk.Label(image_group, text="Choose zoom")
        image_scale = ttk.Scale(image_group, from_=1, to=8, orient="horizontal", variable=self.model.scale)


        self.preview_canvas = tk.Canvas(frame_right, width=400, height=520, bg="white", highlightthickness=1, highlightcolor='black')
        self.preview_canvas.bind('<Button-1>', self.add_pdf)
        self.preview_canvas.bind("<Enter>", lambda event: self.preview_canvas.config(bg="#f0f0f0"))
        self.preview_canvas.bind("<Leave>", lambda event: self.preview_canvas.config(bg="white"))


        self.preview_canvas.create_rectangle(30, 30, 370, 490, outline='gray', width=1,dash=(5, 5))
        self.preview_canvas.create_text(200, 250, text="click or drag file here",font=("Segoe UI", 12, 'italic'), fill="gray")
        apply_dnd(self.preview_canvas, self.on_drop_pdf)

        

        frame_left.grid(row=0, column=0, padx=10, sticky='we')
        tab_tools.grid_columnconfigure(0, weight=1)
        frame_right.grid(row=0, column=1)
        frame_bottom.grid(row=1, column=0, columnspan=2, sticky='e')

        split_group.pack(fill='x', pady=10)
        split_label.pack(fill='x')
        self.split_entry.pack(fill='x')

        delete_group.pack(fill='x', pady=10)
        delete_label.pack(fill='x')
        self.delete_entry.pack(fill='x')

        rotate_group.pack(fill='x', pady=10)
        rotate_label.pack(fill='x')
        self.rotate_entry.pack(fill='x')
        rotate_label2.pack(fill='x', pady=(10, 0))
        rotate_combobox.pack(fill='x')

        image_group.pack(fill='x', pady=10)
        image_label.pack(fill='x')
        self.image_entry.pack(fill='x')
        image_label2.pack(fill='x', pady=(10, 0))
        image_scale.pack(fill='x')

        self.preview_canvas.pack(padx=10, pady=10, fill='both')

        return tab_tools


    def tab_merge(self):
        tab = ttk.Frame(self.parent)

        ttk.Label(tab, foreground ='gray', font=('Segoe UI', 10, 'italic') , text="PDF Merger: A user-friendly tool that allows you to easily combine multiple PDF files into a single document. \nDrag and drop your PDF files, rearrange them as needed.").pack(fill='x', padx=10, pady=20)

        _ = ttk.Frame(tab)
        _.pack(fill='x')


        def on_select(values):
            path, _ = values
            self.controler.select_pdf(path)

        
        self.treepdf = Treeview(tab, on_select=on_select, on_drop=self.on_drop_pdf, columns=("A", "B"), show='headings')
        self.treepdf.column("# 1", stretch='yes')
        self.treepdf.heading("# 1", text="path", anchor='w')
        self.treepdf.column("# 2",anchor='e', stretch='no', width=80)
        self.treepdf.heading("# 2", text="pages")

        ttk.Button(_, text="Add file", command=self.add_pdf).pack(padx=10, pady=10, anchor='nw', side='left')
        ttk.Button(_, text="Up", command=self.treepdf.move_up).pack(padx=10, pady=10, anchor='nw', side='right')
        ttk.Button(_, text="Down", command=self.treepdf.move_down).pack(padx=10, pady=10, anchor='nw', side='right')
        ttk.Button(_, text="remove", command=self.treepdf.remove_item).pack(padx=10, pady=10, anchor='nw', side='right')

        self.treepdf.pack(fill='both', expand=True, anchor='nw', padx=10, pady=10)
        
        return tab


    def tab_convert(self):
        tab = ttk.Frame(self.parent)
        ttk.Label(tab, foreground ='gray', font=('Segoe UI', 10, 'italic'), text="Image to PDF Converter: A user-friendly tool that allows you to easily convert and combine multiple images \ninto a single, high-quality PDF file with drag-and-drop functionality.").pack(fill='x', padx=10, pady=20)

        _ = ttk.Frame(tab)
        _.pack(fill='x')

        def on_select(value):
            filename , path = value
            print("Show preview of image: ", filename)
        
        self.treeimage = Treeview(tab, on_select=on_select, on_drop=self.on_drop_img, columns=("A", "B"), show='headings')
        self.treeimage.column("# 1",anchor='w', stretch='no', width=200)
        self.treeimage.heading("# 1", text="filename")
        self.treeimage.column("# 2", stretch='yes')
        self.treeimage.heading("# 2", text="path", anchor='w')

        ttk.Button(_, text="Add file", command=self.add_pdf).pack(padx=10, pady=10, anchor='nw', side='left')
        ttk.Button(_, text="Up", command=self.treeimage.move_up).pack(padx=10, pady=10, anchor='nw', side='right')
        ttk.Button(_, text="Down", command=self.treeimage.move_down).pack(padx=10, pady=10, anchor='nw', side='right')
        ttk.Button(_, text="remove", command=self.treeimage.remove_item).pack(padx=10, pady=10, anchor='nw', side='right')


        self.treeimage.pack(fill='both', expand=True, padx=10, pady=10)

        return tab


    def tab_settings(self):
        tab = ttk.Frame(self.parent)

        save_group = ttk.LabelFrame(tab, text="Save Location")
        save_group.pack(fill='x', padx=15, pady=10)

        ttk.Radiobutton(save_group, text="in same location of origin file", variable=self.model.save_option, value=1, command=self.controler.change_settings).pack(fill='x', pady=3)
        ttk.Radiobutton(save_group, text="in this location: ", variable=self.model.save_option, value=2, command=self.controler.change_settings).pack(fill='x', pady=3)

        self.save_label = ttk.Label(save_group, text="", foreground="gray", wraplength=600)
        self.save_label.pack(fill='x', padx=(40, 0), anchor='nw', expand=True)

        _ = ttk.Frame(tab)
        ttk.Label(_, text="PDF tools v4.0", font=('default', 12, 'bold')).pack(pady=(68, 12))
        ttk.Button(_, text="check update", state='disabled').pack(padx=10, pady=12, ipadx=4)
        ttk.Label(_, text="https://github.com/youssefhoummad/pdf-tools/", foreground="dodgerblue1").pack(pady=10)
        ttk.Label(_, text="Copyrigth © youssef hoummad, All rights reserved", foreground="gray").pack()
        _.pack(fill='x')      

        return tab


    def add_pdf(self, *args, **kws):
        path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
        if not path: return

        path = r'{}'.format(path) # convert to raw

        self.controler.select_pdf(path)
        self.treepdf.insert("", 'end', values=(path,len(self.model.PDF)))


    def on_drop_pdf(self, event, *args):
        for path in event:
            if path.lower().endswith('.pdf'):
                self.controler.select_pdf(path)
                self.treepdf.insert("", 'end', values=(path,len(self.model.PDF)))


    def on_drop_img(self, event, *args, **kws):
        for path in event:
            if path.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.treeimage.insert("", 'end', values=(Path(path).name, path))



if __name__ == '__main__':
    # multiprocessing.freeze_support() # for multiprecessing in windows	
    # myappid =  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('youssefhoummad.pdftools.4.0') # show icon in taskbar
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    window = tk.Tk()
    
    window.iconbitmap(r'img/icon.ico')

    window.title('pdftools')
    styling_tkinter(window)

    app = App(window, View, Model)
    app.mainloop()