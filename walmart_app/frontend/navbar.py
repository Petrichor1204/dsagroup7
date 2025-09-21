import tkinter as tk

def create_navbar(root, controller):
    nav_bar_color_bg = "#4060e1"
    nav_bar_color_fg = "white"
    nav_bar = tk.Frame(root, bg=nav_bar_color_bg, height=60)
    nav_bar.pack(fill=tk.X)

    # Use controller.show_page instead of importing pages directly
    home_button = tk.Button(
        nav_bar,
        text="Home",
        bg=nav_bar_color_bg,
        fg=nav_bar_color_fg,
        font=("Arial", 14),
        borderwidth=0,
        highlightthickness=0,
        command=lambda: controller.show_page("HomePage")
    )
    home_button.pack(side=tk.LEFT, padx=10)

    cart_button = tk.Button(
        nav_bar,
        text="Cart",
        bg=nav_bar_color_bg,
        fg=nav_bar_color_fg,
        font=("Arial", 14),
        borderwidth=0,
        highlightthickness=0,
        command=lambda: controller.show_page("ViewCartPage")
    )
    cart_button.pack(side=tk.RIGHT, padx=10)
