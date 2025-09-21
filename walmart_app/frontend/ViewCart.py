import tkinter as tk
from tkinter import messagebox
from walmart_app.config import *

# TODO: Add button that can add a new item to cart
class AddItemDialog(tk.Toplevel):
    def __init__(self, parent, on_add):
        super().__init__(parent)
        self.on_add = on_add
        self.title("Add Item to Cart")

        tk.Label(self, text="Item Name:").pack(pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.pack(pady=5)

        tk.Label(self, text="Item Price:").pack(pady=5)
        self.price_entry = tk.Entry(self)
        self.price_entry.pack(pady=5)

        tk.Label(self, text="Item Quantity:").pack(pady=5)
        self.qty_entry = tk.Entry(self)
        self.qty_entry.pack(pady=5)

        tk.Button(self, text="Add Item", command=self.add_item).pack(pady=10)

    def add_item(self):
        name = self.name_entry.get()
        price = self.price_entry.get()
        qty = self.qty_entry.get()

        if not name or not price or not qty:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            price = float(price)
            qty = int(qty)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid price or quantity.")
            return

        self.on_add({"name": name, "price": price, "qty": qty})
        self.destroy()


class ViewCartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller

        # Dummy cart data
        self.items = [
            {"name": "Apples", "price": 2.50, "qty": 3},
            {"name": "Grapes", "price": 10.00, "qty": 1},
            {"name": "Bananas", "price": 0.75, "qty": 6},
        ]

        # Title
        tk.Label(self, text="CART", font=FONT_TITLE, fg=COLOR_PRIMARY, bg=WINDOW_BG).pack(pady=16)

        # Scrollable frame for items
        canvas = tk.Canvas(self, bg=WINDOW_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=WINDOW_BG)

        self.scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Summary area
        self.summary_label = tk.Label(self, text="", font=FONT_LABEL, bg=WINDOW_BG, fg="black")
        self.summary_label.pack(pady=12)

        checkout_btn = tk.Button(
            self,
            text="Checkout",
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY,
            fg="white",
            command=self.checkout,
        )
        checkout_btn.pack(pady=(0, 20))

        self.refresh()

    # --- UI refresh ---
    def refresh(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        total_price = 0
        total_items = 0

        for idx, item in enumerate(self.items):
            name = item.get("name", "Unknown")
            price = float(item.get("price", 0))
            qty = int(item.get("qty", 1))

            total_price += price * qty
            total_items += qty

            # Row container
            row = tk.Frame(self.scroll_frame, bg=WINDOW_BG, bd=2, relief="solid")
            row.pack(fill="x", pady=6, padx=12)

            # Remove button
            tk.Button(
                row, text="X", fg="red", font=("Arial", 14, "bold"),
                command=lambda i=idx: self.remove_item(i)
            ).pack(side="left", padx=6)

            # Quantity controls
            qty_frame = tk.Frame(row, bg=WINDOW_BG)
            qty_frame.pack(side="left", padx=10)

            tk.Button(qty_frame, text="-", width=2, command=lambda i=idx: self.change_qty(i, -1)).pack(side="left")
            qty_label = tk.Label(
                qty_frame, text=str(qty), font=("Arial", 12, "bold"), width=4,
                bg="white", relief="solid"
            )
            qty_label.pack(side="left", padx=4)
            tk.Button(qty_frame, text="+", width=2, command=lambda i=idx: self.change_qty(i, +1)).pack(side="left")

            # Item name
            tk.Label(row, text=name, font=FONT_LABEL, bg=WINDOW_BG).pack(side="left", padx=12)

            # Price
            tk.Label(
                row, text=f"${price:.2f}", font=FONT_BUTTON,
                bg="white", relief="solid", width=8
            ).pack(side="right", padx=8)

        self.summary_label.config(
            text=f"Total Items: {total_items}     TOTAL: ${total_price:.2f}"
        )

    # --- Item actions ---
    def remove_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.refresh()

    def change_qty(self, index, delta):
        if 0 <= index < len(self.items):
            self.items[index]["qty"] = max(1, int(self.items[index].get("qty", 1)) + delta)
            self.refresh()

    def checkout(self):
        if not self.items:
            messagebox.showinfo("Checkout", "Cart is empty")
            return
        total = sum(float(it.get("price", 0)) * int(it.get("qty", 1)) for it in self.items)
        if messagebox.askyesno("Checkout", f"Confirm checkout — total ${total:.2f}?"):
            self.items = []
            self.refresh()
            self.controller.show_page("CheckoutPage")
