import tkinter as tk
from tkinter import messagebox
from walmart_app.config import *
from walmart_app.frontend.navbar import create_navbar


class AddItemPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller

        # create_navbar(self)

        tk.Label(self, text="Add Items to Cart", font=FONT_TITLE, fg=COLOR_PRIMARY, bg=WINDOW_BG).pack(pady=16)

        form_frame = tk.Frame(self, bg=WINDOW_BG)
        form_frame.pack(pady=10)

        # Fields
        tk.Label(form_frame, text="Item name:", font=FONT_LABEL, fg=COLOR_PRIMARY, bg=WINDOW_BG).grid(row=0, column=0, pady=8, sticky="e")
        self.entry_name = tk.Entry(form_frame, width=30, font=("Arial", 12), bd=2, relief="solid")
        self.entry_name.grid(row=0, column=1, pady=8)

        tk.Label(form_frame, text="Item price:", font=FONT_LABEL, fg=COLOR_PRIMARY, bg=WINDOW_BG).grid(row=1, column=0, pady=8, sticky="e")
        self.entry_price = tk.Entry(form_frame, width=30, font=("Arial", 12), bd=2, relief="solid")
        self.entry_price.grid(row=1, column=1, pady=8)

        tk.Label(form_frame, text="Item quantity:", font=FONT_LABEL, fg=COLOR_PRIMARY, bg=WINDOW_BG).grid(row=2, column=0, pady=8, sticky="e")
        self.entry_qty = tk.Entry(form_frame, width=30, font=("Arial", 12), bd=2, relief="solid")
        self.entry_qty.grid(row=2, column=1, pady=8)

        # Buttons
        btn_frame = tk.Frame(self, bg=WINDOW_BG)
        btn_frame.pack(pady=16)

        tk.Button(btn_frame, text="SAVE", width=10, font=FONT_BUTTON, command=self.save_item, relief="solid").grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="RESET", width=10, font=FONT_BUTTON, command=self.reset_form, relief="solid").grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="BACK", width=10, font=FONT_BUTTON, command=lambda: controller.show_page("HomePage"), relief="solid").grid(row=0, column=2, padx=8)

    def save_item(self):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        qty = self.entry_qty.get().strip()

        if not name or not price or not qty:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        try:
            price_val = float(price)
            qty_val = int(qty)
        except ValueError:
            messagebox.showwarning("Input Error", "Enter valid numeric values for price and quantity!")
            return

        messagebox.showinfo("Success", f"Item Saved:\n\nName: {name}\nPrice: {price_val}\nQuantity: {qty_val}")

    def reset_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_qty.delete(0, tk.END)
