import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Tkinter Template")

    # Example label
    label = tk.Label(root, text="Hello, Tkinter!")
    label.pack(pady=10)

    # Example button
    button = tk.Button(root, text="Click Me", command=lambda: label.config(text="Button Clicked!"))
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()