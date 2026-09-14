from pathlib import Path
from tkinter import ttk

from funcs import load_settings


CURRENT_LANG = 'en'
RTL = False

SETTINGS_PATH = Path(__file__).resolve().parent / "settings.ini"


LEFT, RIGHT, W, E, NW, NE = 'left', 'right', 'w', 'e', 'nw', 'ne'

PADX = (20,10)


RLM = "\u200f" # add this to end of arabic string to fix :?!

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
        'zoom_label': 'Zoom: ',
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
        'placeholder_direction': 'اختر الاتجاه...' + RLM ,
        'zoom_label': 'تكبير: '+RLM,
        'btn_apply': 'تطبيق',
        'btn_clear': 'مسح',
        'btn_add_file': 'إضافة ملف',
        'no_file_selected': 'لم يتم اختيار ملف \n',
        'drop_hint': 'اضغط أو اسحب الملف هنا',
        'merge_desc': (": PDF دمج ملفات الـ \nأداة سهلة الاستخدام تتيح لك دمج عدة ملفات في مستند واحد بسهولة اسحب وأفلت ملفاتك، ورتّبها كما تشاء." + RLM),
        'convert_desc': (": PDF تحويل الصور إلى \n أداة سهلة الاستخدام تتيح لك تحويل ودمج عدة صور في ملف  واحد عالي الجودة بالسحب والإفلات." + RLM),
        'col_path': 'المسار',
        'col_pages': 'الصفحات',
        'col_filename': 'اسم الملف',
        'save_location': 'مكان الحفظ',
        'save_same_location': 'في نفس مكان الملف الأصلي  ',
        'save_custom_location': 'في هذا المكان:  ' + RLM,
        'settings_language': 'اللغة',
        'lang_auto': 'تلقائي (حسب النظام)',
        'lang_ar': 'العربية  ',
        'lang_en': 'الإنجليزية  ',
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
 


settings = load_settings(SETTINGS_PATH)
CURRENT_LANG = settings.get('LANG', {}).get('current_lang', 'en')

if CURRENT_LANG == 'ar':
    LEFT, RIGHT, W, E, NW, NE = 'right', 'left', 'e', 'w', 'ne', 'nw'
    PADX = 10, 20
    RTL = True




 
def t(key):
    """يرجع النص المترجم للمفتاح المعطى حسب اللغة الحالية المحمَّلة."""
    return STRINGS.get(CURRENT_LANG, STRINGS['en']).get(key, key)




def style_rtl(window):
    window.option_add('*Ttk*direction', 'rtl')
    window.option_add('*TLabel*justify', 'right')
    window.option_add('*TLabel*anchor', 'e')
    window.option_add('*TEntry*justify', 'right')

    for widget in ["Ttk", "Tk", "TLabelFrame", "TRadiobutton", "TEntry", "TButton", "TLabel", "TScale"]:
        window.option_add(f'*{widget}*direction', 'rtl')
        window.option_add(f'*{widget}*justify', 'right')
        window.option_add(f'*{widget}*anchor', 'e')

    style = ttk.Style()
    style.configure('TNotebook.Tab', tabposition='ne')
    style.configure('TNotebook', height=40, width=80, tabposition='ne')

    style.layout('TRadiobutton', [
        ('Radiobutton.padding', {'sticky': 'nswe', 'children': [
            ('Radiobutton.indicator', {'side': 'right', 'sticky': ''}),
            ('Radiobutton.focus', {'side': 'right', 'sticky': '', 'children': [
                ('Radiobutton.label', {'sticky': ''})
            ]})
        ]})
    ])

    style.layout('TCombobox', [
        ('Combobox.field', {'sticky': 'nswe', 'children': [
            ('Combobox.downarrow', {'side': 'left', 'sticky': 'ns'}),
            ('Combobox.padding', {'expand': '1', 'sticky': 'nswe', 'children': [
                ('Combobox.textarea', {'sticky': 'nswe'})
            ]})
        ]})
    ])



def reverse_notebook(notebook):
    current_tabs = notebook.tabs() # Returns a list of widget names            
    for index, tab_id in enumerate(reversed(current_tabs)):
        notebook.insert(index, tab_id)



def reverse_treeview(window):
    window.treepdf["displaycolumns"] = ("B", "A")
    window.treeimage["displaycolumns"] = ("B", "A")



def flip_grid_horizontally(parent):
    items = []
    for child in parent.winfo_children():
        info = child.grid_info()
        if info:
            items.append((int(info['row']), int(info['column']), child))
    if not items:
        return
    max_col = max(c for _, c, _ in items)
    for row, col, widget in items:
        widget.grid_configure(column=max_col - col)



def reverse_scale(scale):
    scale.configure(from_=8, to=1)
    