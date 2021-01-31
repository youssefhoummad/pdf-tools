import subprocess
from threading import Thread
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer

def threaded(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


# def loadfont(fontpath, private=True, enumerable=False):
#     '''
#     Makes fonts located in file `fontpath` available to the font system.

#     `private`     if True, other processes cannot see this font, and this 
#                   font will be unloaded when the process dies
#     `enumerable`  if True, this font will appear when enumerating fonts

#     See https://msdn.microsoft.com/en-us/library/dd183327(VS.85).aspx

#     '''
    
#     FR_PRIVATE  = 0x10
#     FR_NOT_ENUM = 0x20
    
#     # This function was taken from
#     # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15
#     # This function is written for Python 2.x. For 3.x, you
#     # have to convert the isinstance checks to bytes and str
#     if isinstance(fontpath, str):
#         pathbuf = create_string_buffer(fontpath)
#         AddFontResourceEx = windll.gdi32.AddFontResourceExA
#     if isinstance(fontpath, unicode):
#         pathbuf = create_unicode_buffer(fontpath)
#         AddFontResourceEx = windll.gdi32.AddFontResourceExW
#     else:
#         raise TypeError('fontpath must be of type str or unicode')

#     flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
#     numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
#     return bool(numFontsAdded)


FR_PRIVATE  = 0x10
FR_NOT_ENUM = 0x20
def loadfont(fontpath, private=True, enumerable=False):
    # This function was taken from
    # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15
    # This function is written for Python 2.x. For 3.x, you
    # have to convert the isinstance checks to bytes and str
    if isinstance(fontpath, bytes):
        pathbuf = create_string_buffer(fontpath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExA
    elif isinstance(fontpath, str):
        pathbuf = create_unicode_buffer(fontpath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExW
    else:
        raise TypeError('fontpath must be of type str or unicode')
    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
    numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
    return bool(numFontsAdded)

