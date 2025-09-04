import decimal
import datetime

item_names = [("mango", 2, 12), ("grape", 4, 10)]
prices = []

def generate_text_receipt(items, total_amount, date=datetime.date.today()):
    print("----------------------------------------")
    print("             WALMART            ")
    print("----------------------------------------")
    print(f"Date: {date}")
    print("----------------------------------------")
    print("Item            Qty   Price   Total")
    print("----------------------------------------")
    for item, qty, price in items:
        item_str = item.ljust(15)
        qty_str = str(qty).ljust(5)
        price_str = f"{price:.2f}".ljust(7)
        total_item_str = f"{qty * price:.2f}"
        print(f"{item_str}{qty_str}{price_str}{total_item_str}")
    print("----------------------------------------")
    print(f"Total: {total_amount:.2f}")
    print("----------------------------------------")

def calculate_tax(price):
    tax_rate = 10.44 / 100
    return price * tax_rate

def name_input(x: int):
    name = input(f"Enter name of item {x}: ")
    try:
        name = int(name)
        print("Name cannot be a number")
        return False
    except ValueError:
        item_names.append(name)
        return name

def count_decimal_places_decimal(number):
    d = decimal.Decimal(str(number))  # Convert to string to avoid float precision issues
    return abs(d.as_tuple().exponent)

def price_input(x: int):
    price = input(f"Enter price of item {x} (Items price must be numbers or decimals. ): ")
    try:
        price = float(price)
    except ValueError:
        print("Invalid Input: Item price must be a number or decimal")
        return "Invalid Input"
    if count_decimal_places_decimal(price) > 2:
        print("WARNING: Item prices are rounded to 2 decimal places")
        change_price = input("Change item price? (y/n): ")
        if change_price == "y":
            price = price_input(x)
        else:
            price = round(price, 2)
            prices.append(price)
    return price

price = price_input(3)
# TODO: Write logic to handle commas
if price != "Invalid Input":
    generate_text_receipt(item_names, price)
