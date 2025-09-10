import decimal
import datetime

item_names = []
prices = []
quantities = []


def generate_text_receipt(items, total_amount, date=datetime.date.today()):
    print("----------------------------------------")
    print("             WALMART            ")
    print("----------------------------------------")
    print(f"Date: {date}")
    print("----------------------------------------")
    print("Item            Qty   Price   Tax   Total")
    print("----------------------------------------")
    # for item, qty, price in items:
    for item, quantity, price_before_tax, price_after_tax in items:
        tax = price_after_tax - price_before_tax
        item_price = price_before_tax/quantity
        item_price = round(item_price, 2)
        tax = round(tax, 2)
        item_str = item.ljust(15)
        qty_str = str(quantity).ljust(5)
        price_before_tax_str = f"{price_before_tax:.2f}".ljust(7)
        tax_str = f"{tax:.2f}".ljust(5)
        total_item_str = f"{price_after_tax:.2f}"
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
        name = name_input(x)
    except ValueError:
        # item_names.append(name)
        return name

def count_decimal_places_decimal(number):
    d = decimal.Decimal(str(number))  # Convert to string to avoid float precision issues
    return abs(d.as_tuple().exponent)

def price_input(x: int):
    price = input(f"Enter price of item {x} (Items price must be numbers or decimals. ): ")
    try:
        price = float(price)
        if price < 0:
            print("ERROR: Price cannot be negative")
            price = price_input(x)
        else:
            if count_decimal_places_decimal(price) > 2:
                print("WARNING: Item prices are rounded to 2 decimal places")
                change_price = input("Change item price? (y/n): ")
                if change_price == "y":
                    price = price_input(x)
                else:
                    price = round(price, 2)
            else:
                price = round(price, 2)

    except ValueError:
        print("ERROR: Invalid Input. Item price must be a number or decimal")
        price = price_input(x)
    return round(price, 2)

def get_quantity(item_name):
    quantity = input(f"Enter quantity of {item_name}: ")
    try:
        quantity = int(quantity)
        if quantity < 0:
            print("ERROR: Quantity cannot be negative")
            quantity = get_quantity(item_name)
        if quantity == 0:
            print("WARNING: You have entered 0 for Quantity.\n")
            remove_from_cart = input(f"Do you want to remove {item_name} from your cart? (y for yes): ")
            if remove_from_cart == "y":
                return 0
            else:
                quantity = get_quantity(item_name)
        else:
            return quantity
    except ValueError:
        print("ERROR: Invalid Input. Quantity must be a number")
        quantity = get_quantity(item_name)

#adding items to cart
def add_items():
    total_amount = 0
    global count
    count = 0
    while True:
        name = name_input(count + 1)
        item_price = price_input(count + 1)
        quantity = get_quantity(name)
        price_before_tax = item_price * quantity

        tax = calculate_tax(price_before_tax)
        tax = round(tax, 2)
        price_after_tax = price_before_tax + tax
        total_amount += price_after_tax
        if total_amount <= 100:
            item_names.append(name)
            prices.append((price_before_tax, price_after_tax))

            print("Remaining Balance: ${:.2f}".format(100 - total_amount))
            print("----------------------------------------")        
        else:
            print("\nERROR: Your total has exceeded $100. Could not add {}".format(name))
            total_amount -= price_after_tax
            break
        count += 1

    remaining_balance = 100 - total_amount
    remaining_balance = round(remaining_balance, 2)
    print(f"Remaining balance: {remaining_balance}")
    choice = input("Type c to checkout or s to continue shopping (c/s): ")
    if choice == "s":
        print(f"Please add items with prices not more than {remaining_balance}")
        add_items() # TODO: Fix this so that the remaning balance does not start afresh
    elif choice == "c":
        print("Checking out...")
        # items = list(zip(item_names, prices))
        items = [(item_names[i], prices[i]) for i in range(len(item_names))]
        print("\nITEMS ARRAY:")
        print(items)
        print()
        total_amount = round(total_amount, 2)
        # generate_text_receipt(items, total_amount)
    else:
        print("Invalid Input")


add_items()
