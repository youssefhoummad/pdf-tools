
import configparser
import ctypes
# import multiprocessing
import os
import tkinter as tk
from tkinter import filedialog, ttk
import re
from PIL import ImageTk, Image
from pathlib import Path
import sys

path = str(Path(Path(__file__).parent.absolute()) / 'packages')
sys.path.insert(0, path)


import pypdfium2 as pdfium



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


def styling(window):
    background =  "#FDFDFD" #'#EFF4F9' 

    style = ttk.Style()
    window.config(background="#F0F0F0")
    style.configure('TEntry', padding=3)
    style.configure('TCombobox', padding=3)
    style.configure('TButton', padding=3)
    style.configure('TFrame', background=background)
    style.configure('TRadiobutton', background=background)
    style.configure('TLabel', background=background)
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


def validate_input(astr:str) -> bool:
    if astr[-2:] in ['  ', '--', ',,', '-,', ',-']:
        return False
    if astr[-3:] in ['- -', ', ,', '- ,', ', -']:
        return False
    return all(char.isdigit() or char in '-, ' for char in astr)


def get_last_chars(s):
    if len(s) > 60:
        return '...' + s[-60:]  # Add '...' before the last 30 characters
    return s




class Model:
    def __init__(self):
        self.PDF = None
        self.PATHS = []

        self.scale = tk.IntVar(value=1)
        self.degree = tk.IntVar(value=0)
        self.save_option = tk.IntVar(value=1)



class App:
    def __init__(self, parent, View, Model):
        self.parent = parent

        self.model = Model() 
        self.view = View(self.parent, controler=self, model=self.model)
        self.view.setup(self, self.model)

        save_location = load_settings('settings.ini')['Save']['location']
        if save_location:
            self.model.save_option.set(3)
            self.view.save_label.configure(text=save_location)
    

    def on_row_select(self, event, *args, **kws):
        selected_item = self.view.treeview.selection()
        
        if selected_item:
            # Get the values of the selected row
            file_path, _ = self.view.treeview.item(selected_item[0], 'values')
            # print("Selected Row Values:", item_values)
            self.select_pdf(file_path)
    

    def select_pdf(self, path):
        self.model.PDF = pdfium.PdfDocument(path)
        self.view.file_info.config(text=f"Selected file: {get_last_chars(path)}\nPages: {len(self.model.PDF)}")
        self.show_preview()


    def output_dir(self, src_path):
        if self.model.save_option.get()==1:
            output_dir = set_output_dir(src_path)
        
        if self.model.save_option.get()==2:
            output_dir = filedialog.askdirectory()
            if not output_dir: 
                self.model.save_option.set(1)
                output_dir = set_output_dir(src_path)

        if self.model.save_option.get()==3:
            save_location = load_settings('settings.ini')['Save']['location']
            output_dir = Path(save_location).joinpath('images')
            output_dir.mkdir(parents=True, exist_ok=True)
        
        return output_dir


    def output_path(self, src_path):
        if self.model.save_option.get()==1:
            output_path = set_output_file(src_path, 'new')
        
        if self.model.save_option.get()==2:
            output_path = filedialog.askdirectory()
            if not output_path: 
                self.model.save_option.set(1)
                output_dir = set_output_dir(src_path)

        if self.model.save_option.get()==3:
            save_loction = load_settings('settings.ini')['Save']['location']
            filename = os.path.basename(src_path)
            print(f"{save_loction=}")
            print(f"{filename=}")
            output_dir = os.path.join(save_loction, filename)

        return output_dir


    def clear(self):
        self.view.split_entry.delete(0, 'end')
        self.view.delete_entry.delete(0, 'end')
        self.view.rotate_entry.delete(0, 'end')
        self.view.image_entry.delete(0, 'end')
        self.view.preview_canvas.delete('picture')
        self.view.preview_canvas.update()
        self.view.treeview.delete(*self.view.treeview.get_children())
        self.view.file_info.config(text=f"Selected file: \nPages:")

        self.model.PDF = None
        self.model.PATHS = []


    def add_file(self, *args, **kws):
        file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
        if not file_path: return

        file_path = r'{}'.format(file_path) # convert to raw

        self.select_pdf(file_path)
        self.model.PATHS.append(file_path)
        self.view.treeview.insert("", 'end', values=(file_path,len(self.model.PDF)))



    def on_drop_pdfs(self, event, *args):
        matches = re.findall(r'(?:\{(.+?)\}|([^\s]+))', event.data)

        # Flatten the matches and filter out empty strings
        paths = [item for match in matches for item in match if item]
        print(paths)

        # paths = event.data.split(', ').strip().strip("{}").split("} {")
        # print(event.data.replace('', ))
        # paths = event.data.replace("} {", ",").replace('{','').replace('}', '').split(',')
        # print(paths)
        for path in paths:
            if path.lower().endswith('.pdf'):
                self.tree_pdfs.insert('', 'end', values=(path,))


    def show_preview(self, event=None, astr=None):
        if not self.model.PDF: return
        page = 1 if not astr else int(re.findall(r'\d+', astr)[-1])

        if page > len(self.model.PDF) : 
            raise IndexError("Failed to load page.")
        
        print(page)

        self.view.preview_canvas.delete('picture')

        bitmap = self.model.PDF[page-1].render(scale=1, rotation=0)
        image  = bitmap.to_pil()
        image = image.resize((400, 520), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(image)
        self.view.preview_canvas.create_image(0, 0, anchor="nw", image=tk_image, tag='picture')
        self.view.preview_canvas.image = tk_image # for ignore garbage collection


    def apply(self):
        writer = pdfium.PdfDocument.new()
        writing = False

        if self.view.notebook.index("current") == 0: # first tab
            
            if self.view.image_entry.get():
                output_dir = self.output_dir(self.model.PATHS[-1])

                pages_selected = parse_range(self.view.image_entry.get())
                zoom = int(self.model.scale.get())
                print(f"convert {pages_selected=} to images with {zoom=}...")

                def one_page(index):
                    page = self.model.PDF[index]  # load a page
                    bitmap = page.render(
                        scale = zoom,    # 72dpi resolution
                        rotation = 0, # no additional rotation
                        # ... further rendering options
                    )
                    pil_image = bitmap.to_pil()
                    pil_image.save(Path(output_dir,  f"page-{index+1}.png"))

                list(map(lambda index: one_page(index), pages_selected))


            if self.view.rotate_entry.get():
                output_path = self.output_path(self.model.PATHS[-1])

                pages_selected = parse_range(self.view.rotate_entry.get())
                degree = int(self.model.degree.get())
                list(map(lambda page_index: self.model.PDF[page_index].set_rotation(degree), pages_selected))
                writing = True
                # print(f"rotating pages {pages_selected=} to {degree=}...")
            

            if self.view.split_entry.get() or self.view.delete_entry.get():
                output_path = self.output_path(self.model.PATHS[-1])

                pages_split = parse_range(self.view.split_entry.get())
                pages_split = pages_split if pages_split else range(0, len(self.model.PDF))
                pages_delete = parse_range(self.view.delete_entry.get())
                pages_selected = sorted(list(filter(lambda x: x not in pages_delete, pages_split)))

                writer.import_pages(self.model.PDF, pages_selected)
                writing = True
                # print(f"spliting pages {pages_selected}... ")


            if writing:
                writer.save(output_path)


        if self.view.notebook.index("current") == 1:
            # print("merging...")
            output_path = self.output_path(self.model.PATHS[0])

            writer = pdfium.PdfDocument.new()
            
            for pdf_path in self.model.PATHS:
                writer.import_pages(
                    pdfium.PdfDocument(pdf_path)
                )
            writer.save(output_path)
        

        # if self.view.notebook.index("current") == 2:

            
    def change_settings(self):
        settings = {'Save': {'option': self.model.save_option.get(), 'location': ''},}
        if self.model.save_option.get() == 3:
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


    def setup(self, controler, model):
        self.controler = controler
        self.model = model

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(pady=(5,10), expand=True, fill='both', padx=10)

        self.notebook.add(self.tab_tools(), text=" Tools ")
        self.notebook.add(self.tab_merge(), text=" Merge ")
        self.notebook.add(self.tab_settings(), text=" Settings ")

        ttk.Button(self.parent, text="Apply", command=self.controler.apply).pack(side="right", padx=15, pady=(5,20), ipadx=10)
        ttk.Button(self.parent, text="clear", command=self.controler.clear).pack(side="right", padx=5, pady=(5,20))

        self.file_info = tk.Label(self.parent, text=f"Selected file: \nPages: ", fg="gray", bg="#F0F0F0", justify='left', anchor='nw', wraplength=500)
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
        self.preview_canvas.bind('<Button-1>', self.controler.add_file)
        self.preview_canvas.bind("<Enter>", lambda event: self.preview_canvas.config(bg="#f0f0f0"))
        self.preview_canvas.bind("<Leave>", lambda event: self.preview_canvas.config(bg="white"))


        self.preview_canvas.create_rectangle(30, 30, 370, 490, outline='gray', width=1,dash=(5, 5))
        self.preview_canvas.create_text(200, 250, text="click or drag file here",font=("Segoe UI", 12, 'italic'), fill="gray")

        

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
        tab_merge = ttk.Frame(self.parent)

        _ = ttk.Frame(tab_merge)

        ttk.Button(_, text="Add file", command=self.controler.add_file).pack(padx=10, pady=10, anchor='nw', side='left')
        ttk.Button(_, text="Up", command=self.move_up).pack(padx=10, pady=10, anchor='nw', side='right')
        ttk.Button(_, text="Down", command=self.move_down).pack(padx=10, pady=10, anchor='nw', side='right')

        _.pack(fill='x')
        
        self.treeview = ttk.Treeview(tab_merge, columns=("A", "B"), show='headings')
        self.treeview.column("# 1", stretch='yes')
        self.treeview.heading("# 1", text="path", anchor='w')
        self.treeview.column("# 2",anchor='e', stretch='no', width=80)
        self.treeview.heading("# 2", text="pages")

        self.treeview.bind("<<TreeviewSelect>>", self.controler.on_row_select)
   

        self.treeview.pack(fill='both', expand=True, anchor='nw', padx=10, pady=10)
        

        return tab_merge

    def move_up(self):
        leaves = self.treeview.selection()
        for i in leaves:
            self.treeview.move(i, self.treeview.parent(i), self.treeview.index(i)-1)



    def move_down(self):
        leaves = self.treeview.selection()
        for i in reversed(leaves):
            self.treeview.move(i, self.treeview.parent(i), self.treeview.index(i)+1)

    def tab_settings(self):
        tab = ttk.Frame(self.parent)

        save_group = ttk.LabelFrame(tab, text="Save Location")
        save_group.pack(fill='x', padx=15, pady=10)
        ttk.Radiobutton(save_group, text="in same location of origin file", variable=self.model.save_option).pack(fill='x', pady=3)
        ttk.Radiobutton(save_group, text="ask every time", variable=self.model.save_option, value=2).pack(fill='x', pady=3)
        ttk.Radiobutton(save_group, text="in this location: ", variable=self.model.save_option, value=3, command=self.controler.change_settings).pack(fill='x')

        self.save_label = tk.Label(save_group, text="", fg="gray", justify='left',  bg="#FDFDFD", anchor='nw', wraplength=600)
        self.save_label.pack(fill='x', padx=(40, 0), anchor='nw', expand=True)

        _ = ttk.Frame(tab)
        ttk.Label(_, text="PDF tools v3.6", font=('default', 12, 'bold')).pack(pady=(68, 12))
        ttk.Button(_, text="check update", state='disabled').pack(padx=10, pady=12, ipadx=4)
        ttk.Label(_, text="https://github.com/youssefhoummad/pdf-tools/", foreground="dodgerblue1").pack(pady=10)
        ttk.Label(_, text="Copyrigth © youssef hoummad, All rights reserved", foreground="gray").pack()
        _.pack(fill='x')      

        return tab




if __name__ == '__main__':
    # multiprocessing.freeze_support() # for multiprecessing in windows	
    myappid = 'youssefhoummad.pdftools.4.0' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    window = tk.Tk()
    # window = TkinterDnD.Tk()

    window.iconbitmap(r'img/icon.ico')


    window.title('pdftools')
    styling(window)

    app = App(window, View, Model)
    app.mainloop()