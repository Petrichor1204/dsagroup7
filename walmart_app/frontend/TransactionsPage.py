import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import datetime
from openpyxl import Workbook

import subprocess
import os
import sys

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

        # Download button
        download_btn = tk.Button(
            self,
            text="Download History (Excel)",
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY,
            fg="white",
            command=self.export_to_excel,
        )
        download_btn.pack(pady=(10, 20))

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

    def export_to_excel(self):
        transactions = db_helper.get_transactions()
        if not transactions:
            messagebox.showinfo("Export", "No transactions found to export.")
            return

        wb = Workbook()

        # Sheet 1: Transactions
        ws1 = wb.active
        ws1.title = "Transactions"
        ws1.append(["ID", "Cart ID", "Created At", "Subtotal", "Tax Total", "Grand Total"])

        for tx in transactions:
            ws1.append([
                tx["id"],
                tx.get("cart_id", ""),
                tx["created_at"],
                tx["subtotal"],
                tx["tax_total"],
                tx["grand_total"],
            ])

        # Sheet 2: Transaction Items
        ws2 = wb.create_sheet("Transaction Items")
        ws2.append(["ID", "Transaction ID", "Name", "Unit Price", "Quantity", "Tax Amount", "Line Total"])

        for tx in transactions:
            items = db_helper.get_transaction_items(tx["id"])
            for item in items:
                ws2.append([
                    item["id"],
                    tx["id"],
                    item["name"],
                    item["unit_price"],
                    item["quantity"],
                    item["tax_amount"],
                    item["line_total"],
                ])


        downloads_path = Path.home() / "Downloads"
        if not downloads_path.exists() or not os.access(downloads_path, os.W_OK):
            # Fallback to current working directory if Downloads is not accessible
            downloads_path = Path.cwd()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = downloads_path / f"order_history_{timestamp}.xlsx"

        try:
            wb.save(filename)
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save file:\n{str(e)}")
            return

        try:
            if os.name == 'nt':  # Windows
                os.startfile(filename)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', str(filename)], check=True)
            else:  # Linux and other Unix-like
                subprocess.run(['xdg-open', str(filename)], check=True)
        except Exception as e:
            messagebox.showwarning("Open Failed", f"Saved successfully but could not open automatically:\n{str(e)}")

        messagebox.showinfo("Export Successful", f"Order history exported to:\n{filename}")