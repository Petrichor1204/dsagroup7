import tkinter as tk
from tkinter import messagebox
from walmart_app.config import *
from walmart_app.backend import db_helper


class CheckoutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller

        # Title
        tk.Label(
            self, text="CHECKOUT RECEIPT", font=FONT_TITLE, fg=COLOR_PRIMARY, bg=WINDOW_BG
        ).pack(pady=16)

        # Scrollable receipt frame
        canvas = tk.Canvas(self, bg=WINDOW_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.receipt_frame = tk.Frame(canvas, bg=WINDOW_BG)

        self.receipt_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.receipt_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        scrollbar.pack(side="right", fill="y")

        # Action buttons
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
            bg="#555",
            fg="white",
            command=lambda: controller.show_page("HomePage"),
        ).pack(side="left", padx=10)

        self.refresh()

    def refresh(self):
        """Clear and render receipt items."""
        for widget in self.receipt_frame.winfo_children():
            widget.destroy()

        items = db_helper.get_cart_items()

        if not items:
            tk.Label(
                self.receipt_frame,
                text="No items in cart.",
                font=FONT_LABEL,
                bg=WINDOW_BG,
                fg="gray",
            ).pack(pady=20)
            return

        total_price = 0
        total_items = 0

        # Table header
        header = tk.Frame(self.receipt_frame, bg=WINDOW_BG)
        header.pack(fill="x", pady=(0, 6))
        tk.Label(header, text="Item", font=FONT_LABEL, bg=WINDOW_BG, width=20).pack(
            side="left", padx=6
        )
        tk.Label(header, text="Qty", font=FONT_LABEL, bg=WINDOW_BG, width=10).pack(
            side="left", padx=6
        )
        tk.Label(header, text="Price", font=FONT_LABEL, bg=WINDOW_BG, width=10).pack(
            side="left", padx=6
        )
        tk.Label(header, text="Subtotal", font=FONT_LABEL, bg=WINDOW_BG, width=12).pack(
            side="left", padx=6
        )

        # Line items
        for item in items:
            name = item["name"]
            qty = item["quantity"]
            price = item["price"]
            subtotal = qty * price

            total_price += subtotal
            total_items += qty

            row = tk.Frame(self.receipt_frame, bg="white", bd=1, relief="solid")
            row.pack(fill="x", pady=3)

            tk.Label(row, text=name, font=FONT_BODY, bg="white", width=20, anchor="w").pack(
                side="left", padx=6
            )
            tk.Label(row, text=str(qty), font=FONT_BODY, bg="white", width=10).pack(
                side="left", padx=6
            )
            tk.Label(row, text=f"${price:.2f}", font=FONT_BODY, bg="white", width=10).pack(
                side="left", padx=6
            )
            tk.Label(
                row, text=f"${subtotal:.2f}", font=FONT_BODY, bg="white", width=12
            ).pack(side="left", padx=6)

        # Summary
        summary = tk.Frame(self.receipt_frame, bg=WINDOW_BG)
        summary.pack(fill="x", pady=12)

        tk.Label(
            summary,
            text=f"Total Items: {total_items}",
            font=FONT_LABEL,
            bg=WINDOW_BG,
        ).pack(side="left", padx=6)

        tk.Label(
            summary,
            text=f"TOTAL: ${total_price:.2f}",
            font=("Arial", 14, "bold"),
            bg=WINDOW_BG,
            fg=COLOR_PRIMARY,
        ).pack(side="right", padx=6)

    def print_receipt(self):
        """Save receipt as text file (mock print)."""
        items = db_helper.get_cart_items()
        if not items:
            messagebox.showinfo("Print", "No items to print.")
            return

        try:
            with open("receipt.txt", "w", encoding="utf-8") as f:
                f.write("==== Walmart Checkout Receipt ====\n\n")
                total = 0
                for item in items:
                    subtotal = item["quantity"] * item["price"]
                    total += subtotal
                    f.write(
                        f"{item['name']} (x{item['quantity']}) - ${item['price']:.2f} → ${subtotal:.2f}\n"
                    )
                f.write(f"\nTOTAL: ${total:.2f}\n")
                f.write("Thank you for shopping with us!\n")

            messagebox.showinfo(
                "Print", "Receipt saved as 'receipt.txt'.\n(Replace with real printer call.)"
            )
        except Exception as e:
            messagebox.showerror("Print Error", str(e))
