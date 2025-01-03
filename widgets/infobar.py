import tkinter as tk



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
            icon_text = u'\ue814' # Warning icon #TODO need change
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
        icon_label = tk.Label(self, text=icon_text, bg=bg_color, fg=fg_color, font=("Segoe Fluent Icons", 14, "normal"))
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
        width = len(text) * 8 + 140
        if width > 400:
            width = 400
        # width = 460
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
            self.after(10, self._slide_out)
        else:
            self.destroy()  # Remove the widget completely





if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("500x200")
    root.title("InfoBar Test")

    def show_info():
        infobar = InfoBar(root, "Success", "This is a success message!", "success", 5000)
        infobar.show()

    def show_warning():
        infobar = InfoBar(root, "Warning", "This is a warning message!", "warning", 5000)
        infobar.show()

    def show_error():
        infobar = InfoBar(root, "Error", "This is an error messageThis is an error messageThis is an error message!", "error", 5000)
        infobar.show()

    tk.Button(root, text="Show Success", command=show_info).pack(pady=10)
    tk.Button(root, text="Show Warning", command=show_warning).pack(pady=10)
    tk.Button(root, text="Show Error", command=show_error).pack(pady=10)

    root.mainloop()