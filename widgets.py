
import tkinter as tk
from tkinter import ttk
from functools import partial




class ScrollFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        justify = kwargs.pop('justify', 'left')
        assert justify in ['left', 'right']
        anchor, invers_anchor = 'nw', 'se'
        vsb_place = {'relx':1.0, 'rely':1.0, 'anchor':invers_anchor, 'relheight':1, 'x':1}
        if justify == 'right':
            anchor, invers_anchor = 'se', 'nw'
            vsb_place = {'relx':0.0, 'rely':0.0, 'anchor':invers_anchor, 'relheight':1, 'x':-1}

        super().__init__(parent, **kwargs) # create a frame (self)

        
        
        self.canvas = tk.Canvas(self, bg=parent['bg'], bd=0, highlightthickness=0)
        self.viewPort = ttk.Frame(self.canvas)
        self.viewPort.pack(fill='both', expand=True)
        self.vsb = AutoHideScrollbar(self,  orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)                   

        self.canvas.pack( fill='both', expand=True)           
        
        self.vsb.place(**vsb_place)                           
        self.canvas_window = self.canvas.create_window((0,0), window=self.viewPort, anchor=anchor)

        self.viewPort.bind("<Configure>", self.onFrameConfigure)    
        self.canvas.bind("<Configure>", self.onCanvasConfigure)     
            
        self.viewPort.bind('<Enter>', self.onEnter)                 
        self.viewPort.bind('<Leave>', self.onLeave)                

        self.onFrameConfigure(None) 
    


        
    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
           

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)  

    def onMouseWheel(self, event):                                                 
        if not self.vsb.winfo_ismapped(): 
            return
        self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")

    
    def onEnter(self, event):              
        self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                     
        self.canvas.unbind_all("<MouseWheel>")


class AutoHideScrollbar(ttk.Scrollbar):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry_manager_add = lambda: None
        self.geometry_manager_forget = lambda: None
    
    

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.geometry_manager_forget()
        else:
            self.geometry_manager_add()
        super().set(lo, hi)
    

    def grid(self, **kwargs):
        self.geometry_manager_add = partial(super().grid, **kwargs)
        self.geometry_manager_forget = super().grid_forget

    def pack(self, **kwargs):
        self.geometry_manager_add = partial(super().pack, **kwargs)
        self.geometry_manager_forget = super().pack_forget

    def place(self, **kwargs):
        self.geometry_manager_add = partial(super().place, **kwargs)
        self.geometry_manager_forget = super().place_forget


class Frame(tk.Frame):
    def __init__(self, master,  **kwargs):
        super().__init__(master, bg="#FBFCFE", highlightbackground="#E4E5EA", highlightthickness=1, height=80)
        self.pack_propagate(False) # disable resize


class Seperator(tk.Label):
    def __init__(self, master,  **kwargs):
        super().__init__(master, text='|', fg='light grey', font=('',16) , bg="#FBFCFE")

