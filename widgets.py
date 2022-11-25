
import tkinter as tk
from tkinter import ttk
from functools import partial

from constants import pack_opts


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

        self.vsb = AutoHideScrollbar(self,  orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)                   

        self.canvas.pack( fill='both', expand=True)           
        self.viewPort.pack(fill='both', expand=True)
        
        self.vsb.place(**vsb_place)                           
        self.canvas_window = self.canvas.create_window((0,0), window=self.viewPort, anchor=anchor)

        self.viewPort.bind("<Configure>", self.onFrameConfigure)    
        self.canvas.bind("<Configure>", self.onCanvasConfigure)     
            
        self.viewPort.bind('<Enter>', self.onEnter)                 
        self.viewPort.bind('<Leave>', self.onLeave)                

        self.onFrameConfigure(None)


        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.viewPort.bind("<Configure>", self.onFrameConfigure)

        
        self.outer_attr = set(dir(tk.Widget))
    


    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.viewPort, item)



    def go_to_bottom(self, event=None):
        self.canvas.yview_moveto(1)
    


        
    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        # self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
        _, _, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        width = self.canvas.winfo_width()    
        self.canvas.config(scrollregion = (0,0, x2, max(y2, height)))
        self.canvas.itemconfigure("all", width=width)  
           

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
    def __init__(self, master, **kwargs):
        height = kwargs.get('height', 80)
        super().__init__(master, bg="#FBFCFE", highlightbackground="#E4E5EA", highlightthickness=1, height=height)
        self.pack_propagate(False) # disable resize

    


class CollapseFrame(tk.Frame):

    instences = []

    def __init__(self, master, target_frame:tk.Frame, collapsed=True, scrollbar=None, **kwargs):
        super().__init__(master, bg="#FBFCFE", highlightbackground="#E4E5EA", highlightthickness=1, height=80, cursor='hand2')
        self.pack_propagate(False) # disable resize

        self.master = master
        self.scrollbar = scrollbar

        print(scrollbar)

        self.target_frame=target_frame
        self.target_frame.pack_propagate(False)

        self.instences.append(target_frame)

        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)


        self.collapsed = collapsed

        if not collapsed:
            self.target_frame.pack(after=self, **pack_opts)

    
    def on_release(self, e):

        if self.collapsed:

            [frame.pack_forget() for frame in self.instences] # collapse other

            self.target_frame.pack(after=self, **pack_opts)
            self.collapsed = False

        else:
            self.target_frame.pack_forget()
            self.collapsed = True

    def on_hover(self, e):
        
        self.config(background='#F3F7FA', highlightbackground="#E1E6EA")
        for w in self.winfo_children():
            try:
                w.config(background='#F3F7FA') # type: ignore
            except:
                pass
  
    def on_leave(self, e):
        self.config(bg='#FBFCFE')
        for w in self.winfo_children():
            try:
                w.config(bg='#FBFCFE') # type: ignore
            except:
                pass
    
    
    def pack(self, *arg, **kwags):
        for w in self.winfo_children():
            if isinstance(w, ttk.Label):
                w.bind("<ButtonRelease-1>", self.on_release)
                w.bind("<Enter>", self.on_hover)
                w.bind("<Leave>", self.on_leave)
        super().pack( *arg, **kwags)






class Seperator(tk.Label):
    def __init__(self, master,  **kwargs):
        super().__init__(master, text='|', fg='light grey', font=('',16) , bg="#FBFCFE")



class VerticalScrolledFrame:
    """
    A vertically scrolled Frame that can be treated like any other Frame
    ie it needs a master and layout and it can be a master.
    :width:, :height:, :bg: are passed to the underlying Canvas
    :bg: and all other keyword arguments are passed to the inner Frame
    note that a widget layed out in this frame will have a self.master 3 layers deep,
    (outer Frame, Canvas, inner Frame) so 
    if you subclass this there is no built in way for the children to access it.
    You need to provide the controller separately.
    """
    def __init__(self, master, **kwargs):
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)

        self.outer = tk.Frame(master, bg=master['bg'], bd=0, highlightthickness=0)

        self.vsb = ttk.Scrollbar(self.outer, orient=tk.VERTICAL)
        self.vsb.pack(side='right', fill='y')
        self.canvas = tk.Canvas(self.outer,bg=master['bg'], highlightthickness=0, width=width, height=height) # type: ignore
        self.canvas.pack(fill='both', expand=True)
        self.canvas['yscrollcommand'] = self.vsb.set
        # mouse scroll does not seem to work with just "bind"; You have
        # to use "bind_all". Therefore to use multiple windows you have
        # to bind_all in the current widget
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vsb['command'] = self.canvas.yview

        self.inner = tk.Frame(self.canvas, bg=master['bg'])
        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(0, 0, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(tk.Widget))
    

    def moveto(self, y):
        self.canvas.yview_moveto(y)


    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        # self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
        _, _, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        width = self.canvas.winfo_width()    
        self.canvas.config(scrollregion = (0,0, x2, max(y2, height)))
        self.canvas.itemconfigure("all", width=width)  

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units" )
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units" )

    def __str__(self):
        return str(self.outer)





class Popup(tk.Toplevel):
	"""modal window requires a master"""
	def __init__(self, master, **kwargs):
		tk.Toplevel.__init__(self, master, **kwargs)

		lbl = tk.Label(self, text="this is the popup")
		lbl.pack()

		btn = tk.Button(self, text="OK", command=self.destroy)
		btn.pack()

		# The following commands keep the popup on top.
		# Remove these if you want a program with 2 responding windows.
		# These commands must be at the end of __init__
		self.transient(master) # set to be on top of the main window
		self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
		master.wait_window(self) # pause anything on the main window until this one closes

