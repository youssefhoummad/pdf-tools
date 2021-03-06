from tkinter import Entry, Label, Frame
from tkinter import ttk
import time



class NumEntry(ttk.Entry):
  """a Entry binding width up & down key to crease or increse number, placeholder """
  def __init__(self, parent, placeholder='',_min=0, **kw): #, placeholder=''
    super().__init__(parent, foreground="gray",font=(None, 11), **kw) #, foreground="gray"
    # self.entry.config(width=kw.get('width', 10))


    self.bind("<Up>", self.handleUp)
    self.bind("<Down>", self.handleDown)

    self.bind('<FocusIn>',self.focus_in)
    self.bind('<FocusOut>',self.focus_out)

    self.set(placeholder)
    self.placeholder = placeholder
    self.min = _min


  def handleUp(self, event):
    if not self.get().isdigit() : self.set(0)
    self.set(int(self.get()) + 1)


  def handleDown(self, event):
    if not self.get().isdigit() : self.set(0)
    if int(self.get()) == self.min: return
    self.set(int(self.get()) - 1)
    

  def focus_in(self, event):
    if self.get() == self.placeholder:
      self.set(str(self.min))
    self.configure(foreground='black')


  def focus_out(self, event):
    if self.get() == '':
      self.configure(foreground='gray')
      self.set(self.placeholder)


  def set(self, value):
    self.delete(0, tk.END)
    self.insert(tk.END, value)   
    


class EntryWithPlusMinus(Frame):
  def __init__(self, master, _min=None, _max=None, textvariable=None, placeholder=None):
    super().__init__(master)

    self._min = _min or 0
    self._max = _max
    self.placeholder = placeholder

    self.interval = 0

    FONT = ('Calibri', 12, 'bold')
    self.config(bg=master['bg'], bd=0, relief='solid',highlightthickness=1, highlightcolor="#CCC", highlightbackground='#CCC')

    self.plus = Label(self, text='+', bg=self['bg'], width=2, font=FONT)
    self.entry =Entry(self,width=10, relief='flat', justify='center', textvariable=textvariable, validate='key')

    # validation key
    self.entry['validatecommand'] = (self.entry.register(self.testVal),'%P','%d')

    self.minus = Label(self, text='-', bg=self['bg'], width=2, font=FONT)

    self.plus.pack(side='left')
    # self.plus.pack_propagate()
    Frame(self, width=1, height=22, bg='#CCC').pack(side='left')
    self.entry.pack(side='left', expand=True)
    Frame(self, width=1, height=22, bg='#CCC').pack(side='left')
    self.minus.pack(side='left')

    if placeholder:
      self._label = Label(self, width=self.entry['width']-2, text=placeholder, bg='white', fg='gray', justify='center')
    
    if self.get() == 0 and placeholder: 
      self._label.place(x=24, y=1)

      self._label.bind("<Button-1>", self.on_click_placeholder)


    self.set('')

    self.plus.bind("<ButtonPress-1>", self.on_press_plus)
    self.plus.bind("<ButtonRelease-1>", self.on_release_plus)

    self.minus.bind("<ButtonPress-1>", self.on_press_minus)
    self.minus.bind("<ButtonRelease-1>", self.on_release_minus)

    self.entry.bind("<Up>", self.increase)
    self.entry.bind("<Down>", self.decrease)



    # look
    self.plus.bind("<Enter>", self.on_enter_plus)
    self.plus.bind("<Leave>", self.on_leave_plus)
    self.plus.bind("<ButtonPress-1>", self.on_press_plus)

    self.minus.bind("<Enter>", self.on_enter_minus)
    self.minus.bind("<Leave>", self.on_leave_minus)
    self.minus.bind("<ButtonPress-1>", self.on_press_minus)


  def on_click_placeholder(self, event=None):
    self._label.place_forget()
    self.entry.focus_set()


  def on_enter_plus(self, event=None):
    self.plus.config(bg='#EEE')


  def on_leave_plus(self, event=None):
    self.plus.config(bg='white')


  def on_press_plus(self, event=None):
    self.plus.config(bg='#CCC')
    self.interval += 1
    self.increase()
    speed = max(600//self.interval,50)
    self.after_increse = self.after(speed, self.on_press_plus)
 

  def on_release_plus(self, event=None):
    self.on_enter_plus()
    self.interval = 0
    self.after_cancel(self.after_increse)
    # this trick from https://stackoverflow.com/a/51253906


  def on_enter_minus(self, event=None):
    self.minus.config(bg='#EEE')


  def on_leave_minus(self, event=None):
    self.minus.config(bg='white')


  def on_press_minus(self, event=None):
    self.minus.config(bg='#CCC')
    self.interval += 1
    self.decrease()
    speed = max(600//self.interval,50)
    self.after_decrese = self.after(speed, self.on_press_minus)


  def on_release_minus(self, event=None):
    self.on_enter_minus()
    self.interval = 0
    self.after_cancel(self.after_decrese)


  # https://stackoverflow.com/a/35554720
  def testVal(self, inStr,acttyp):
    # if key pressed is number 
    if acttyp == '1': #insert
      if not inStr.isdigit():
        self.flash()
        return False
      if self._max:
        if int(inStr) > self._max:
          self.flash()
          return False
    return True


  def get(self):
    try:
      return int(self.entry.get())
    except:
      return 0


  def set(self, value):
    self.entry.delete(0, 'end')
    self.entry.insert(0, value) 

    if self.get() in [0, ''] and self.placeholder:
      self._label.place(x=24, y=1)
    elif self.placeholder:
      self._label.place_forget()
    return 
  

  def increase(self, event=None):
    if self.get() == self._max: return
    self.set(self.get() + 1)


  def decrease(self, event=None):
    if self.get() == self._min: return
    self.set(self.get() - 1)


  def flash(self):
    self.entry.config(bg='#FFB3B3')
    self.update_idletasks()
    time.sleep(0.06)
    self.entry.config(bg="white")
    self.update_idletasks()

    time.sleep(0.05)
    self.entry.config(bg="#FFB3B3")
    self.update_idletasks()
    time.sleep(0.04)
    self.entry.config(bg="white")
    self.update_idletasks()
    
    time.sleep(0.03)
    self.entry.config(bg="#FFB3B3")
    self.update_idletasks()
    time.sleep(0.02)
    self.entry.config(bg="white")
    self.update_idletasks()

  

  




if __name__ == "__main__":
  from tkinter import Tk, StringVar
  root = Tk()
  text = StringVar()
  f = Frame(root, bg='white')
  entry1 = EntryWithPlusMinus(f, placeholder='test')
  
  entry1.pack(padx=22, pady=20)
  f.pack()

  root.mainloop()
