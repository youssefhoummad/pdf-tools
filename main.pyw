import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage

from widgets import Combobox, Treeview, Entry, apply_dnd ,InfoBar

# sys.path.append('./libs') # pip install --target=./libs -r requirements.txt

from PIL import ImageTk

import pypdfium2 as pdfium

from funcs import *



STRINGS = {
    'en': {
        'app_title': 'pdftools',
        'tab_tools': 'Tools',
        'tab_merge': 'Merge',
        'tab_convert': 'Convert',
        'tab_settings': 'Settings',
        'group_split': 'Split',
        'group_delete': 'Delete',
        'group_rotate': 'Rotate',
        'group_images': 'Images',
        'placeholder_range': 'Example: 1, 2, 6-12',
        'placeholder_direction': 'Choose direction...',
        'zoom_label': 'Zoom',
        'btn_apply': 'Apply',
        'btn_clear': 'clear',
        'btn_add_file': 'Add file',
        'no_file_selected': 'No file selected \n',
        'drop_hint': 'click or drag file here',
        'merge_desc': ("PDF Merger: A user-friendly tool that allows you to easily combine "
                        "multiple PDF files into a single document. \n"
                        "Drag and drop your PDF files, rearrange them as needed."),
        'convert_desc': ("Image to PDF Converter: A user-friendly tool that allows you to easily "
                          "convert and combine multiple images \n"
                          "into a single, high-quality PDF file with drag-and-drop functionality."),
        'col_path': 'path',
        'col_pages': 'pages',
        'col_filename': 'filename',
        'save_location': 'Save Location',
        'save_same_location': 'in same location of origin file',
        'save_custom_location': 'in this location: ',
        'settings_language': 'Language',
        'lang_ar': 'Arabic',
        'lang_en': 'English',
        'restart_note': 'Restart the app for the language change to take effect.',
        'pages_count': 'Pages: ',
        'warning_title': 'Warning',
        'page_less_than': 'page must be less than ',
        'success_title': 'success',
        'settings_saved': 'All settings saved :)',
        'pdf_saved_in': 'The new PDF saved in:\n\n',
        'files_merged_in': 'All files merged in:\n\n',
        'copyright': 'Copyright © Youssef Hoummad, All rights reserved',
        'select_pdf_title': 'Select PDF File',
        'select_image_title': 'Select Image File',
    },
    'ar': {
        'app_title': 'أدوات PDF',
        'tab_tools': 'أدوات',
        'tab_merge': 'دمج',
        'tab_convert': 'تحويل',
        'tab_settings': 'إعدادات',
        'group_split': 'تقسيم',
        'group_delete': 'حذف',
        'group_rotate': 'تدوير',
        'group_images': 'صور',
        'placeholder_range': 'مثال: 1, 2, 6-12',
        'placeholder_direction': '...اختر الاتجاه',
        'zoom_label': 'تكبير ',
        'btn_apply': 'تطبيق',
        'btn_clear': 'مسح',
        'btn_add_file': 'إضافة ملف',
        'no_file_selected': 'لم يتم اختيار ملف \n',
        'drop_hint': 'اضغط أو اسحب الملف هنا',
        'merge_desc': ("دمج PDF: أداة سهلة الاستخدام تتيح لك دمج عدة ملفات PDF في مستند واحد بسهولة.\n"
                        "اسحب وأفلت ملفاتك، ورتّبها كما تشاء."),
        'convert_desc': ("تحويل الصور إلى PDF: أداة سهلة الاستخدام تتيح لك تحويل ودمج عدة صور\n"
                          "في ملف PDF واحد عالي الجودة بالسحب والإفلات."),
        'col_path': 'المسار',
        'col_pages': 'الصفحات',
        'col_filename': 'اسم الملف',
        'save_location': 'مكان الحفظ',
        'save_same_location': 'في نفس مكان الملف الأصلي ',
        'save_custom_location': ': في هذا المكان ',
        'settings_language': 'اللغة',
        'lang_auto': 'تلقائي (حسب النظام)',
        'lang_ar': 'العربية ',
        'lang_en': 'الإنجليزية ',
        'restart_note': 'أعد تشغيل البرنامج لتطبيق تغيير اللغة.',
        'pages_count': 'الصفحات: ',
        'warning_title': 'تحذير',
        'page_less_than': 'رقم الصفحات يجب أن يكون أقل من ',
        'success_title': 'نجاح',
        'settings_saved': 'حُفظ مكان التخزين',
        'pdf_saved_in': ':حًفظ الملف الجديد في \n\n',
        'files_merged_in': ':دُمجت الملفات في\n\n',
        'copyright': 'Copyright © Youssef Hoummad, All rights reserved',

    },
}
 
 
 
def t(key):
    """يرجع النص المترجم للمفتاح المعطى حسب اللغة الحالية المحمَّلة."""
    return STRINGS.get(CURRENT_LANG, STRINGS['en']).get(key, key)
 

CURRENT_LANG = 'en'
rtl = False

LEFT, RIGHT, W, E, NW, NE = 'left', 'right', 'w', 'e', 'nw', 'ne'
PADX = (20,10)

SAVE_LOCATION = ''


def change_lang(lang):
    global LEFT, RIGHT, W, E, NW, NE, PADX, rtl, CURRENT_LANG

    CURRENT_LANG = 'en'
    rtl = False

    LEFT, RIGHT, W, E, NW, NE = 'left', 'right', 'w', 'e', 'nw', 'ne'
    PADX = (20,10)

    if lang == 'ar':
        LEFT, RIGHT, W, E, NW, NE = RIGHT, LEFT, E, W, NE, NW
        PADX = PADX[1], PADX[0]
        rtl = True
        CURRENT_LANG = 'ar'





def get_settings():
    global SAVE_LOCATION

    settings = load_settings('settings.ini')
    SAVE_LOCATION = settings.get('SAVE', {}).get('custom_div')

    CURRENT_LANG = settings.get('LANG', {}).get('current_lang')
    change_lang(CURRENT_LANG)




class GroupFrame(ttk.Frame):

    def __init__(self, parent, title, on_entry_change=None, zoom=False, degree=False, *args,**kws):
        super().__init__(parent, *args, **kws)


        self.on_entry_change = on_entry_change
        self.title_str = title

        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill='x', expand=True, pady=2)

        self.title = ttk.Label(self.top_frame, text=title, font=('Segoe UI', 10, 'bold' ))
        self.title.pack(side=LEFT, fill='x', pady=(0, 8))

        self.entry = Entry(self, placeholder=t('placeholder_range'))
        self.entry.pack(fill='x', expand=True, ipady=1)
        self.entry.bind("<KeyRelease>", self._cmd_on_change, add="+") # Add a <KeyRelease> event binding without overriding existing bindings
        self._debounce_id = None

        zoom_container = ttk.Frame(self)
        self.label_zoom = ttk.Label(zoom_container, text=t('zoom_label'), justify=LEFT)
        self.scale_zoom = ttk.Scale(zoom_container, from_=1, to=8, orient='horizontal', command=self._sync_zoom) 

        self.rotate_combobox = Combobox(self, placeholder=t('placeholder_direction'), values=[90, 180, 270] )
  

        if zoom:
            self.label_zoom.pack(side=LEFT, anchor=NE)
            self.scale_zoom.pack(fill='x', expand=True, side=LEFT)
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
        self.label_zoom.config(text=f'{t('zoom_label')} {int(self.scale_zoom.get())}:')




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
        self.save_location = tk.StringVar(value="")
        self.current_lang = tk.StringVar(value='en')
        
        self.PDF = None

        self.view = View(self.parent, controller=self)
        self.view.setup(self)

        self._preview_cache = {}   # {page_number: tk_image}


        # settings
        if SAVE_LOCATION:
            self.save_location.set('custom')
        else:
            self.save_location.set('')

        self.current_lang.set(CURRENT_LANG)

        
    def select_pdf(self, path):
        if self.PDF:
            self.PDF.close()
        self._last_preview_page = None
        self.PDF = pdfium.PdfDocument(path)
        self._preview_cache = {}
        self.view.file_info.config(text=f"{Path(path).name}\n {t("pages_count")} {len(self.PDF)}")
        self.show_preview()


    def get_output_path(self, src_path, is_file=True):

        # Option 1: Default save location
        if SAVE_LOCATION :
            save_location = Path(SAVE_LOCATION)
            if not is_file:
                output_dir = save_location / 'images'
                output_dir.mkdir(parents=True, exist_ok=True)
                return output_dir
            if is_file:
                return save_location / Path(src_path).name

        else:
            return set_output_file(src_path, 'new') if is_file else set_output_dir(src_path)


    def clear(self):
        self.view.split.entry.delete(0, 'end')
        self.view.delete.entry.delete(0, 'end')
        self.view.rotate.entry.delete(0, 'end')
        self.view.images.entry.delete(0, 'end')

        self.view.preview_canvas.delete('picture')

        self.view.treepdf.delete(*self.view.treepdf.get_children())
        self.view.treeimage.delete(*self.view.treeimage.get_children())

        self.view.file_info.config(text=t('no_file_selected'))

        self._preview_cache = {}
        self._last_preview_page = None


        if self.PDF: 
            self.PDF.close()
            self.PDF = None


    def show_preview(self, event=None, astr=None):
        if not self.PDF: return

        digits = re.findall(r'\d+', astr) if astr else []
        page = int(digits[-1]) if digits else 1
        if page > len(self.PDF):
            InfoBar(self.parent, title=t("warning_title"), info_type='warning', text=f"{t('page_less_than')} {len(self.PDF)}", rtl=rtl).show()
        page = max(1, min(page, len(self.PDF)))

        if page == getattr(self, '_last_preview_page', None):
            return

        if page in self._preview_cache:
            tk_image = self._preview_cache[page]
        else:
            page_obj = self.PDF[page-1]
            target_width = 380
            scale = target_width / page_obj.get_width()   # get_width() متوفرة في pypdfium2
            
            bitmap = page_obj.render(scale=scale, rotation=0)
            image = bitmap.to_pil()
            tk_image = ImageTk.PhotoImage(image)
      
            self._preview_cache[page] = tk_image





        self.view.preview_canvas.delete('picture')
        self._last_preview_page = page
        self.view.preview_canvas.create_image(0, 0, anchor='nw', image=tk_image, tag='picture')
        self.view.preview_canvas.image = tk_image # for ignore garbage collection


    def apply(self):
        current_tab_id = self.view.notebook.index("current")
        current_tab_name =  self.view.notebook.tab(current_tab_id, "text")


        if current_tab_name == t('tab_settings'):
            global SAVE_LOCATION
            if not self.save_location.get():
                SAVE_LOCATION = ''
            else:
                SAVE_LOCATION = self.save_location.get()
                self.save_location.set('custom')


            settings = {'SAVE': {'custom_div': SAVE_LOCATION}, 'LANG': {'current_lang': self.current_lang.get()}}
            save_settings('settings.ini', settings)

            if CURRENT_LANG != self.current_lang.get():
                messagebox.showinfo(
                    title=t('warning_title'),
                    message=t('restart_note')
                )
                self.parent.quit()


            InfoBar(self.parent, title=t('success_title'), text=f"{t('settings_saved')}", rtl=rtl).show()

            return
    

        if current_tab_name == t('tab_convert'):
            paths_imgs = [self.view.treeimage.item(item)['values'][1] for item in self.view.treeimage.get_children()]
            if not paths_imgs: return
            
            output_path = Path(self.get_output_path(paths_imgs[0], is_file=False))
            output_path = output_path.with_suffix('.pdf')
            images_pdfs(paths_imgs, output_path) # convert func

            InfoBar(self.parent, title=t('success_title'), text=f"{t('pdf_saved_in')} {output_path}", rtl=rtl).show()

            return
        
        
        if not self.PDF: return

        writer = pdfium.PdfDocument.new()
        paths = [self.view.treepdf.item(item)['values'][0] for item in self.view.treepdf.get_children()]


        if current_tab_name == t('tab_tools'):
            if not self.view.images.enable and not self.view.split.enable and not self.view.rotate.enable and not self.view.delete.enable:
                return

            rotated = False
            splited = False

            if self.view.images.enable:
                output_dir = self.get_output_path(paths[-1], is_file=False)
                pdf_images(self.PDF, self.view.images.astr, self.view.images.zoom, output_dir)


            if self.view.rotate.enable:
                if self.view.rotate.rotate_combobox.get() == "":
                    # print("NO DEGREE CHOOSEN")
                    return False
                output_path = self.get_output_path(self.PDF._input)
                pdf_rotate(self.PDF, self.view.rotate.astr, self.view.rotate.degree)
                rotated = True


            if self.view.split.enable or self.view.delete.enable:
                output_path = self.get_output_path(self.PDF._input)

                pdf_split(self.PDF, self.view.split.astr, self.view.delete.astr, writer)
                splited = True


            if splited: 
                writer.save(output_path)
                InfoBar(self.parent, title=t('success_title'), text=f"{t('pdf_saved_in')} {output_path}", rtl=rtl).show()
                return
            
            if rotated:
                self.PDF.save(output_path)
                if not splited:
                    InfoBar(self.parent, title=t('success_title'), text=f"{t('pdf_saved_in')} {output_path}", rtl=rtl).show()
                return
            

        if current_tab_name == t('tab_merge'):
            if not paths: return
            output_path = self.get_output_path(paths[0])

            writer = pdfium.PdfDocument.new()
            
            for pdf_path in paths:
                with pdfium.PdfDocument(pdf_path) as src_pdf:
                    writer.import_pages(src_pdf)
            writer.save(output_path)

            InfoBar(self.parent, title=t('success_title'), text=f"{t('files_merged_in')} {output_path}", rtl=rtl).show()
            return


    def mainloop(self):
        self.parent.mainloop()





class View:
    def __init__(self, parent, controller):
        self.parent = parent
        self.app = controller


    def setup(self, controller):
        self.app = controller

        self.canvas_height = 520
        self.canvas_width= 400

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(expand=True, fill='both', padx=8, pady=0)

        self.notebook.add(self.tab_tools(), text=t('tab_tools'), padding=10)
        self.notebook.add(self.tab_merge(), text=t('tab_merge'), padding=10)
        self.notebook.add(self.tab_convert(), text=t('tab_convert'), padding=10)
        self.notebook.add(self.tab_settings(), text=t('tab_settings'), padding=10)

        ttk.Button(self.parent, text=t('btn_apply'), command=self.app.apply).pack(side=RIGHT, padx=10, ipadx=8)
        ttk.Button(self.parent, text=t('btn_clear'), command=self.app.clear).pack(side=RIGHT)

        self.file_info = tk.Label(self.parent, text=t('no_file_selected'), fg="gray", bg=self.parent['bg'], justify=LEFT, anchor=NW, wraplength=600)
        self.file_info.pack(side=LEFT, padx=20, pady=22, fill='x', expand=True)


        if rtl:
            current_tabs = self.notebook.tabs() # Returns a list of widget names            
            for index, tab_id in enumerate(reversed(current_tabs)):
                self.notebook.insert(index, tab_id)


    def tab_tools(self):
        tab_tools = ttk.Frame(self.parent)
        frame_left = ttk.Frame(tab_tools)
        frame_right = ttk.Frame(tab_tools)
        frame_bottom = ttk.Frame(tab_tools)

        self.split = GroupFrame(frame_left, title=t('group_split'), on_entry_change=self.app.show_preview)
        self.split.pack(fill='x', expand=True, pady=12)

        self.delete = GroupFrame(frame_left, title=t('group_delete'), on_entry_change=self.app.show_preview)
        self.delete.pack(fill='x', expand=True, pady=12)

        self.rotate = GroupFrame(frame_left, title=t('group_rotate'), degree=True, on_entry_change=self.app.show_preview)
        self.rotate.pack(fill='x', expand=True, pady=12)

        self.images = GroupFrame(frame_left, title=t('group_images'), zoom=True, on_entry_change=self.app.show_preview)
        self.images.pack(fill='x', expand=True, pady=12)

        self.preview_canvas = tk.Canvas(frame_right, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=1, highlightcolor='black')
        self.preview_canvas.config(cursor="hand2")
        self.preview_canvas.bind('<Button-1>', self.add_pdf)
        self.preview_canvas.bind("<Enter>", lambda event: self.preview_canvas.config(bg="#F3F3F3"))
        self.preview_canvas.bind("<Leave>", lambda event: self.preview_canvas.config(bg="white"))

        self.preview_canvas.create_rectangle(30, 30, 370, 490, outline='gray', width=1,dash=(5, 5))
        self.preview_canvas.create_text(200, 250, text=t('drop_hint'),font=("Segoe UI", 12, 'italic'), fill="gray")
        apply_dnd(self.preview_canvas, self.on_drop_pdf)


        col_start = 1 if rtl else 0
        col_end = 0 if rtl else 1
        padx = (10, 0) if rtl else (0, 10)


        frame_left.grid(row=0, column=col_start, sticky=NW+E, padx=padx)
        tab_tools.grid_columnconfigure(col_start, weight=1)
        frame_right.grid(row=0, column=col_end, sticky=W)
        frame_bottom.grid(row=1, column=0, columnspan=2, sticky=E)

        self.preview_canvas.pack(fill='both')

        return tab_tools


    def tab_merge(self):
        tab = ttk.Frame(self.parent)

        ttk.Label(tab, foreground ='gray' , text=t('merge_desc'), justify=LEFT).pack(fill='x', pady=20)

        _ = ttk.Frame(tab)
        _.pack(fill='x', pady=(0,6))

        def on_select(values):
            path, _ = values
            self.app.select_pdf(path)
        
        self.treepdf = Treeview(tab, on_select=on_select, columns=("A", "B"), show='headings')
        apply_dnd(self.treepdf, self.on_drop_pdf) 


        self.treepdf.column("# 1", stretch='yes')
        self.treepdf.heading("# 1", text=t("col_path"), anchor=W)

        self.treepdf.column("# 2",anchor='e', stretch='no', width=80)
        self.treepdf.heading("# 2", text=t('col_pages'))

        ttk.Button(_, text=t("btn_add_file"), command=self.add_pdf).pack(side=LEFT, ipadx=15)

        ttk.Button(_, text=u"\ue971", command=self.treepdf.move_up).pack(side=RIGHT)
        ttk.Button(_, text=u"\ue972", command=self.treepdf.move_down).pack(side=RIGHT, padx=6)
        ttk.Button(_, text=u"\ue74d", command=self.treepdf.remove_item).pack(side=RIGHT)

        self.treepdf.pack(fill='both', expand=True, anchor=NW)
        
        return tab


    def tab_convert(self):
        tab = ttk.Frame(self.parent)
        ttk.Label(tab, foreground ='gray', text=t('convert_desc'), justify=LEFT, anchor=W).pack(fill='x', pady=20, anchor=W)

        _ = ttk.Frame(tab)
        _.pack(fill='x', pady=(0,6))

        def on_select(value):
            filename , path = value
            print("Show preview of image: ", filename)
        
        self.treeimage = Treeview(tab, on_select=on_select, columns=("A", "B"), show='headings')
        apply_dnd(self.treeimage, self.on_drop_img)
        self.treeimage.column("# 1",anchor=W, stretch='no', width=200)
        self.treeimage.heading("# 1", text=t("col_filename"))
        self.treeimage.column("# 2", stretch='yes')
        self.treeimage.heading("# 2", text=t("col_path"), anchor=W)

        ttk.Button(_, text=t("btn_add_file"), command=self.add_img).pack(side=LEFT, ipadx=15)
        ttk.Button(_, text=u"\ue971", command=self.treeimage.move_up).pack(side=RIGHT)
        ttk.Button(_, text=u"\ue972", command=self.treeimage.move_down).pack(side=RIGHT, padx=6)
        ttk.Button(_, text=u"\ue74d", command=self.treeimage.remove_item).pack(side=RIGHT)

        self.treeimage.pack(fill='both', expand=True)

        return tab


    def tab_settings(self):
        tab = ttk.Frame(self.parent)

        save_group = ttk.Frame(tab)
        ttk.Label(save_group, text=t("save_location"), font=('Segoe UI', 9, 'bold' )).pack(fill='x', pady=(0,6))
        ttk.Radiobutton(save_group, text=t("save_same_location"), variable=self.app.save_location, value="").pack(fill='x', pady=3, padx=8)
        ttk.Radiobutton(save_group, text=t("save_custom_location"), variable=self.app.save_location, value='custom', command=self.custom_location).pack(fill='x', pady=3, padx=8)
        self.save_label = ttk.Label(save_group, text=SAVE_LOCATION, foreground="gray", wraplength=600)
        self.save_label.pack(fill='x', padx=40, expand=True)
        save_group.pack(fill='x', pady=10, anchor=NW)

        lang_group = ttk.Frame(tab)
        ttk.Label(lang_group, text=t("settings_language"), font=('Segoe UI', 9, 'bold' )).pack(fill='x', pady=(0,6))
        ttk.Radiobutton(lang_group, text=t("lang_ar"), variable=self.app.current_lang, value='ar').pack(fill='x', pady=3, padx=8)
        ttk.Radiobutton(lang_group, text=t('lang_en') , variable=self.app.current_lang, value='en').pack(fill='x', pady=3, padx=8)
        lang_group.pack(fill='x', pady=10, anchor=NW)

        _ = ttk.Frame(tab)
        ttk.Label(_, text="PDF tools v4.0", font=('default', 12, 'bold')).pack(pady=(68, 0))
        ttk.Label(_, text="https://github.com/youssefhoummad/pdf-tools/", foreground="dodgerblue1").pack(pady=8)
        ttk.Label(_, text=t('copyright'), foreground="gray").pack()
        _.pack(fill='x', anchor=NE, expand=True)

        return tab


    def add_pdf(self, *args, **kws):
        path = filedialog.askopenfilename(title=t('select_pdf_title'), filetypes=[("PDF files", "*.pdf")])
        if not path: return

        path = r'{}'.format(path) # convert to raw

        self.app.select_pdf(path)
        self.treepdf.insert("", 'end', values=(path,len(self.app.PDF)))


    def add_img(self, *args, **kws):
        path = filedialog.askopenfilename(title=t('select_image_title'), filetypes=[("Images files", ("*.jpg", "*.jpeg", "*.png"))])
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
        result = filedialog.askdirectory()
        if not result: return

        save_location = Path(result)
        self.app.save_location.set(save_location)
        self.save_label.configure(text=save_location)






if __name__ == '__main__':
    get_settings()

    window = tk.Tk()
    window.geometry("650x650")
    window.resizable(False, False)
    window.iconbitmap(r'img/icon.ico')
    window.title(t('app_title'))

    styling_tkinter(window, rtl=rtl)

    app = App(window, View)    
    app.mainloop()
