import tkinter as tk
from walmart_app.config import *
from walmart_app.backend import db_helper


class TransactionsPage(tk.Frame):
    """Page to display past transactions (order history)."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller

        # Title
        tk.Label(
            self, text="ORDER HISTORY", font=FONT_TITLE, fg=COLOR_PRIMARY, bg=WINDOW_BG
        ).pack(pady=16)

        # Scrollable area
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

        self.refresh()

    def refresh(self):
        """Load transactions and display them."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        transactions = db_helper.get_transactions()
        if not transactions:
            tk.Label(
                self.scroll_frame,
                text="No past transactions found.",
                font=FONT_LABEL,
                bg=WINDOW_BG,
                fg="gray",
            ).pack(pady=20)
            return

        for tx in transactions:
            frame = tk.Frame(self.scroll_frame, bg="white", bd=2, relief="solid")
            frame.pack(fill="x", pady=8, padx=12)

            # Header
            tk.Label(
                frame,
                text=f"Transaction ID: {tx['id']}",
                font=("Arial", 10),
                bg="white",
                fg="gray",
                anchor="w",
            ).pack(fill="x")

            tk.Label(
                frame,
                text=f"Date: {tx['created_at']}",
                font=("Arial", 11),
                bg="white",
                anchor="w",
            ).pack(fill="x", padx=6)

            # Items
            items = db_helper.get_transaction_items(tx["id"])
            for item in items:
                tk.Label(
                    frame,
                    text=f"  {item['name']} (x{item['quantity']}) - ${item['line_total']:.2f}",
                    font=FONT_BODY,
                    bg="white",
                    anchor="w",
                ).pack(fill="x", padx=12)

            # Totals
            tk.Label(
                frame,
                text=f"Subtotal: ${tx['subtotal']:.2f} | Tax: ${tx['tax_total']:.2f} | Grand Total: ${tx['grand_total']:.2f}",
                font=FONT_LABEL,
                bg="white",
                fg=COLOR_PRIMARY,
            ).pack(anchor="e", padx=12, pady=(4, 6))
