from tkinter import ttk

# has placeholder
class Combobox(ttk.Combobox):
    """
    A custom Combobox widget with placeholder text functionality.
    Parameters:
    container : widget
        The parent widget.
    placeholder : str, optional
        The placeholder text to display when no selection is made (default is "Select an option...").
    *args : tuple
        Additional positional arguments passed to the ttk.Combobox.
    **kwargs : dict
        Additional keyword arguments passed to the ttk.Combobox.
    Methods:
    _clear_placeholder(event=None)
        Clears the placeholder text when the widget gains focus.
    _add_placeholder(event=None)
        Adds the placeholder text when the widget loses focus and no selection is made.
    _on_select(event=None)
        Handles the event when an option is selected from the combobox.
    get()
        Returns the current value of the combobox, or an empty string if the placeholder is active.
    configure(*args, **kwargs)
        Configures the combobox widget. Handles enabling and disabling of the widget and manages the placeholder text accordingly.
    """

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



if __name__ == "__main__":
    import tkinter as tk

    root = tk.Tk()
    root.geometry("300x200")
    cb = Combobox(root, values=["one", "two", "three"], placeholder="Select a number...")
    cb.pack()
    root.mainloop()

