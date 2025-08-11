"""
sample_data.py
Populates the database with realistic sample data for testing the AI agent.

HOW TO USE:
1. Make sure you've run 'python database_setup.py' first
2. Save this file as 'sample_data.py' in your project folder
3. Run: python sample_data.py
4. This will add 100+ sample records to your database
"""

import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker for generating realistic data
fake = Faker()

def connect_db():
    """Connect to the database"""
    return sqlite3.connect('inventory_sales.db')

def insert_categories(conn):
    """Insert product categories"""
    print("📁 Adding categories...")
    
    categories = [
        ("Electronics", "Consumer electronics and gadgets"),
        ("Clothing", "Apparel and fashion items"),
        ("Home & Garden", "Home improvement and garden supplies"),
        ("Books", "Books and educational materials"),
        ("Sports", "Sports equipment and accessories"),
        ("Automotive", "Car parts and accessories"),
        ("Health & Beauty", "Health and beauty products"),
        ("Toys & Games", "Toys and gaming products"),
        ("Office Supplies", "Office and business supplies"),
        ("Kitchen & Dining", "Kitchenware and dining accessories")
    ]
    
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO categories (category_name, description) VALUES (?, ?)",
        categories
    )
    conn.commit()
    print(f"✅ Added {len(categories)} categories")

def insert_suppliers(conn):
    """Insert suppliers"""
    print("🏢 Adding suppliers...")
    
    suppliers = []
    for _ in range(15):
        suppliers.append((
            fake.company(),
            fake.name(),
            fake.email(),
            fake.phone_number()[:20],
            fake.address(),
            fake.city(),
            fake.country()
        ))
    
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO suppliers (supplier_name, contact_person, email, phone, address, city, country)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, suppliers)
    conn.commit()
    print(f"✅ Added {len(suppliers)} suppliers")

def insert_warehouses(conn):
    """Insert warehouses"""
    print("🏭 Adding warehouses...")
    
    warehouses = [
        ("Main Warehouse", "Lagos, Nigeria", 10000, "John Adebayo", "+234-801-234-5678"),
        ("North Warehouse", "Kano, Nigeria", 8000, "Fatima Hassan", "+234-802-345-6789"),
        ("South Warehouse", "Port Harcourt, Nigeria", 6000, "Emeka Okafor", "+234-803-456-7890"),
        ("West Warehouse", "Ibadan, Nigeria", 7500, "Bola Tinubu", "+234-804-567-8901"),
        ("East Warehouse", "Enugu, Nigeria", 5500, "Chika Okwu", "+234-805-678-9012")
    ]
    
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO warehouses (warehouse_name, location, capacity, manager_name, phone)
        VALUES (?, ?, ?, ?, ?)
    """, warehouses)
    conn.commit()
    print(f"✅ Added {len(warehouses)} warehouses")

def insert_products(conn):
    """Insert products"""
    print("📦 Adding products...")
    
    # Product templates by category
    product_templates = {
        1: [  # Electronics
            ("iPhone 15 Pro", "Latest Apple smartphone", 899.99, 750.00, "0.17 kg", "146.6x70.6x7.8 mm"),
            ("Samsung Galaxy S24", "Android flagship phone", 799.99, 650.00, "0.16 kg", "147x70.6x7.6 mm"),
            ("MacBook Air M3", "Apple laptop computer", 1299.99, 1050.00, "1.24 kg", "304x213x11.3 mm"),
            ("Dell XPS 13", "Windows ultrabook", 999.99, 820.00, "1.2 kg", "296x199x14.8 mm"),
            ("iPad Pro 11", "Professional tablet", 799.99, 650.00, "0.47 kg", "248x178.5x5.9 mm"),
            ("AirPods Pro", "Wireless earbuds", 249.99, 180.00, "0.056 kg", "30.9x21.8x24.0 mm"),
            ("Sony WH-1000XM5", "Noise cancelling headphones", 399.99, 280.00, "0.25 kg", "254x220 mm"),
            ("Nintendo Switch", "Gaming console", 299.99, 220.00, "0.4 kg", "239x102x13.9 mm"),
        ],
        2: [  # Clothing
            ("Nike Air Force 1", "Classic white sneakers", 109.99, 65.00, "0.5 kg", "Size 9"),
            ("Levi's 501 Jeans", "Original fit jeans", 79.99, 45.00, "0.6 kg", "32x34"),
            ("Adidas Hoodie", "Cotton blend hoodie", 69.99, 35.00, "0.4 kg", "Medium"),
            ("Tommy Hilfiger Shirt", "Cotton dress shirt", 89.99, 50.00, "0.3 kg", "Large"),
            ("Zara Dress", "Summer floral dress", 59.99, 30.00, "0.2 kg", "Size 8"),
            ("H&M T-Shirt", "Basic cotton t-shirt", 19.99, 8.00, "0.15 kg", "Medium"),
        ],
        3: [  # Home & Garden
            ("Dyson V15 Vacuum", "Cordless vacuum cleaner", 649.99, 450.00, "3.0 kg", "1257x250x166 mm"),
            ("KitchenAid Mixer", "Stand mixer", 349.99, 220.00, "10.9 kg", "355x221x406 mm"),
            ("IKEA Sofa", "3-seat sofa", 499.99, 280.00, "45 kg", "218x88x88 cm"),
            ("Garden Hose", "50ft expandable hose", 39.99, 18.00, "2.0 kg", "50 ft"),
        ]
    }
    
    products = []
    product_id = 1
    
    for category_id, product_list in product_templates.items():
        for name, desc, price, cost, weight, dimensions in product_list:
            # Create multiple variants with different suppliers
            for i in range(2):  # 2 variants each
                supplier_id = random.randint(1, 15)
                code = f"PRD{product_id:04d}"
                
                products.append((
                    name + (f" - Variant {i+1}" if i > 0 else ""),
                    code,
                    category_id,
                    supplier_id,
                    desc,
                    price + random.uniform(-50, 50),  # Price variation
                    cost + random.uniform(-20, 20),   # Cost variation
                    weight,
                    dimensions,
                    1  # is_active
                ))
                product_id += 1
    
    # Add more random products to reach 100+
    categories = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for i in range(50):  # Add 50 more random products
        category_id = random.choice(categories)
        supplier_id = random.randint(1, 15)
        code = f"PRD{product_id:04d}"
        
        products.append((
            fake.word().capitalize() + " " + fake.word().capitalize(),
            code,
            category_id,
            supplier_id,
            fake.text(max_nb_chars=100),
            round(random.uniform(10, 1000), 2),
            round(random.uniform(5, 800), 2),
            f"{random.uniform(0.1, 5):.2f} kg",
            f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)} cm",
            random.choice([1, 1, 1, 0])  # 75% active
        ))
        product_id += 1
    
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO products (product_name, product_code, category_id, supplier_id, description, 
                            unit_price, cost_price, weight, dimensions, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products)
    conn.commit()
    print(f"✅ Added {len(products)} products")

def insert_customers(conn):
    """Insert customers"""
    print("👥 Adding customers...")
    
    customers = []
    for i in range(50):
        customer_type = random.choice(['Individual', 'Business'])
        if customer_type == 'Business':
            name = fake.company()
            credit_limit = random.uniform(5000, 50000)
        else:
            name = fake.name()
            credit_limit = random.uniform(500, 5000)
        
        customers.append((
            name,
            customer_type,
            fake.email(),
            fake.phone_number()[:20],
            fake.address(),
            fake.city(),
            "Nigeria",
            round(credit_limit, 2)
        ))
    
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO customers (customer_name, customer_type, email, phone, address, city, country, credit_limit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)
    conn.commit()
    print(f"✅ Added {len(customers)} customers")

def insert_inventory(conn):
    """Insert inventory records"""
    print("📊 Adding inventory...")
    
    cursor = conn.cursor()
    
    # Get all products and warehouses
    cursor.execute("SELECT product_id FROM products")
    products = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT warehouse_id FROM warehouses")
    warehouses = [row[0] for row in cursor.fetchall()]
    
    inventory = []
    for product_id in products:
        # Not all products in all warehouses (realistic scenario)
        selected_warehouses = random.sample(warehouses, random.randint(1, len(warehouses)))
        
        for warehouse_id in selected_warehouses:
            qty_on_hand = random.randint(0, 500)
            qty_reserved = random.randint(0, min(qty_on_hand, 50))
            reorder_level = random.randint(5, 30)
            max_stock = random.randint(100, 1000)
            
            inventory.append((
                product_id,
                warehouse_id,
                qty_on_hand,
                qty_reserved,
                reorder_level,
                max_stock
            ))
    
    cursor.executemany("""
        INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, quantity_reserved, reorder_level, max_stock_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, inventory)
    conn.commit()
    print(f"✅ Added {len(inventory)} inventory records")

def insert_sales_orders(conn):
    """Insert sales orders and order items"""
    print("💰 Adding sales orders...")
    
    cursor = conn.cursor()
    
    # Get customers, warehouses, and products for orders
    cursor.execute("SELECT customer_id FROM customers")
    customers = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT warehouse_id FROM warehouses")
    warehouses = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id, unit_price FROM products WHERE is_active = 1")
    products = cursor.fetchall()
    
    # Generate orders from last 6 months
    start_date = datetime.now() - timedelta(days=180)
    orders = []
    order_items = []
    
    for i in range(100):  # 100 orders
        order_id = i + 1
        customer_id = random.choice(customers)
        warehouse_id = random.choice(warehouses)
        order_date = fake.date_between(start_date, datetime.now().date())
        
        # Order status distribution
        status_weights = [
            ('Delivered', 0.6),
            ('Shipped', 0.15),
            ('Processing', 0.1),
            ('Pending', 0.1),
            ('Cancelled', 0.05)
        ]
        order_status = random.choices(
            [s[0] for s in status_weights],
            weights=[s[1] for s in status_weights]
        )[0]
        
        payment_status = 'Paid' if order_status in ['Delivered', 'Shipped'] else random.choice(['Pending', 'Paid', 'Partial'])
        
        # Calculate dates based on status
        required_date = order_date + timedelta(days=random.randint(1, 14))
        shipped_date = order_date + timedelta(days=random.randint(1, 5)) if order_status in ['Shipped', 'Delivered'] else None
        
        # Select 1-5 products for this order
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)
        
        subtotal = 0
        for product_id, unit_price in selected_products:
            quantity = random.randint(1, 10)
            discount = random.uniform(0, 15)  # 0-15% discount
            line_total = quantity * unit_price * (1 - discount/100)
            subtotal += line_total
            
            order_items.append((
                order_id,
                product_id,
                quantity,
                unit_price,
                discount,
                round(line_total, 2)
            ))
        
        tax_amount = subtotal * 0.075  # 7.5% VAT
        shipping_cost = random.uniform(5, 50)
        total_amount = subtotal + tax_amount + shipping_cost
        
        orders.append((
            f"ORD{order_id:05d}",
            customer_id,
            warehouse_id,
            order_date,
            required_date,
            shipped_date,
            order_status,
            payment_status,
            round(subtotal, 2),
            round(tax_amount, 2),
            round(shipping_cost, 2),
            round(total_amount, 2),
            fake.text(max_nb_chars=100) if random.random() < 0.3 else None
        ))
    
    # Insert orders
    cursor.executemany("""
        INSERT INTO sales_orders (order_number, customer_id, warehouse_id, order_date, required_date, 
                                shipped_date, order_status, payment_status, subtotal, tax_amount, 
                                shipping_cost, total_amount, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders)
    
    # Insert order items
    cursor.executemany("""
        INSERT INTO sales_order_items (order_id, product_id, quantity, unit_price, discount_percentage, line_total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, order_items)
    
    conn.commit()
    print(f"✅ Added {len(orders)} sales orders with {len(order_items)} line items")

def insert_inventory_movements(conn):
    """Insert inventory movements"""
    print("📈 Adding inventory movements...")
    
    cursor = conn.cursor()
    
    # Get inventory records
    cursor.execute("""
        SELECT i.product_id, i.warehouse_id, i.quantity_on_hand 
        FROM inventory i 
        WHERE i.quantity_on_hand > 0
        LIMIT 200
    """)
    inventory_records = cursor.fetchall()
    
    movements = []
    for product_id, warehouse_id, qty_on_hand in inventory_records:
        # Generate random movements over the last 6 months
        num_movements = random.randint(1, 10)
        for _ in range(num_movements):
            movement_type = random.choice(['IN', 'OUT', 'ADJUSTMENT'])
            quantity = random.randint(1, min(50, qty_on_hand))
            
            if movement_type == 'OUT':
                quantity = -quantity
            
            reference_type = {
                'IN': 'PURCHASE_ORDER',
                'OUT': 'SALES_ORDER',
                'ADJUSTMENT': 'ADJUSTMENT'
            }[movement_type]
            
            movement_date = fake.date_time_between(start_date='-6M', end_date='now')
            
            movements.append((
                product_id,
                warehouse_id,
                movement_type,
                quantity,
                reference_type,
                random.randint(1, 100),  # reference_id
                movement_date,
                fake.text(max_nb_chars=50) if random.random() < 0.2 else None
            ))
    
    cursor.executemany("""
        INSERT INTO inventory_movements (product_id, warehouse_id, movement_type, quantity, 
                                       reference_type, reference_id, movement_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, movements)
    conn.commit()
    print(f"✅ Added {len(movements)} inventory movements")

def verify_data(conn):
    """Verify the data was inserted correctly"""
    print("\n🔍 Verifying data...")
    
    cursor = conn.cursor()
    
    tables_to_check = [
        'categories', 'suppliers', 'warehouses', 'products', 
        'customers', 'inventory', 'sales_orders', 'sales_order_items', 
        'inventory_movements'
    ]
    
    total_records = 0
    for table in tables_to_check:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  📋 {table}: {count} records")
        total_records += count
    
    print(f"\n🎉 Total records in database: {total_records}")
    return total_records

def main():
    """Main function to populate the database"""
    print("🚀 Populating Inventory & Sales Database...")
    print("=" * 50)
    
    try:
        conn = connect_db()
        
        # Insert data in correct order (respecting foreign keys)
        insert_categories(conn)
        insert_suppliers(conn)
        insert_warehouses(conn)
        insert_products(conn)
        insert_customers(conn)
        insert_inventory(conn)
        insert_sales_orders(conn)
        insert_inventory_movements(conn)
        
        # Verify
        total = verify_data(conn)
        
        conn.close()
        
        print(f"\n✅ Database population complete!")
        print(f"📊 {total} total records added")
        print("\n🎯 Next step: run 'python ai_agent.py' to test queries")
        print("🌐 Or run 'streamlit run app.py' to start the web interface")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        return False

if __name__ == "__main__":
    main()