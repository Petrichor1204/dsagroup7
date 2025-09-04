import decimal
import datetime

item_names = []
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
        if price < 0:
            print("ERROR: Price cannot be negative")
            price = price_input(x)
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
    return round(price, 2)


#adding items to cart
def add_items():
    total_amount = 0
    global count
    count = 0
    while True:
        name = name_input(count + 1)
        price_before_tax = price_input(count + 1)

        tax = calculate_tax(price_before_tax)
        tax = round(tax, 2)
        price_after_tax = price_before_tax + tax
        total_amount += price_after_tax
        
        if total_amount <= 100:
            item_names.append(name)
            prices.append((price_before_tax, price_after_tax))
        else:
            print("ERROR: Your total has exceeded $100. Could not add {}".format(name))
            total_amount -= price_after_tax
            break
        count += 1

    remaining_balance = 100 - total_amount
    print("Total Ammount: {}".format(total_amount))
    print(f"Remaining balance: {round(remaining_balance, 2)}")
    choice = input("Type c to checkout or s to continue shopping (c/s): ")
    if choice == "s":
        print(f"Please add items with prices not more than {remaining_balance}")
        add_items()
    else:
        print("Checking out...")
        generate_text_receipt(item_names, total_amount)


        

add_items()

# price = price_input(3)
# # TODO: Write logic to handle commas
# if price != "Invalid Input":
#     generate_text_receipt(item_names, price)
