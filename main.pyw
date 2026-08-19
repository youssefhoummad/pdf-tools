import re
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from widgets import Combobox, Treeview, Entry, apply_dnd, InfoBar

# sys.path.append('./libs') # pip install --target=./libs -r requirements.txt

from PIL import ImageTk

import pypdfium2 as pdfium

from funcs import *

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class GroupFrame(ttk.Frame):

    def __init__(self, parent, title, on_entry_change=None, zoom=False, degree=False, *args,**kws):
        super().__init__(parent, *args, **kws)


        self.on_entry_change = on_entry_change
        self.title_str = title

        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill='x', expand=True, pady=2)

        self.title = ttk.Label(self.top_frame, text=title, font=('Segoe UI', 10, 'bold' ))
        self.title.pack(side='left', fill='x')

        self.entry = Entry(self, placeholder="Example: 1, 2, 6-12")
        self.entry.pack(fill='x', expand=True, ipady=1)
        self.entry.bind("<KeyRelease>", self._cmd_on_change, add="+") # Add a <KeyRelease> event binding without overriding existing bindings
        self._debounce_id = None

        zoom_container = ttk.Frame(self)
        self.label_zoom = ttk.Label(zoom_container, text=f"Zoom 1:")
        self.scale_zoom = ttk.Scale(zoom_container, from_=1, to=8, orient='horizontal', command=self._sync_zoom) 

        self.rotate_combobox = Combobox(self, placeholder='Choose direction...', values=[90, 180, 270] )
        # self.rotate_combobox.config() 
  

        if zoom:
            self.label_zoom.pack(side='left', padx=(0,6))
            self.scale_zoom.pack(fill='x', expand=True, side='left')
            zoom_container.pack(fill='x', expand=True, pady=(12,6))

        if degree:
            self.rotate_combobox.pack(fill='x', expand=True, pady=(12,6), ipadx=1)
    

    def _cmd_on_change(self, *_):
        if not self.on_entry_change:
            return
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(150, lambda: self.on_entry_change(astr=self.entry.get()))
        

    def _sync_zoom(self, *_):
        self.label_zoom.config(text=f'Zoom {int(self.scale_zoom.get())}:')




    @property
    def enable(self):
        if self.entry.get().strip() == "":
            # print(f"{self.title_str} is disabled")
            return False
        return True


    @property
    def astr(self):
        return self.entry.get()
    

    @property
    def pages(self):
        return parse_range(self.entry.get())
    
    @property
    def last_entry(self):
        return self.pages[-1]

    @property
    def degree(self):
        return self.rotate_combobox.get()


    @property
    def zoom(self):
        return self.scale_zoom.get()
        



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
        settings = load_settings(os.path.join(BASE_DIR, 'settings.ini'))
        if settings.get('Save', {}).get('option') == '2':
            self.save_option.set(2)
            self.view.save_label.configure(text=settings['Save']['location'])
        else:
            self.save_option.set(1)
        



    def select_pdf(self, path):
        self.PDF = pdfium.PdfDocument(path)
        self._last_preview_page = None
        self.view.file_info.config(text=f"{Path(path).name}\nPages: {len(self.PDF)}")
        self.show_preview()


    def get_output_path(self, src_path, is_file=True):
        save_option = self.save_option.get()

        # Option 1: Default save location
        if save_option == 1:
            return set_output_file(src_path, 'new') if is_file else set_output_dir(src_path)

        # Option 2: Load location from settings.ini
        elif save_option == 2:
            save_location = Path(load_settings(os.path.join(BASE_DIR, 'settings.ini'))['Save']['location'])
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

        if self.PDF: 
            self.PDF.close()
            self.PDF = None


    def show_preview(self, event=None, astr=None):
        if not self.PDF: return

        digits = re.findall(r'\d+', astr) if astr else []
        page = int(digits[-1]) if digits else 1
        if page > len(self.PDF):
            InfoBar(self.parent, title="Warning", info_type='warning', text=f"page must be less than {len(self.PDF)}").show()
        page = max(1, min(page, len(self.PDF)))

        if page == getattr(self, '_last_preview_page', None):
            return
        self._last_preview_page = page

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
            save_settings(os.path.join(BASE_DIR, 'settings.ini'), settings)
            InfoBar(self.parent, title="success", text="All settings saved :)").show()
            return
    

        if self.view.notebook.index("current") == 2: # Convert images to pdf tab
            paths_imgs = [self.view.treeimage.item(item)['values'][1] for item in self.view.treeimage.get_children()]
            if not paths_imgs: return
            
            output_path = Path(self.get_output_path(paths_imgs[0], is_file=False))
            output_path = output_path.with_suffix('.pdf')
            images_pdfs(paths_imgs, output_path) # convert func

            return
        
        
        if not self.PDF:
            return
        

        writer = pdfium.PdfDocument.new()
        paths = [self.view.treepdf.item(item)['values'][0] for item in self.view.treepdf.get_children()]


        if self.view.notebook.index("current") == 0: # tools tab
            if not self.view.images.enable and not self.view.split.enable and not self.view.rotate.enable and not self.view.delete.enable:
                return

            rotated = False
            splited = False

            if self.view.images.enable:
                output_dir = self.get_output_path(paths[-1], is_file=False)
                pdf_images(self.PDF, self.view.images.astr, self.view.images.zoom, output_dir)


            if self.view.rotate:
                if self.view.rotate.rotate_combobox.get() == "":
                    # print("NO DEGREE CHOOSEN")
                    return False
                output_path = self.get_output_path(self.PDF._input)
                pdf_rotate(self.PDF, self.view.rotate.astr, self.view.rotate.degree)
                rotated = True


            if self.view.split or self.view.delete:
                output_path = self.get_output_path(self.PDF._input)

                pdf_split(self.PDF, self.view.split.astr, self.view.delete.astr, writer)
                splited = True


            if splited: 
                writer.save(output_path)
                InfoBar(self.parent, title="success", text=f"The new PDF saved in: \n {output_path})").show()

                return
            if rotated:
                self.PDF.save(output_path)
                # InfoBar(self.parent, title="success", text="All settings saved :)").show()

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

            InfoBar(self.parent, title="success", text=f"All files merged in:\n {output_path}").show()
            return





    def mainloop(self):
        self.parent.mainloop()





class View:
    def __init__(self, parent, controler):
        self.parent = parent
        self.app = controler

    def setup(self, controler):
        self.app = controler

        self.canvas_height = 520
        self.canvas_width= 400

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(expand=True, fill='both', padx=8, pady=0)

        self.notebook.add(self.tab_tools(), text="Tools")
        self.notebook.add(self.tab_merge(), text="Merge")
        self.notebook.add(self.tab_convert(), text="Convert")
        self.notebook.add(self.tab_settings(), text="Settings")

        ttk.Button(self.parent, text="Apply", command=self.app.apply).pack(side="right", padx=10, pady=22, ipadx=16, ipady=2)
        ttk.Button(self.parent, text="clear", command=self.app.clear).pack(side="right", pady=22, ipadx=4, ipady=2)

        self.file_info = tk.Label(self.parent, text=f"No file selected \n", fg="gray", bg=self.parent['bg'], justify='left', anchor='nw', wraplength=600)
        self.file_info.pack(side="left", padx=20, pady=22, anchor='nw', fill='x', expand=True)

                
                
        # self.parent.bind("<Configure>", self.on_resize)

        
    def tab_tools(self):
        tab_tools = ttk.Frame(self.parent)
        frame_left = ttk.Frame(tab_tools)
        frame_right = ttk.Frame(tab_tools)
        frame_bottom = ttk.Frame(tab_tools)

        self.split = GroupFrame(frame_left, title="Split", on_entry_change=self.app.show_preview)
        self.split.pack(fill='x', expand=True, pady=12)

        self.delete = GroupFrame(frame_left, title="Delete", on_entry_change=self.app.show_preview)
        self.delete.pack(fill='x', expand=True, pady=12)

        self.rotate = GroupFrame(frame_left, title="Rotate", degree=True, on_entry_change=self.app.show_preview)
        self.rotate.pack(fill='x', expand=True, pady=12)

        self.images = GroupFrame(frame_left, title="Images", zoom=True, on_entry_change=self.app.show_preview)
        self.images.pack(fill='x', expand=True, pady=12)

        self.preview_canvas = tk.Canvas(frame_right, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=1, highlightcolor='black')
        self.preview_canvas.config(cursor="hand2")
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
        
        self.treepdf = Treeview(tab, on_select=on_select, columns=("A", "B"), show='headings')
        apply_dnd(self.treepdf, self.on_drop_pdf) # on_drop=self.on_drop_pdf,
        self.treepdf.column("# 1", stretch='yes')
        self.treepdf.heading("# 1", text="path", anchor='w')
        self.treepdf.column("# 2",anchor='e', stretch='no', width=80)
        self.treepdf.heading("# 2", text="pages")

        ttk.Button(_, text="Add file", command=self.add_pdf).pack(padx=10, anchor='nw', side='left', ipadx=15, ipady=1)

        ttk.Button(_, text=u"\ue971", command=self.treepdf.move_up).pack(anchor='nw', side='right', padx=(0,12), ipady=1)
        ttk.Button(_, text=u"\ue972", command=self.treepdf.move_down).pack(anchor='nw', side='right', padx=6, ipady=1)
        ttk.Button(_, text=u"\ue74d", command=self.treepdf.remove_item).pack(anchor='nw', side='right', ipady=1)

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
        
        self.treeimage = Treeview(tab, on_select=on_select, columns=("A", "B"), show='headings')
        apply_dnd(self.treeimage, self.on_drop_img)
        self.treeimage.column("# 1",anchor='w', stretch='no', width=200)
        self.treeimage.heading("# 1", text="filename")
        self.treeimage.column("# 2", stretch='yes')
        self.treeimage.heading("# 2", text="path", anchor='w')

        ttk.Button(_, text="Add file", command=self.add_img, style='Accent.TButton').pack(padx=10, anchor='nw', side='left', ipadx=15, ipady=1)
        ttk.Button(_, text=u"\ue971", command=self.treeimage.move_up).pack(anchor='nw', side='right',  padx=(0,12), ipady=1)
        ttk.Button(_, text=u"\ue972", command=self.treeimage.move_down).pack(  anchor='nw', side='right', padx=6, ipady=1)
        ttk.Button(_, text=u"\ue74d", command=self.treeimage.remove_item).pack(  anchor='nw', side='right', ipady=1)

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


    def custom_location(self):
        save_location = filedialog.askdirectory()
        if not save_location: return
        save_location = Path(save_location) 
        self.save_label.configure(text=save_location)


    def on_resize(self, *_):
        print(f"resizing...{self.parent.winfo_height()}")






if __name__ == '__main__':


    window = tk.Tk()
    window.geometry("650x650")
    window.resizable(False, False)
    window.iconbitmap(os.path.join(BASE_DIR, 'img', 'icon.ico'))    window.title('pdftools')
    styling_tkinter(window)

    app = App(window, View)    
    app.mainloop()
