import tkinter as tk
from tkinter import messagebox, filedialog
from walmart_app.config import *
from walmart_app.frontend.navbar import create_navbar

# Dummy data for receipt
DUMMY_RECEIPT = {
    "store": "Walmart Shopping App",
    "date": "2025-09-21",
    "items": [
        {"name": "Apples", "qty": 3, "price": 2.50},
        {"name": "Grapes", "qty": 1, "price": 10.00},
        {"name": "Bananas", "qty": 6, "price": 0.75},
    ],
    "total": 0.0,
}


class CheckoutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller

        # create_navbar(self)

        # Title
        tk.Label(
            self, text="Checkout Receipt", font=FONT_TITLE, fg=COLOR_PRIMARY, bg=WINDOW_BG
        ).pack(pady=16)

        # Receipt Frame
        self.receipt_frame = tk.Frame(self, bg="white", bd=2, relief="solid")
        self.receipt_frame.pack(pady=20, padx=40, fill="x")

        self.render_receipt(DUMMY_RECEIPT)

        # Action Buttons
        btn_frame = tk.Frame(self, bg=WINDOW_BG)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Print Receipt",
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY,
            fg="white",
            command=self.print_receipt,
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="Back to Home",
            font=FONT_BUTTON,
            command=lambda: controller.show_page("HomePage"),
        ).pack(side="left", padx=10)

    def render_receipt(self, data):
        """Render receipt layout with dummy or real data."""
        for widget in self.receipt_frame.winfo_children():
            widget.destroy()

        # Header
        tk.Label(
            self.receipt_frame,
            text=data["store"],
            font=("Courier", 16, "bold"),
            bg="white",
        ).pack(pady=4)
        tk.Label(
            self.receipt_frame, text=f"Date: {data['date']}", font=("Courier", 12), bg="white"
        ).pack()

        tk.Label(self.receipt_frame, text="-" * 40, font=("Courier", 12), bg="white").pack()

        # Items
        total = 0.0
        for item in data["items"]:
            line = f"{item['name']} (x{item['qty']})".ljust(25)
            cost = f"${item['qty'] * item['price']:.2f}".rjust(10)
            tk.Label(self.receipt_frame, text=line + cost, font=("Courier", 12), bg="white", anchor="w").pack(fill="x", padx=10)
            total += item["qty"] * item["price"]

        tk.Label(self.receipt_frame, text="-" * 40, font=("Courier", 12), bg="white").pack()

        # Total
        tk.Label(
            self.receipt_frame,
            text=f"TOTAL: ${total:.2f}",
            font=("Courier", 14, "bold"),
            bg="white",
        ).pack(pady=6)

    def print_receipt(self):
        """Simulate printing by saving to a text file (can extend to PDF later)."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Receipt",
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=== Walmart Shopping App Receipt ===\n")
                f.write(f"Date: {DUMMY_RECEIPT['date']}\n\n")
                for item in DUMMY_RECEIPT["items"]:
                    f.write(f"{item['name']} (x{item['qty']}): ${item['qty'] * item['price']:.2f}\n")
                f.write("\n")
                total = sum(it["qty"] * it["price"] for it in DUMMY_RECEIPT["items"])
                f.write(f"TOTAL: ${total:.2f}\n")
                f.write("====================================\n")
            messagebox.showinfo("Print", f"Receipt saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save receipt: {e}")
