import tkinter as tk
from tkinter import messagebox
from walmart_app.config import *
from walmart_app.backend import db_helper
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
import datetime
import subprocess
import os
import sys


class CheckoutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=WINDOW_BG)
        self.controller = controller
        self.items = []
        self.current_tx = None  # will hold transaction info after confirm

        # Title
        tk.Label(
            self,
            text="CHECKOUT RECEIPT",
            font=FONT_TITLE,
            fg=COLOR_PRIMARY,
            bg=WINDOW_BG,
        ).pack(pady=16)

        # Scrollable frame
        canvas_widget = tk.Canvas(self, bg=WINDOW_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas_widget.yview)
        self.scroll_frame = tk.Frame(canvas_widget, bg=WINDOW_BG)

        self.scroll_frame.bind(
            "<Configure>", lambda e: canvas_widget.configure(scrollregion=canvas_widget.bbox("all"))
        )

        canvas_widget.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas_widget.configure(yscrollcommand=scrollbar.set)

        canvas_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Summary
        self.summary_label = tk.Label(
            self, text="", font=FONT_LABEL, bg=WINDOW_BG, fg="black", justify="left"
        )
        self.summary_label.pack(pady=12)

        # Buttons
        btn_frame = tk.Frame(self, bg=WINDOW_BG)
        btn_frame.pack(pady=12)

        tk.Button(
            btn_frame,
            text="Confirm Purchase",
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY,
            fg="white",
            command=self.confirm_checkout,
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame,
            text="Print Receipt",
            font=FONT_BUTTON,
            bg="gray",
            fg="white",
            command=self.print_receipt,
        ).pack(side="left", padx=8)

    # --- Refresh page ---
    def refresh(self):
        """Reload cart items from DB and render receipt preview."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.items = db_helper.get_cart_items()
        subtotal = sum(it["price"] * it["quantity"] for it in self.items)
        tax_total = sum((it["price"] * it["quantity"]) * it.get("tax_rate", 0.1) for it in self.items)
        grand_total = subtotal + tax_total

        for item in self.items:
            row = tk.Frame(self.scroll_frame, bg=WINDOW_BG)
            row.pack(fill="x", pady=4, padx=12)
            tk.Label(row, text=f"{item['name']} (x{item['quantity']})", font=FONT_LABEL, bg=WINDOW_BG).pack(side="left")
            tk.Label(row, text=f"${item['price'] * item['quantity']:.2f}", font=FONT_BUTTON, bg=WINDOW_BG).pack(side="right")

        self.summary_label.config(
            text=f"Subtotal: ${subtotal:.2f}\nTax: ${tax_total:.2f}\n--------------------\nGrand Total: ${grand_total:.2f}"
        )

    # --- Confirm purchase ---
    def confirm_checkout(self):
        if not self.items:
            messagebox.showinfo("Checkout", "Cart is empty")
            return

        subtotal = sum(it["price"] * it["quantity"] for it in self.items)
        tax_total = sum((it["price"] * it["quantity"]) * it.get("tax_rate", 0.1) for it in self.items)
        grand_total = subtotal + tax_total

        if messagebox.askyesno("Confirm Purchase", f"Confirm checkout — total ${grand_total:.2f}?"):
            tx_id = db_helper.complete_checkout(self.items, subtotal, tax_total, grand_total)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.current_tx = {
                "id": tx_id,
                "date": now,
                "subtotal": subtotal,
                "tax": tax_total,
                "total": grand_total,
                "items": self.items,
            }
            messagebox.showinfo("Checkout", f"Purchase successful!\nTransaction ID: {tx_id}")
            db_helper.clear_cart()
            # self.controller.show_page("HomePage")

    # --- Print receipt to PDF ---
    def print_receipt(self):
        if not self.current_tx:
            messagebox.showinfo("Print", "No receipt available. Please checkout first.")
            return

        tx = self.current_tx
        filename = f"receipt_{tx['id']}.pdf"

        # Try to save to Downloads folder, fallback to current directory
        downloads_path = Path.home() / "Downloads"
        if not downloads_path.exists():
            downloads_path = Path.cwd()

        filepath = downloads_path / filename

        try:
            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Use monospaced font for alignment
            c.setFont("Courier", 10)
            left_margin = 50
            top_margin = height - 50
            line_height = 14

            y = top_margin

            # Generate receipt lines exactly as in your text format
            total_before_tax = tx["subtotal"]
            total_tax = tx["tax"]
            total_after_tax = tx["total"]
            item_count = sum(it["quantity"] for it in tx["items"])

            # Precompute tax and price_after_tax per item if not already present
            items_with_tax = []
            for it in tx["items"]:
                tax_rate = it.get("tax_rate", 0.1)  # default 10%
                tax_amount = it["price"] * it["quantity"] * tax_rate
                price_after_tax = (it["price"] * it["quantity"]) + tax_amount
                items_with_tax.append({
                    **it,
                    "tax": tax_amount,
                    "price_after_tax": price_after_tax
                })

            lines = [
                "----------------------------------------",
                "             WALMART                    ",
                "----------------------------------------",
                f"Date: {tx['date']}",
                "----------------------------------------",
                "Item            Qty   Price    Tax      Line Total",
                "----------------------------------------"
            ]

            for it in items_with_tax:
                # Truncate long item names to fit column
                name = (it['name'][:14] + '..') if len(it['name']) > 15 else it['name']
                line = f"{name:<15} {it['quantity']:<5} ${it['price'] * it['quantity']:<7.2f} ${it['tax']:<7.2f} ${it['price_after_tax']:<7.2f}"
                lines.append(line)

            lines.extend([
                "----------------------------------------",
                f"Items purchased: {item_count}",
                f"Subtotal (before tax): ${total_before_tax:.2f}",
                f"Tax: ${total_tax:.2f}",
                f"Total (after tax): ${total_after_tax:.2f}",
                "----------------------------------------",
                "",
                "Thank you for shopping at Walmart!"
            ])

            # Draw each line
            for line in lines:
                c.drawString(left_margin, y, line)
                y -= line_height
                if y < 50:  # Add new page if needed
                    c.showPage()
                    y = height - 50
                    c.setFont("Courier", 10)

            c.save()

            messagebox.showinfo("Receipt Saved", f"Receipt saved to:\n{filepath}")

            # Attempt to open the PDF with default viewer
            try:
                if sys.platform == "win32":
                    os.startfile(filepath)
                elif sys.platform == "darwin":
                    subprocess.run(["open", filepath])
                else:
                    subprocess.run(["xdg-open", filepath])
            except Exception as e:
                messagebox.showwarning("Open File", f"Could not open the receipt file automatically:\n{str(e)}")
                # Provide manual instructions
                messagebox.showinfo("Manual Open", f"Please open the file manually:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{str(e)}")