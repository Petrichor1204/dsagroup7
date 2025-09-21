from walmart_app.frontend.BaseWindow import BaseWindow
from walmart_app.frontend.home import HomePage
from walmart_app.frontend.AddItem import AddItemPage
from walmart_app.frontend.ViewCart import ViewCartPage
from walmart_app.frontend.Checkout import CheckoutPage


def run_app():
    app = BaseWindow()

    # Register pages
    app.add_page(HomePage, "HomePage")
    app.add_page(AddItemPage, "AddItemPage")
    app.add_page(ViewCartPage, "ViewCartPage")
    app.add_page(CheckoutPage, "CheckoutPage")

    # Show home page first
    app.show_page("HomePage")

    app.mainloop()


if __name__ == "__main__":
    run_app()
