import json
import sys
from awesometkinter.bidirender import render_text
# from textwrap import wrap



def need_reshap(text:str):
  matches = '0123456789.!:abcdefghijklmnopkrstuvwxyz'
  if any(x in text.lower() for x in matches):
    return True
  return False


with open(r'src\languages.json') as json_file:
  translate = json.load(json_file)


def gettext(text, lang):
  if lang=='en':
    return text
  translated = translate[lang].get(text, text) or text
  if lang == 'ar' and need_reshap(translated):
    # txt = '\n'.join(wrap(translated, 40))
    if len(translated)<60:
      return render_text(translated)
  return translated



def str_to_list(string:str)-> list[int|tuple]:
  """like 1,4, 6, 20-33"""

  result = []
  string_filtred = "".join(filter(lambda char: char in  "0123456789-,", string))

  for item in list(filter(None, string_filtred.split(","))): # convert to list and remove empty
    if '-' in item:
      x, y = item.split('-')
      result.append((int(x), int(y)+1))
    else:
      result.append(int(item))
  return result


def last_in_list(string:str)-> int:
  # remve all chars 
  string_filtred = "".join(filter(lambda char: char in  "0123456789,", string.replace("-", ",")))
  str_list = list(filter(None, string_filtred.split(",")))
  if not str_list: return 0
  return  int(str_list[-1])

