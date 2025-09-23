import tkinter as tk
from tkinter import messagebox
from walmart_app.config import *
from walmart_app.backend import db_helper


class ViewCartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller
        self.items = []

        # Title
        tk.Label(
            self,
            text="CART",
            font=FONT_TITLE,
            fg=COLOR_PRIMARY,
            bg=WINDOW_BG,
        ).pack(pady=16)

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
        self.summary_label = tk.Label(
            self, text="", font=FONT_LABEL, bg=WINDOW_BG, fg="black"
        )
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
        """Clear and reload items from DB."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.items = db_helper.get_cart_items()

        total_price = 0
        total_items = 0

        for item in self.items:
            item_id = item["id"]
            name = item["name"]
            price = float(item["price"])
            qty = int(item["quantity"])

            total_price += price * qty
            total_items += qty

            # Row container
            row = tk.Frame(self.scroll_frame, bg=WINDOW_BG, bd=2, relief="solid")
            row.pack(fill="x", pady=6, padx=12)

            # Remove button
            tk.Button(
                row,
                text="X",
                fg="red",
                font=("Arial", 14, "bold"),
                command=lambda i=item_id: self.remove_item(i),
            ).pack(side="left", padx=6)

            # Quantity controls
            qty_frame = tk.Frame(row, bg=WINDOW_BG)
            qty_frame.pack(side="left", padx=10)

            # Qty label (pass this into change_qty)
            qty_label = tk.Label(
                qty_frame,
                text=str(qty),
                font=("Arial", 12, "bold"),
                width=4,
                bg="white",
                relief="solid",
            )
            qty_label.pack(side="left", padx=4)

            # Subtotal label (pass this too)
            subtotal_label = tk.Label(
                row,
                text=f"${price * qty:.2f}",
                font=FONT_BUTTON,
                bg="white",
                relief="solid",
                width=10,
            )
            subtotal_label.pack(side="right", padx=8)

            tk.Button(
                qty_frame,
                text="-",
                width=2,
                command=lambda i=item_id, ql=qty_label, sl=subtotal_label, p=price: self.change_qty(i, -1, ql, sl, p),
            ).pack(side="left")

            tk.Button(
                qty_frame,
                text="+",
                width=2,
                command=lambda i=item_id, ql=qty_label, sl=subtotal_label, p=price: self.change_qty(i, +1, ql, sl, p),
            ).pack(side="left")

            # Item name
            tk.Label(row, text=name, font=FONT_LABEL, bg=WINDOW_BG).pack(
                side="left", padx=12
            )

        self.summary_label.config(
            text=f"Total Items: {total_items}     TOTAL: ${total_price:.2f}"
        )


    # --- Item actions ---
    def remove_item(self, item_id):
        db_helper.remove_item(item_id)
        self.refresh()

    def change_qty(self, item_id, delta, qty_label=None, subtotal_label=None, price=0.0):
        for item in self.items:
            if item["id"] == item_id:
                new_qty = max(1, item["quantity"] + delta)
                db_helper.update_item_qty(item_id, new_qty)
                item["quantity"] = new_qty  # keep local copy in sync

                # Update UI labels live
                if qty_label:
                    qty_label.config(text=str(new_qty))
                if subtotal_label:
                    subtotal_label.config(text=f"${price * new_qty:.2f}")

        # Update totals
        self.update_summary()

    def update_summary(self):
        total_price = sum(it["price"] * it["quantity"] for it in self.items)
        total_items = sum(it["quantity"] for it in self.items)
        self.summary_label.config(
            text=f"Total Items: {total_items}     TOTAL: ${total_price:.2f}"
        )

    def checkout(self):
        if not self.items:
            messagebox.showinfo("Checkout", "Cart is empty")
            return
        total = sum(it["price"] * it["quantity"] for it in self.items)
        if messagebox.askyesno("Checkout", f"Confirm checkout — total ${total:.2f}?"):
            # db_helper.clear_cart()
            # self.refresh()
            # messagebox.showinfo("Checkout", "Checkout complete — cart cleared")
            self.controller.show_page("CheckoutPage")

