import tkinter as tk
from tkinter import messagebox
from walmart_app.config import *
from walmart_app.backend import db_helper


class AddItemPage(tk.Frame):
    """Page to add items into the shopping cart (DB-backed)."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller

        # Title
        title_label = tk.Label(
            self,
            text="Add Items to Cart",
            font=FONT_TITLE,
            fg=COLOR_PRIMARY,
            bg=WINDOW_BG,
        )
        title_label.pack(pady=16)

        # Form frame
        form_frame = tk.Frame(self, bg=WINDOW_BG)
        form_frame.pack(pady=10)

        # Item Name
        tk.Label(
            form_frame,
            text="Item name:",
            font=FONT_LABEL,
            fg=COLOR_PRIMARY,
            bg=WINDOW_BG,
        ).grid(row=0, column=0, pady=8, sticky="e")
        self.entry_name = tk.Entry(form_frame, width=30, font=FONT_BODY, bd=2, relief="solid")
        self.entry_name.grid(row=0, column=1, pady=8)

        # Item Price
        tk.Label(
            form_frame,
            text="Item price:",
            font=FONT_LABEL,
            fg=COLOR_PRIMARY,
            bg=WINDOW_BG,
        ).grid(row=1, column=0, pady=8, sticky="e")
        self.entry_price = tk.Entry(form_frame, width=30, font=FONT_BODY, bd=2, relief="solid")
        self.entry_price.grid(row=1, column=1, pady=8)

        # Item Quantity
        tk.Label(
            form_frame,
            text="Item quantity:",
            font=FONT_LABEL,
            fg=COLOR_PRIMARY,
            bg=WINDOW_BG,
        ).grid(row=2, column=0, pady=8, sticky="e")
        self.entry_qty = tk.Entry(form_frame, width=30, font=FONT_BODY, bd=2, relief="solid")
        self.entry_qty.grid(row=2, column=1, pady=8)

        # Buttons
        btn_frame = tk.Frame(self, bg=WINDOW_BG)
        btn_frame.pack(pady=16)

        save_btn = tk.Button(
            btn_frame,
            text="SAVE",
            width=12,
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY,
            fg="white",
            command=self.save_item,
        )
        save_btn.grid(row=0, column=0, padx=8)

        reset_btn = tk.Button(
            btn_frame,
            text="RESET",
            width=12,
            font=FONT_BUTTON,
            command=self.reset_form,
        )
        reset_btn.grid(row=0, column=1, padx=8)

    # --- Actions ---
    def save_item(self):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        qty = self.entry_qty.get().strip()

        # === 1. Required Fields ===
        if not name or not price or not qty:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        # === 2. Validate Name ===
        if len(name) < 2:
            messagebox.showwarning("Input Error", "Item name must be at least 2 characters long!")
            return

        if len(name) > 100:
            messagebox.showwarning("Input Error", "Item name cannot exceed 100 characters!")
            return

        # Check if name is empty after stripping (e.g., all spaces)
        if not name:
            messagebox.showwarning("Input Error", "Item name cannot be empty or whitespace only!")
            return

        # Check if name is ONLY digits
        if name.isdigit():
            messagebox.showwarning("Input Error", "Item name cannot be only numbers!")
            return

        # Check if name is ONLY punctuation/symbols
        if all(not c.isalnum() for c in name):
            messagebox.showwarning("Input Error", "Item name cannot be only symbols or punctuation!")
            return

        # === 3. Validate Price ===
        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValueError("Price must be positive")
            if price_val > 999999.99:  # Set reasonable upper limit
                messagebox.showwarning("Input Error", "Price too high! Max: $999,999.99")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Enter a valid positive number for price (e.g., 5.99)!")
            return

        # === 4. Validate Quantity ===
        try:
            qty_val = int(qty)
            if qty_val <= 0:
                raise ValueError("Quantity must be positive")
            if qty_val > 10000:  # Set reasonable upper limit
                messagebox.showwarning("Input Error", "Quantity too high! Max: 10,000")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Enter a valid positive integer for quantity (e.g., 3)!")
            return

        # === 5. Save to DB ===
        try:
            db_helper.add_item(name, price_val, qty_val, tax_rate=0.1)
            messagebox.showinfo(
                "Success",
                f"Item Saved to Cart:\n\nName: {name}\nPrice: ${price_val:.2f}\nQuantity: {qty_val}",
            )
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save item: {str(e)}")

    def reset_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_qty.delete(0, tk.END)
