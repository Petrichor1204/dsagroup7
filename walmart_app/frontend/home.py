import tkinter as tk
from walmart_app.config import *


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller

        # Walmart Logo
        image_path = WALMART_LOGO
        try:
            image = tk.PhotoImage(file=image_path)
            image_label = tk.Label(self, image=image, bg=WINDOW_BG)
            self.image_ref = image  # keep reference to avoid garbage collection
            image_label.pack(padx=10, pady=(40, 20))
        except Exception as e:
            print(f"Error loading image: {e}")
            tk.Label(
                self,
                text="Welcome to Walmart 🛒",
                font=FONT_TITLE,
                fg=COLOR_PRIMARY,
                bg=WINDOW_BG,
            ).pack(pady=20)

        # Buttons
        btn_style = {"bg": COLOR_PRIMARY, "fg": "white", "font": FONT_BUTTON, "width": 30, "height": 2}

        tk.Button(self, text="Add Item", command=lambda: controller.show_page("AddItemPage"), **btn_style).pack(pady=6)
        tk.Button(self, text="View Cart", command=lambda: controller.show_page("ViewCartPage"), **btn_style).pack(pady=6)
        tk.Button(self, text="Checkout", command=lambda: controller.show_page("CheckoutPage"), **btn_style).pack(pady=(6, 40))
