import tkinter as tk
from tkinter import ttk
from funcs import *
from typing import Callable




class InfoBar(tk.Frame):
    def __init__(self, parent, title, text, info_type="success", duration=3000):
        """
        Create a styled InfoBar with horizontal sliding animation.
        :param parent: Parent widget to contain the InfoBar.
        :param title: Title to display on the InfoBar.
        :param text: The message to display in the InfoBar.
        :param info_type: The type of InfoBar ("success", "warning", or "error").
        :param duration: Time in milliseconds before the InfoBar hides automatically.
        """
        super().__init__(parent)
        # Define styles for success, warning, and error
        if info_type == "success":
            bg_color = "#d4edda"  # Light green
            fg_color = "#155724"  # Dark green
            border_color = "#c3e6cb"  # Green border
            icon_text = ""  # Success icon
        elif info_type == "warning":
            bg_color = "#fff3cd"  # Light yellow
            fg_color = "#856404"  # Dark yellow/brown
            border_color = "#ffeeba"  # Yellow border
            icon_text = u'\uF167' # Warning icon #TODO need change
        else:  # error
            bg_color = "#f8d7da"  # Light red
            fg_color = "#721c24"  # Dark red
            border_color = "#f5c6cb"  # Red border
            icon_text = ""  # Error icon

        self.config(
            bg=bg_color,
            padx=10,
            pady=10,
            highlightbackground=border_color,
            highlightthickness=1,  # Border thickness
            bd=0,  # Internal border thickness
            width=450,
            )

        # Icon label
        icon_label = tk.Label(self, text=icon_text, bg=bg_color, fg=fg_color, font=("Segoe Fluent Icons", 16, "bold"))
        icon_label.pack(side="left", padx=5)

        # Title label
        title_label = tk.Label(self, text=title, bg=bg_color, fg=fg_color, font=("Segoe UI", 11, "bold"))
        title_label.pack(side="left", padx=5)

        # Message label
        message_label = tk.Label(self, text=text, bg=bg_color, font=("Segoe UI", 10, "normal"), fg=fg_color, anchor="w", justify="left", wraplength=300)
        message_label.pack(side="left", fill="both", expand=True, padx=5)

        # Close button
        close_button = tk.Button(
            self,
            text="",
            bg=bg_color,
            fg=fg_color,
            relief="flat",
            font=("Segoe Fluent Icons", 10, "bold"),
            command=self.destroy,
            highlightthickness=0,
            activebackground=bg_color,
            bd = 0
        )
        close_button.pack(side="right")


        # Animation properties
        width = 460
        self._duration = duration
        self._parent = parent
        # self._parent.update()
        self._current_x = self._parent.winfo_width()  # Start off-screen (right)
        self._target_x = self._current_x - width - 10

        # Place the InfoBar initially off-screen
        self.place(x=self._current_x, y=10, width=width)


    def show(self):
        """Show the InfoBar with a sliding animation (right to left)."""
        self.after(10, self._slide_in)


    def _slide_in(self):
        """Slide the InfoBar in from right to left."""
        if self._current_x > self._target_x:
            self._current_x -= 10  # Adjust speed here
            self.place_configure(x=self._current_x)
            self.after(5, self._slide_in)
        else:
            self.after(self._duration, self.hide)  # Auto-hide after duration


    def hide(self):
        """Hide the InfoBar with a sliding animation (left to right)."""
        # self.after(10, self._slide_out)
        self.destroy()


    def _slide_out(self):
        """Slide the InfoBar out from left to right."""
        if self._current_x < 460:
            self._current_x += 10  # Adjust speed here
            self.place_configure(x=self._current_x)
            self.after(1, self._slide_out)
        else:
            self.destroy()  # Remove the widget completely









# has placeholder
class Entry(ttk.Entry):
    def __init__(self, master=None, placeholder="",command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        super().insert(0, placeholder)

        # Bind events for removing and adding placeholder
        self.bind("<FocusIn>", self.remove_placeholder)
        self.bind("<FocusOut>", self.add_placeholder)
        self.bind("<KeyRelease>", self.check_empty)




    def configure(self, *args, **kwargs):
        if kwargs.get("state") == "enable":
            super().config(state="enable")
            self.add_placeholder(None)

        if kwargs.get("state") == "disable":
            super().delete(0, 'end')
            self.state(["!invalid"])
            super().config(state="disable")


    config = configure



    def validate(self, *_):
        """
        This method invalidates the entry if its content is not an integer
        """
        if validate_input(self.get()):
            self.state(["!invalid"])
        else:
            self.state(["invalid"])

 

    def remove_placeholder(self, event):
        """Remove placeholder text when the user clicks into the entry field."""

        color = self.tk.call("ttk::style", "lookup", "TEntry", "-foreground")
        if super().get() == self.placeholder:
            super().configure(foreground=color)
            self.delete(0, 'end')
        
        self.validate()

    def add_placeholder(self, event):
        """Add placeholder text back if the entry is empty."""
        # self.bind("<FocusOut>", self.validate_int)

        if super().get() == "":
            super().configure(foreground='gray')
            self.insert(0, self.placeholder)

    def check_empty(self, event):
        """Check if the entry is empty and handle placeholder."""
        self.bind("<KeyRelease>", self.validate)

        if super().get() == "":
            self.add_placeholder(event)
        
        if super().get() == self.placeholder:
            self.remove_placeholder(event)
    
    def get(self):
        if super().get() == self.placeholder:
            return ""
        return super().get()
        

# has placeholder
class Combobox(ttk.Combobox):
    def __init__(self, container, placeholder="Select an option...", *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_active = True
        
        # Set initial placeholder
        self.set(self.placeholder)
        
        # Bind events
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self.bind("<<ComboboxSelected>>", self._on_select)
    
    def _clear_placeholder(self, event=None):
        if self.placeholder_active:
            self.set('')
            self.placeholder_active = False
    
    def _add_placeholder(self, event=None):
        if not self.get():
            self.set(self.placeholder)
            self.placeholder_active = True
    
    def _on_select(self, event=None):
        self.placeholder_active = False
        color = self.tk.call("ttk::style", "lookup", "TLabel", "-foreground")

        self.config(foreground=color)
    
    def get(self):
        # Return empty string if placeholder is active
        if self.placeholder_active:
            return ''
        return super().get()
    

    def configure(self, *args, **kwargs):
        if kwargs.get("state") == "enable":
            self._add_placeholder(None)

        if kwargs.get("state") == "disable":
            self.set('')
            super().config(foreground='gray')
        
        super().config(*args, **kwargs)
    
    config = configure


# width move up methods
class Treeview(ttk.Treeview):
    def __init__(self, parent, on_select:Callable, on_drop:Callable, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bind("<<TreeviewSelect>>", self.on_row_select)
        apply_dnd(self, on_drop)

        self.on_select = on_select
    
    
    def move_up(self, *args, **kwargs):
        leaves = self.selection()
        for i in leaves:
            self.move(i, self.parent(i), self.index(i)-1)


    def move_down(self, *args, **kwargs):
        leaves = self.selection()
        for i in reversed(leaves):
            self.move(i, self.parent(i), self.index(i)+1)
    

    def remove_item(self, *args, **kwargs):
        leaves = self.selection()
        if leaves:
            self.delete(leaves[0])



    def on_row_select(self, *args, **kws):
        selected_item = self.selection()
        if selected_item:
            values = self.item(selected_item[0], 'values')
            self.on_select(values)
