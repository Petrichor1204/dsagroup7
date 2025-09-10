import datetime
import decimal

TAX_RATE = 0.1044
BUDGET = 100.00
BUDGET_WARN_THRESHOLD = 10.00  # warn when remaining <= $10

class ShoppingCart:
    def __init__(self):
        self.items = []
        self.total_amount = 0.0

    def add_item(self, name, price, quantity):
        price_before_tax = round(price * quantity, 2)
        tax = self.calculate_tax(price_before_tax)
        price_after_tax = round(price_before_tax + tax, 2)

        if self.total_amount + price_after_tax > BUDGET:
            remaining = self.get_remaining_balance()
            print(f"\nERROR: Adding {name} would exceed your ${BUDGET:.2f} budget.")
            print(f"Remaining balance: ${remaining:.2f}")
            while True:
                choice = input("Type 'c' to checkout or 'k' to keep shopping: ").strip().lower()
                if choice == 'c':
                    return "checkout"
                if choice == 'k':
                    return "keep_shopping"
                print("Invalid choice. Enter 'c' or 'k'.")

        # Update state
        self.total_amount = round(self.total_amount + price_after_tax, 2)
        self.items.append({
            "name": name,
            "price": round(price, 2),
            "quantity": quantity,
            "price_before_tax": price_before_tax,
            "tax": tax,
            "price_after_tax": price_after_tax
        })
        return "added"

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            line = self.items.pop(index)
            self.total_amount = round(self.total_amount - line["price_after_tax"], 2)
            print(f"Removed '{line['name']}' (x{line['quantity']}).")
            return True
        print("Invalid index.")
        return False

    def calculate_tax(self, price):
        return round(price * TAX_RATE, 2)

    def get_total(self):
        return self.total_amount

    def get_remaining_balance(self):
        return round(BUDGET - self.total_amount, 2)

    def get_totals_breakdown(self):
        total_before_tax = round(sum(it["price_before_tax"] for it in self.items), 2)
        total_tax = round(sum(it["tax"] for it in self.items), 2)
        total_after_tax = round(total_before_tax + total_tax, 2)
        item_count = sum(it["quantity"] for it in self.items)
        return total_before_tax, total_tax, total_after_tax, item_count

    def generate_receipt(self, date=datetime.date.today()):
        total_before_tax, total_tax, total_after_tax, item_count = self.get_totals_breakdown()
        lines = [
            "----------------------------------------",
            "             WALMART                    ",
            "----------------------------------------",
            f"Date: {date}",
            "----------------------------------------",
            "Item            Qty   Price    Tax      Line Total",
            "----------------------------------------"
        ]
        for it in self.items:
            lines.append(
                f"{it['name']:<15} {it['quantity']:<5} ${it['price']:<7.2f} ${it['tax']:<7.2f} ${it['price_after_tax']:<7.2f}"
            )
        lines.extend([
            "----------------------------------------",
            f"Items purchased: {item_count}",
            f"Subtotal (before tax): ${total_before_tax:.2f}",
            f"Tax: ${total_tax:.2f}",
            f"Total (after tax): ${total_after_tax:.2f}",
            "----------------------------------------"
        ])
        return "\n".join(lines)

def get_name_input(count):
    while True:
        name = input(f"Enter name of item {count}: ")
        try:
            int(name)
            print("Name cannot be a number")
        except ValueError:
            if not name.strip():
                print("Name cannot be empty")
            else:
                return name.strip()

def get_price_input(name):
    while True:
        price_str = input(f"Enter price of {name} ({TAX_RATE*100:.2f}% tax is applied on all items): ")
        try:
            price = float(price_str)
            if price < 0:
                print("ERROR: Price cannot be negative")
                continue
            if abs(decimal.Decimal(price_str).as_tuple().exponent) > 2:
                print("WARNING: Item prices are rounded to 2 decimal places")
                if input("Change item price? (y/n): ").lower() == "y":
                    continue
            return round(price, 2)
        except (ValueError, decimal.InvalidOperation):
            print("ERROR: Invalid Input. Item price must be a number or decimal")

def get_quantity_input(name):
    while True:
        quantity_str = input(f"Enter quantity of {name}: ")
        try:
            quantity = int(quantity_str)
            if quantity < 0:
                print("ERROR: Quantity cannot be negative")
                continue
            if quantity == 0:
                print("WARNING: You entered 0 for quantity. Item will not be added.")
                return 0
            return quantity
        except ValueError:
            print("ERROR: Invalid Input. Quantity must be a number")

def main():
    cart = ShoppingCart()
    item_count = 1

    while True:
        remaining = cart.get_remaining_balance()
        print("\n--- Walmart Shopping System ---")
        print(f"Remaining Balance: ${remaining:.2f}")
        if remaining <= BUDGET_WARN_THRESHOLD and remaining > 0:
            print("WARNING: You are close to your budget limit.")

        print("1. Add item")
        print("2. View / remove items")
        print("3. Checkout")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            name = get_name_input(item_count)
            price = get_price_input(name)
            quantity = get_quantity_input(name)
            if quantity > 0:
                result = cart.add_item(name, price, quantity)
                if result == "added":
                    item_count += 1
                    print(f"'{name}' added to cart.")
                elif result == "checkout":
                    print("\nChecking out...")
                    print(cart.generate_receipt())
                    break
                # If result is "keep_shopping", we do nothing and the loop continues.
        elif choice == "2":
            print("\n--- Current Cart ---")
            if not cart.items:
                print("Your cart is empty.")
            else:
                for idx, it in enumerate(cart.items):
                    print(f"{idx}. {it['name']} (x{it['quantity']}): ${it['price_after_tax']:.2f}")
                print(f"Total: ${cart.get_total():.2f}")
                if input("Remove an item? (y/n): ").strip().lower() == "y":
                    try:
                        rm_idx = int(input("Enter the index to remove: "))
                        cart.remove_item(rm_idx)
                    except ValueError:
                        print("Invalid index.")
        elif choice == "3":
            print("\nChecking out...")
            print(cart.generate_receipt())
            break
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

try:
    main()
except KeyboardInterrupt:
    print("\nThank you for shopping with Walmart...")
