import locale
from .easysettings import EasySettings



P_COLOR = "#1481CE"
S_COLOR = "#F67E6A"
STOP = False
CANVAS_W = 147
CANVAS_H = 200
FONT = "Segoe UI Semibold"
FONT_1 =  "Tahoma"
FONT_2 =  "Tahoma"


SIDBAR_BG = "#F2F2F2"


settings = EasySettings('config.conf')
DIR = settings.get('DIR')

if not DIR:
  #for direction left to right
  lang , _ = locale.getdefaultlocale()
  if lang.startswith('ar_'): DIR = 'rtl'
  else: DIR = 'ltr'

if DIR == 'rtl':
  START_DIR = 'right'
  END_DIR = 'left'
  NW = 'se'
  TK_E = 'nw'
  END_PADDING_10 = (10,0)
  START_PADDING_24 =(12,24)
  START_PADDING_24_0 =(24,0)

  BROWSE = 'استعراض'

  MAIN_DESC = "مجموعة من الأدوات للتعامل\nمع ملفات البي.دي.اف"

  SPLIT_TITLE = "تقطيع الملفات"
  MERGE_TITLE = "دمج الملفات"
  CROP_TITLE = "تقليم الهوامش"
  EXTRACT_TITLE = "استخراج الصور"
  IMAGES_TITLE = "صور إلى ملف"
  ABOUT_TITLE = "حول"

  SPLIT_DESC = "يقوم بتجزئة الملف من صفحة محددة إلى أخرى\nوتُحفظ في ملف جديد."
  MERGE_DESC = "دمج الملفين بالترتيب في ملف واحد \nبأبسط طريقة ممكنة."
  CROP_DESC = "تقليم حواف صفحات الملف حسب ما تحتاج"
  EXTRACT_DESC = "استخراج جميع الصور المتضمَنة في الملف"
  IMAGES_DESC = "تحويل مجموعة من الصور إلى ملف واحد"
  ABOUT_DESC = "هذه الأداة من تطوير: يوسف حمد \n:يمكنك زيارة حسابي على الغيت هاب من خلال الرابط أدناه"
  EMAIL_TEXT = ":أو يمكنك التواصل معي على البريد الإلكتروني"

  CHOOSE_LANGUAGE = ":اختر لغة"
  
  SPLIT_BTN = 'تقسيم الملف'
  MERGE_BTN = 'دمج الملفين'
  CROP_BTN = 'تقليم الملف'
  EXTRACT_BTN = 'استخراج الصور'
  CONVERT_BTN = 'تحويل الصور لملف'

  FROM_TXT = 'من'
  TO_TXT = 'إلى'
  TOP_TXT = 'الأعلى'
  BOTTOM_TXT = 'الاسفل'
  RIGHT_TXT = 'اليمين'
  LEFT_TXT = 'اليسار'


else:
  START_DIR = 'left'
  END_DIR = 'right'
  NW = 'nw'
  TK_E = 'se'
  END_PADDING_10 = (0,10)
  START_PADDING_24 =(24,12)
  START_PADDING_24_0 =(24,0)

  BROWSE = 'Browse'

  MAIN_DESC = "PDF tools is a collections of tools\nthat will works with pdf files"

  SPLIT_TITLE = "Split file"
  MERGE_TITLE = "Merge files"
  CROP_TITLE = "Crop margins "
  EXTRACT_TITLE = "Extract images"
  IMAGES_TITLE = "images to pdf"
  ABOUT_TITLE = "ABOUT"

  SPLIT_DESC = "Separate one page or a whole set for easy conversion\n into independent PDF files."
  MERGE_DESC = "Combine PDFs in the order you want \nwith the easiest PDF merger available."
  CROP_DESC = "Crop your PDF files with ease."
  EXTRACT_DESC = "Extract all images contained in a PDF."
  IMAGES_DESC = "Convert all images selected into one PDF."
  ABOUT_DESC = "PDF tools devlopped by: youssefhoummad \nvisit my GITHUB account from link below:"
  EMAIL_TEXT = "Or you can contact me by email:"
  CHOOSE_LANGUAGE = "Choose language: "


  SPLIT_BTN = 'Split file'
  MERGE_BTN = 'Merge file'
  CROP_BTN = 'Crop file'
  EXTRACT_BTN = 'Extract images'
  CONVERT_BTN = 'Convert to pdf'


  FROM_TXT = 'from'
  TO_TXT = 'to'
  TOP_TXT = 'top'
  BOTTOM_TXT = 'bottom'
  RIGHT_TXT = 'right'
  LEFT_TXT = 'left'