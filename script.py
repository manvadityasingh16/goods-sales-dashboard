import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Predefined values
regions = ['North', 'South', 'East', 'West']
categories = {
    'Electronics': ['LED TV', 'Smartphone', 'Laptop', 'Bluetooth Speaker'],
    'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Saree'],
    'Home Decor': ['Lamp', 'Wall Art', 'Curtains', 'Cushion Set'],
    'Groceries': ['Rice', 'Milk', 'Oil', 'Pulses']
}

rows = []

for i in range(1000):
    category = random.choice(list(categories.keys()))
    product = random.choice(categories[category])
    price = round(random.uniform(100, 50000), 2)
    quantity = random.randint(1, 10)
    total = round(price * quantity, 2)

    row = {
        "OrderID": f"ORD{1000 + i}",
        "Date": fake.date_between(start_date='-1y', end_date='today'),
        "CustomerName": fake.name(),
        "Region": random.choice(regions),
        "Product": product,
        "Category": category,
        "Quantity": quantity,
        "Price": price,
        "TotalSale": total
    }
    rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows)

# Save to CSV
df.to_csv("goods_sales_data.csv", index=False)

print("✅ Fake dataset 'goods_sales_data.csv' generated successfully!")
