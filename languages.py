merge_discrption = "Combine PDFs in the order you want with the easiest PDF merger available."
split_discrption = "Separate one page or a whole set for easy conversion into independent PDF files."
images_discrption = "Convert each PDF page into a JPG or extract all images contained in a PDF."
rotate_discrption = "Rotate your PDFs the way you need them. You can even rotate multiple PDFs at once!"
crop_discrption = "Crop your PDF's margins the way you need them. You can even crop spesific pages"

about_discrption = "Every tool you need to use PDFs! Merge, split, convert, rotate with just a few clicks."

translate =  {
  'fr':
      {
        "browse": "parcourir",
        "select a file:": "sélectionner un fichier:",
        "select pages:": "sélectionner les pages:",

        "split": "diviser",
        "merge files": "fusionner",
        "crop margins": "rogner les marges",
        "rotate pages": "pivoter les pages",
        "to images": "à images",
        "about": "à propos",

        'top:':"haut",
        'bottom:':"bas",
        'right:':"droite",
        'left:':"gauche",

        'rotate degree:':"degré de rotation:",
        'add files':"ajouter des fichiers",
        'clear all':"tout effacer",
        'save':"sauvegarder",

        "Convert file": "Convertir",
        "Split file": "Diviser",
        "Crop file": "Recadrer",
        "Merge files": "Fusionner",
        "Rotate pages": "pivoter",
        
        "like 2,7, 9-20, 56": "comme: 2,7, 9-20, 56",
        "Choose language:": "Choisissez votre language",
        "open pdf after operation is finished": "ouvrir le pdf une fois l'opération terminée",


        "P R E V I E W": "A P E R Ç U",
        rotate_discrption: "Faites pivoter votre PDF comme vous le souhaitez. Tournez plusieurs pages à la fois!",
        merge_discrption: "Fusionner et combiner des fichiers PDF et les mettre dans l'ordre que vous voulez. C'est très facile et rapide!",
        split_discrption: "Sélectionner la portée de pages, séparer une page, ou convertir chaque page du document en fichier PDF indépendant.",
        images_discrption: "Extraire toutes les images contenues dans un fichier PDF ou convertir chaque page dans un fichier JPG.",
        crop_discrption: "Recadrez les marges de votre PDF comme vous en avez besoin. Vous pouvez même recadrer des pages spécifiques",
        about_discrption:"Tous les outils dont vous avez besoin pour utiliser les PDF, à portée de main. Ils sont tous 100% GRATUITS et simples d'utilisation ! Fusionnez, divisez, convertissez, faites pivoter, en seulement quelques clics.",

        "Dont convert full pages, just extract images": "Ne convertissez pas la page entière, extrayez simplement les images"
      },
    
  'ar':
      {
        "browse": "استعراض",
        "select a file:": ":اختر ملفا",
        "select pages:": ":اختر الصفحات",

        "split": "تقسيم ملف",
        "merge files": "دمج الملفات",
        "crop margins": "تقصيص هومش",
        "rotate pages": "تدوير صفحات",
        "to images": "تحويل لصور",
        "about": "حول",

        'top:':":من الأعلى",
        'bottom:':":من الأسفل",
        'right:':":من اليمين",
        'left:':":من اليسار",

        'rotate degree:':":درجة الدوران",
        'add files':"إضافة ملفات",
        'clear all':"مسح الكل",
        'save':"حفظ",

        "Convert file": "تصدير الصور",
        "Split file": "نقسيم الملف",
        "Crop file": "تقصيص الملف",
        "Merge files": "دمج الملفات",
        "Rotate pages": "تدوير الصفحات",
        
        "like 2,7, 9-20, 56": "مثال: 2,7, 9-20, 56",
        "Choose language:": "اختر لغتك",
        'zoom level:': ":مستوى التكبير",
        "open pdf after operation is finished": "فتح الملف بعد الانتهاء من العمليات ",

        "P R E V I E W": "مـعـايـنـة",
        rotate_discrption: "يمكنك تدوير ملف لأي اتجاه تريده. كما يمكنك تدوير صفحات محددة فقط من ملف واحد في نفس الوقت",
        merge_discrption: "دمج ملفات ووضعها في أي ترتيب تريد مع أسهل أداة لجمع ملفات",
        split_discrption: ".حدد نطاق الصفحات، قم بفصل صفحة واحدة، أو تحويل كل صفحة من الملف إلى ملف مستقل، أو يمكنك إعادة ترتيب ملف",
        images_discrption: "حوّل كل صفحة من صفحات مستند إلى صورة منفصلة أو استخرج جميع الصور من أي ملف",
        crop_discrption: "قم بقص هوامش ملف بالطريقة التي تريدها. يمكنك حتى اقتصاص صفحات معينة",

        "Dont convert full pages, just extract images":"لا تقم بتحويل صفحات كاملة إلى صورة ، فقط استخرج الصور ",
        about_discrption: "كل الأدوات التي أنت في حاجة إليها للتعامل مع مفات البي دي ايف، دمج وتقسيم وتدوير أوحتى تحويلها لصور، كل هذا بدون أنترنت وبنقرات بسيطة"
      },
    

}


def gettext(text, lang):
  if lang=='en':
    return text
  return translate[lang].get(text, text) or text
