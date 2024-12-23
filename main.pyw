import re
import sys
import tkinter as tk
from tkinter import ttk, filedialog
# from tkinter import font

sys.path.append('./libs') # pip install --target=./libs -r requirements.txt

from PIL import ImageTk
import sv_ttk
import darkdetect
import pywinstyles
from funcs import *


import pypdfium2 as pdfium



class Entry(ttk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        super().insert(0, placeholder)

        # Bind events for removing and adding placeholder
        self.bind("<FocusIn>", self.remove_placeholder)
        self.bind("<FocusOut>", self.add_placeholder)
        self.bind("<KeyRelease>", self.check_empty)



    def configure(self, *args, **kwargs):
        if kwargs.get("state") == "enable":
            super().config(state="enable")
            self.add_placeholder(None)

        if kwargs.get("state") == "disable":
            super().delete(0, tk.END)
            self.state(["!invalid"])
            super().config(state="disable")


    config = configure



    def validate_int(self, *_):
        """
        This method invalidates the entry if its content is not an integer
        """
        if validate_input(self.get()):
            self.state(["!invalid"])
        else:
            self.state(["invalid"])

 

    def remove_placeholder(self, event):
        """Remove placeholder text when the user clicks into the entry field."""

        color = self.tk.call("ttk::style", "lookup", "TEntry", "-foreground")
        if super().get() == self.placeholder:
            super().configure(foreground=color)
            self.delete(0, tk.END)
        
        self.validate_int()

    def add_placeholder(self, event):
        """Add placeholder text back if the entry is empty."""
        # self.bind("<FocusOut>", self.validate_int)

        if super().get() == "":
            super().configure(foreground='gray')
            self.insert(0, self.placeholder)

    def check_empty(self, event):
        """Check if the entry is empty and handle placeholder."""
        self.bind("<KeyRelease>", self.validate_int)

        if super().get() == "":
            self.add_placeholder(event)
        
        if super().get() == self.placeholder:
            self.remove_placeholder(event)
    
    def get(self):
        if super().get() == self.placeholder:
            return ""
        return super().get()
        



class GroupFrame(ttk.Frame):
    def __init__(self, parent, title, disc="Some  Description...", zoom=False, degree=False, *args,**kws):
        super().__init__(parent, *args, **kws)

        self._enable = False


        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill='x', expand=True, pady=2)

        self.title = ttk.Label(self.top_frame, text=title, font=('Segoe UI', 10, 'bold' ), foreground='gray')
        self.title.pack(side='left', fill='x')

        self.swich = ttk.Checkbutton(self.top_frame, text="", style="Switch.TCheckbutton", command=self.toggle)
        self.swich.pack(side='right', fill='x')    

        self.desc = ttk.Label(self, text=disc, foreground="gray")
        # self.desc.pack(fill='x', expand=True, pady=(0,6))

        self.entry = Entry(self, placeholder="Example: 1, 2, 6-12", state='disable')
        self.entry.pack(fill='x', expand=True)


        self.label_zoom = ttk.Label(self, text="Zoom level:", foreground="gray")
        self.scale_zoom = ttk.Scale(self, from_=1, to=8, state='disable')

        self.rotate_label = ttk.Label(self, text="Rotate direction:", foreground="gray")
        self.rotate_combobox = ttk.Combobox(self, values=[0, 90, 180, 270], state='disable')
        self.rotate_combobox.current(0)



        if zoom:
            self.label_zoom.pack(fill='x', expand=True, pady=(12,6), padx=2)
            self.scale_zoom.pack(fill='x', expand=True)

        if degree:
            self.rotate_label.pack(fill='x', expand=True, pady=(12,6), padx=2)
            self.rotate_combobox.pack(fill='x', expand=True)


    
    def toggle(self):
        self._enable = not self._enable
        color = self.tk.call("ttk::style", "lookup", "TLabel", "-foreground")

        if self._enable:
            self.title.configure(foreground=color)

            self.entry.configure(state='enable')
            self.desc.configure(foreground=color)

            self.scale_zoom.configure(state='enable')
            self.rotate_label.configure(foreground=color)

            self.rotate_combobox.configure(state='enable')
            self.rotate_label.configure(foreground=color)

        else:
            self.title.configure(foreground='gray')
            self.entry.configure(state='disable')
            self.desc.configure(foreground='gray')

            self.label_zoom.configure(foreground='gray')
            self.scale_zoom.configure(state='disable')
            
            self.rotate_label.configure(foreground='gray')
            self.rotate_combobox.configure(state='disable')

    @property
    def enable(self):
        return self._enable


    @property
    def astr(self):
        return self.entry.get()
    
    @property
    def pages(self):
        return parse_range(self.entry.get())
    
    @property
    def degree(self):
        return self.rotate_combobox.get()

    @property
    def zoom(self):
        self.scale_zoom.get()
        ...
    




class App:
    def __init__(self, parent, View):
        self.parent = parent


        self.scale = tk.IntVar(value=1)
        self.degree = tk.IntVar(value=0)
        self.save_option = tk.IntVar(value=1)
        self.theme = tk.StringVar(value='light')
        self.PDF = None

        self.view = View(self.parent, controler=self)
        self.view.setup(self)
        self.get_settings()


    def get_settings(self):
        settings = load_settings('settings.ini')
        if settings.get('Save', {}).get('option') == '2':
            self.save_option.set(2)
            self.view.save_label.configure(text=settings['Save']['location'])
        else:
            self.save_option.set(1)
        
        if settings.get('Save', {}).get('theme') == 'dark':
            self.view.set_dark_theme()
        elif settings.get('Save', {}).get('theme') == 'light':
            self.view.set_light_theme()
        else:  
            self.view.set_auto_theme()


    def select_pdf(self, path):
        self.PDF = pdfium.PdfDocument(path)
        self.view.file_info.config(text=f"{Path(path).name}\nPages: {len(self.PDF)}")
        self.show_preview()


    def get_output_path(self, src_path, is_file=True):
        save_option = self.save_option.get()

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
        self.view.split.entry.delete(0, 'end')
        self.view.delete.entry.delete(0, 'end')
        self.view.rotate.entry.delete(0, 'end')
        self.view.images.entry.delete(0, 'end')

        self.view.preview_canvas.delete('picture')

        self.view.treepdf.delete(*self.view.treepdf.get_children())
        self.view.treeimage.delete(*self.view.treeimage.get_children())

        self.view.file_info.config(text=f"No file selected \n")

        self.PDF = None


    def show_preview(self, event=None, astr=None):
        if not self.PDF: return
        page = 1 if not astr else int(re.findall(r'\d+', astr)[-1])

        if page > len(self.PDF) : 
            raise IndexError("Failed to load page.")
        
        self.view.preview_canvas.delete('picture')

        bitmap = self.PDF[page-1].render(scale=1, rotation=0)
        image  = bitmap.to_pil()
        image = image.resize((400, 520), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(image)
        self.view.preview_canvas.create_image(0, 0, anchor="nw", image=tk_image, tag='picture')
        self.view.preview_canvas.image = tk_image # for ignore garbage collection


    def apply(self):

        if self.view.notebook.index("current") == 3: # settings tab
            settings = {'Save': {'option': self.save_option.get(), 'location': self.view.save_label.cget("text"), 'theme': self.theme.get()}}
            print(settings)
            save_settings('settings.ini', settings)
            print("Settings saved!")
            return
    

        if self.view.notebook.index("current") == 2: # Convert images to pdf tab
            paths_imgs = [self.view.treeimage.item(item)['values'][1] for item in self.view.treeimage.get_children()]
            if not paths_imgs: return
            
            output_path = Path(self.get_output_path(paths_imgs[0], is_file=False))
            output_path = output_path.with_suffix('.pdf')
            images_pdfs(paths_imgs, output_path) # convert func

            return
        
        
        if not self.PDF:
            self.view.flasher.flash_titlebar(count=3, interval=0.2)
            return
        

        writer = pdfium.PdfDocument.new()
        paths = [self.view.treepdf.item(item)['values'][0] for item in self.view.treepdf.get_children()]


        if self.view.notebook.index("current") == 0: # tools tab
            rotated = False
            splited = False

            if self.view.images.enable:
                output_dir = self.get_output_path(paths[-1], is_file=False)
                pdf_images(self.PDF, self.view.images.astr, self.view.images.zoom, output_dir)


            if self.view.rotate:
                output_path = self.get_output_path(self.PDF._input)
                pdf_rotate(self.PDF, self.view.rotate.astr, self.view.rotate.degree)
                rotated = True


            if self.view.split or self.view.delete:
                output_path = self.get_output_path(self.PDF._input)

                pdf_split(self.PDF, self.view.split.astr, self.view.delete.astr, writer)
                splited = True


            if splited: 
                writer.save(output_path)
                return
            if rotated:
                self.PDF.save(output_path)
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



    def mainloop(self):
        self.parent.mainloop()




class View:
    def __init__(self, parent, controler):
        self.parent = parent

        self.app = controler
        self.validate_cmd = parent.register(validate_input)

        self.flasher = TitlebarFlasher(parent)


    def setup(self, controler):
        self.app = controler

        self.canvas_height = 520
        self.canvas_width= 400


        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(expand=True, fill='both', padx=16)

        self.notebook.add(self.tab_tools(), text=" Tools ")
        self.notebook.add(self.tab_merge(), text=" Merge ")
        self.notebook.add(self.tab_convert(), text=" Convert ")
        self.notebook.add(self.tab_settings(), text=" Settings ")

        ttk.Button(self.parent, text="Apply", command=self.app.apply, style = "Accent.TButton").pack(side="right", padx=22, pady=22, ipadx=30)
        ttk.Button(self.parent, text="clear", command=self.app.clear).pack(side="right", padx=5, pady=22, ipadx=20)

        self.file_info = tk.Label(self.parent, text=f"No file selected \n", fg="gray", bg=self.parent['bg'], justify='left', anchor='nw', wraplength=600)
        self.file_info.pack(side="left", padx=20, pady=22, anchor='nw', fill='x', expand=True)

                
                
        # self.parent.bind("<Configure>", self.on_resize)

        
    def tab_tools(self):
        tab_tools = ttk.Frame(self.parent)
        frame_left = ttk.Frame(tab_tools)
        frame_right = ttk.Frame(tab_tools)
        frame_bottom = ttk.Frame(tab_tools)

        self.split = GroupFrame(frame_left, title="Split")
        self.split.pack(fill='x', expand=True, pady=12)

        self.delete = GroupFrame(frame_left, title="Delete")
        self.delete.pack(fill='x', expand=True, pady=12)

        self.rotate = GroupFrame(frame_left, title="Rotate", degree=True)
        self.rotate.pack(fill='x', expand=True, pady=12)

        self.images = GroupFrame(frame_left, title="Images", zoom=True)
        self.images.pack(fill='x', expand=True, pady=12)
 

        self.preview_canvas = tk.Canvas(frame_right, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=1, highlightcolor='black')
        self.preview_canvas.bind('<Button-1>', self.add_pdf)
        self.preview_canvas.bind("<Enter>", lambda event: self.preview_canvas.config(bg="#F3F3F3"))
        self.preview_canvas.bind("<Leave>", lambda event: self.preview_canvas.config(bg="white"))


        self.preview_canvas.create_rectangle(30, 30, 370, 490, outline='gray', width=1,dash=(5, 5))
        self.preview_canvas.create_text(200, 250, text="click or drag file here",font=("Segoe UI", 12, 'italic'), fill="gray")
        apply_dnd(self.preview_canvas, self.on_drop_pdf)

        frame_left.grid(row=0, column=0, padx=(20,10), sticky='nw', pady=(20, 0))
        tab_tools.grid_columnconfigure(0, weight=1)
        frame_right.grid(row=0, column=1)
        frame_bottom.grid(row=1, column=0, columnspan=2, sticky='e')

        self.preview_canvas.pack(padx=10, pady=10, fill='both')

        return tab_tools


    def tab_merge(self):
        tab = ttk.Frame(self.parent)

        ttk.Label(tab, foreground ='gray', font=('Segoe UI', 10, 'italic') , text="PDF Merger: A user-friendly tool that allows you to easily combine multiple PDF files into a single document. \nDrag and drop your PDF files, rearrange them as needed.").pack(fill='x', padx=10, pady=20)

        _ = ttk.Frame(tab)
        _.pack(fill='x')


        def on_select(values):
            path, _ = values
            self.app.select_pdf(path)

        
        self.treepdf = Treeview(tab, on_select=on_select, on_drop=self.on_drop_pdf, columns=("A", "B"), show='headings')
        self.treepdf.column("# 1", stretch='yes')
        self.treepdf.heading("# 1", text="path", anchor='w')
        self.treepdf.column("# 2",anchor='e', stretch='no', width=80)
        self.treepdf.heading("# 2", text="pages")

        ttk.Button(_, text="Add file", command=self.add_pdf, style='Accent.TButton').pack(padx=10, anchor='nw', side='left', ipadx=15)

        ttk.Button(_, text="Up", command=self.treepdf.move_up, style='Left.TButton').pack(anchor='nw', side='right', padx=(0,12))
        ttk.Button(_, text="Down", command=self.treepdf.move_down, style='Middle.TButton').pack(anchor='nw', side='right', padx=6)
        ttk.Button(_, text="remove", command=self.treepdf.remove_item, style='Right.TButton').pack(anchor='nw', side='right')

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

        ttk.Button(_, text="Add file", command=self.add_img, style='Accent.TButton').pack(padx=10, anchor='nw', side='left', ipadx=15)
        ttk.Button(_, text="Up", command=self.treeimage.move_up).pack(anchor='nw', side='right',  padx=(0,12))
        ttk.Button(_, text="Down", command=self.treeimage.move_down).pack(  anchor='nw', side='right', padx=6)
        ttk.Button(_, text="remove", command=self.treeimage.remove_item).pack(  anchor='nw', side='right')


        self.treeimage.pack(fill='both', expand=True, padx=10, pady=10)

        return tab


    def tab_settings(self):
        tab = ttk.Frame(self.parent)

        save_group = ttk.Frame(tab)
        save_group.pack(fill='x', padx=15, pady=10, anchor='nw')

        ttk.Label(save_group, text="Save Location", font=('Segoe UI', 10, 'bold' )).pack(fill='x', pady=12)

        ttk.Radiobutton(save_group, text="in same location of origin file", variable=self.app.save_option, value=1).pack(fill='x', pady=3)
        ttk.Radiobutton(save_group, text="in this location: ", variable=self.app.save_option, value=2, command=self.custom_location).pack(fill='x', pady=3)

        self.save_label = ttk.Label(save_group, text="", foreground="gray", wraplength=600)
        self.save_label.pack(fill='x', padx=(40, 0), expand=True)

        theme_group = ttk.Frame(tab)
        theme_group.pack(fill='x', padx=15, pady=10, anchor='nw')

        ttk.Label(theme_group, text="theme", font=('Segoe UI', 10, 'bold' )).pack(fill='x', pady=12)

        ttk.Radiobutton(theme_group, text="Light", variable=self.app.theme, value='light', command=self.set_light_theme).pack(fill='x', pady=3)
        ttk.Radiobutton(theme_group, text="Dark", variable=self.app.theme, value='dark', command=self.set_dark_theme).pack(fill='x', pady=3)
        ttk.Radiobutton(theme_group, text="System", variable=self.app.theme, value='auto', command=self.set_auto_theme).pack(fill='x', pady=3)


        _ = ttk.Frame(tab)
        ttk.Label(_, text="PDF tools v4.0", font=('default', 12, 'bold')).pack(pady=(68, 12))
        ttk.Label(_, text="https://github.com/youssefhoummad/pdf-tools/", foreground="dodgerblue1").pack(pady=10)
        ttk.Label(_, text="Copyrigth © youssef hoummad, All rights reserved", foreground="gray").pack()
        _.pack(fill='x', anchor='n', expand=True)      

        return tab


    def add_pdf(self, *args, **kws):
        path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
        if not path: return

        path = r'{}'.format(path) # convert to raw

        self.app.select_pdf(path)
        self.treepdf.insert("", 'end', values=(path,len(self.app.PDF)))


    def add_img(self, *args, **kws):
        path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("Images files", ("*.jpg", "*.jpeg", "*.png"))])
        if not path: return

        path = r'{}'.format(path) # convert to raw

        self.treeimage.insert("", 'end', values=(Path(path).name, path))


    def on_drop_pdf(self, event, *args):
        for path in event:
            if path.lower().endswith('.pdf'):
                self.app.select_pdf(path)
                self.treepdf.insert("", 'end', values=(path,len(self.app.PDF)))


    def on_drop_img(self, event, *args, **kws):
        for path in event:
            if path.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.treeimage.insert("", 'end', values=(Path(path).name, path))


    def set_light_theme(self):
        self.app.theme.set('light')
        sv_ttk.use_light_theme()
        self.parent.config(bg='#EBF0F5')
        pywinstyles.change_header_color(window=self.parent, color='#EBF0F5')
        pywinstyles.change_title_color(window=self.parent, color='#EBF0F5')
        self.file_info.config(background='#EBF0F5')
        self.preview_canvas.config(bg='white')
        self.preview_canvas.bind("<Enter>", lambda event: self.preview_canvas.config(bg="#F3F3F3"))
        self.preview_canvas.bind("<Leave>", lambda event: self.preview_canvas.config(bg="white"))


    def set_dark_theme(self):
        self.app.theme.set('dark')
        sv_ttk.use_dark_theme()
        self.parent.config(bg='#141414')
        pywinstyles.change_header_color(window=self.parent, color='#141414')
        pywinstyles.change_title_color(window=self.parent, color='#141414')
        self.file_info.config(background='#141414')
        self.preview_canvas.config(bg='#1c1c1c')
        self.preview_canvas.bind("<Enter>", lambda event: self.preview_canvas.config(bg="#212121"))
        self.preview_canvas.bind("<Leave>", lambda event: self.preview_canvas.config(bg="#1c1c1c"))


    def set_auto_theme(self):
        if darkdetect.isDark(): self.set_dark_theme()
        else: self.set_light_theme()
        self.app.theme.set('auto')


    def custom_location(self):
        save_location = filedialog.askdirectory()
        if not save_location: return
        save_location = Path(save_location) 
        self.save_label.configure(text=save_location)


    def on_resize(self, *_):
        print(f"resizing...{self.parent.winfo_height()}")
    

if __name__ == '__main__':
    # multiprocessing.freeze_support() # for multiprecessing in windows	

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('youssefhoummad.pdftools.4.0') # show icon in taskbar
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    window = tk.Tk()

    window.iconbitmap(r'img/icon.ico')
    window.title('pdftools')

    app = App(window, View)    
    app.mainloop()
