import tkinter as tk
from walmart_app.config import *


class BaseWindow(tk.Tk):
    """Main application window that manages different pages and navigation."""

    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(bg=WINDOW_BG)

        # Navigation history
        self.history = []
        self.history_index = -1

        # Navbar
        self._create_navbar()

        # Container for pages (below navbar)
        self.container = tk.Frame(self, bg=WINDOW_BG)
        self.container.pack(fill="both", expand=True, padx=10, pady=10, anchor="center")

        # Make container a grid with stretchable center cell
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.current_page = None

    def _create_navbar(self):
        nav_bar_color_bg = "#4060e1"
        nav_bar_color_fg = "white"

        navbar = tk.Frame(self, bg=nav_bar_color_bg, height=60)
        navbar.pack(fill=tk.X, side="top")

        # Back button
        tk.Button(
            navbar,
            text="⬅ Back",
            bg=nav_bar_color_bg,
            fg=nav_bar_color_fg,
            font=("Arial", 12, "bold"),
            borderwidth=0,
            command=self.go_back,
        ).pack(side=tk.LEFT, padx=10)

        # Forward button
        tk.Button(
            navbar,
            text="Forward ➡",
            bg=nav_bar_color_bg,
            fg=nav_bar_color_fg,
            font=("Arial", 12, "bold"),
            borderwidth=0,
            command=self.go_forward,
        ).pack(side=tk.LEFT, padx=10)

        # Home button
        tk.Button(
            navbar,
            text="Home",
            bg=nav_bar_color_bg,
            fg=nav_bar_color_fg,
            font=("Arial", 14),
            borderwidth=0,
            command=lambda: self.show_page("HomePage"),
        ).pack(side=tk.RIGHT, padx=10)

        # Cart button
        tk.Button(
            navbar,
            text="Cart",
            bg=nav_bar_color_bg,
            fg=nav_bar_color_fg,
            font=("Arial", 14),
            borderwidth=0,
            command=lambda: self.show_page("ViewCartPage"),
        ).pack(side=tk.RIGHT, padx=10)

        # Transactions button
        tk.Button(
            navbar,
            text="Transactions",
            bg=nav_bar_color_bg,
            fg=nav_bar_color_fg,
            font=("Arial", 14),
            borderwidth=0,
            command=lambda: self.show_page("TransactionsPage"),
        ).pack(side=tk.RIGHT, padx=10)

    def add_page(self, page_class, name):
        """Register a page by class."""
        frame = page_class(self.container, self)
        self.frames[name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def show_page(self, name, add_to_history=True):
        """Show a page by name and update history."""
        if name not in self.frames:
            return

        frame = self.frames[name]
        frame.tkraise()
        self.current_page = name

        # Always refresh if page has a refresh method
        if hasattr(frame, "refresh"):
            frame.refresh()

        if add_to_history:
            # Cut forward history when new nav occurs
            self.history = self.history[: self.history_index + 1]
            self.history.append(name)
            self.history_index += 1

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            page = self.history[self.history_index]
            self.show_page(page, add_to_history=False)

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            page = self.history[self.history_index]
            self.show_page(page, add_to_history=False)

