"""
database_setup.py
Creates the SQLite database and all necessary tables for the inventory & sales system.

HOW TO USE:
1. Save this file as 'database_setup.py' in your project folder
2. Run: python database_setup.py
3. This will create 'inventory_sales.db' file with all tables
"""

import sqlite3
import os

def create_database():
    """Creates SQLite database and all tables"""
    
    print("🔧 Creating database and tables...")
    
    # Connect to SQLite database (creates file if doesn't exist)
    conn = sqlite3.connect('inventory_sales.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create all tables
    tables = [
        # Categories table
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Suppliers table
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name VARCHAR(150) NOT NULL,
            contact_person VARCHAR(100),
            email VARCHAR(150),
            phone VARCHAR(20),
            address TEXT,
            city VARCHAR(100),
            country VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Products table
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name VARCHAR(200) NOT NULL,
            product_code VARCHAR(50) UNIQUE NOT NULL,
            category_id INTEGER,
            supplier_id INTEGER,
            description TEXT,
            unit_price DECIMAL(10, 2) NOT NULL,
            cost_price DECIMAL(10, 2) NOT NULL,
            weight DECIMAL(8, 3),
            dimensions VARCHAR(50),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        )
        """,
        
        # Warehouses table
        """
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_name VARCHAR(150) NOT NULL,
            location VARCHAR(200),
            capacity INTEGER,
            manager_name VARCHAR(100),
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Inventory table
        """
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            quantity_on_hand INTEGER NOT NULL DEFAULT 0,
            quantity_reserved INTEGER NOT NULL DEFAULT 0,
            reorder_level INTEGER DEFAULT 10,
            max_stock_level INTEGER DEFAULT 1000,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
            UNIQUE (product_id, warehouse_id)
        )
        """,
        
        # Customers table
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name VARCHAR(150) NOT NULL,
            customer_type VARCHAR(20) CHECK(customer_type IN ('Individual', 'Business')) NOT NULL,
            email VARCHAR(150),
            phone VARCHAR(20),
            address TEXT,
            city VARCHAR(100),
            country VARCHAR(100),
            credit_limit DECIMAL(15, 2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Sales Orders table
        """
        CREATE TABLE IF NOT EXISTS sales_orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number VARCHAR(50) UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            required_date DATE,
            shipped_date DATE,
            order_status VARCHAR(20) DEFAULT 'Pending',
            payment_status VARCHAR(20) DEFAULT 'Pending',
            subtotal DECIMAL(15, 2) NOT NULL DEFAULT 0,
            tax_amount DECIMAL(15, 2) NOT NULL DEFAULT 0,
            shipping_cost DECIMAL(10, 2) NOT NULL DEFAULT 0,
            total_amount DECIMAL(15, 2) NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        )
        """,
        
        # Sales Order Items table
        """
        CREATE TABLE IF NOT EXISTS sales_order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            discount_percentage DECIMAL(5, 2) DEFAULT 0,
            line_total DECIMAL(15, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES sales_orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        """,
        
        # Inventory Movements table (for tracking stock changes)
        """
        CREATE TABLE IF NOT EXISTS inventory_movements (
            movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            movement_type VARCHAR(20) NOT NULL, -- 'IN', 'OUT', 'TRANSFER', 'ADJUSTMENT'
            quantity INTEGER NOT NULL,
            reference_type VARCHAR(30), -- 'SALES_ORDER', 'PURCHASE_ORDER', 'ADJUSTMENT'
            reference_id INTEGER,
            movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        )
        """
    ]
    
    # Execute each table creation
    for i, table_sql in enumerate(tables, 1):
        try:
            cursor.execute(table_sql)
            print(f"✅ Created table {i}/9")
        except Exception as e:
            print(f"❌ Error creating table {i}: {e}")
            return False
    
    # Create indexes for better performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_sales_orders_customer ON sales_orders(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_sales_orders_date ON sales_orders(order_date)",
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("🎉 Database created successfully!")
    print("📁 File created: inventory_sales.db")
    return True

def verify_database():
    """Verify database was created correctly"""
    print("\n🔍 Verifying database...")
    
    try:
        conn = sqlite3.connect('inventory_sales.db')
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Inventory & Sales Database...")
    print("=" * 50)
    
    # Remove existing database for fresh start
    if os.path.exists('inventory_sales.db'):
        os.remove('inventory_sales.db')
        print("🗑️  Removed existing database")
    
    # Create new database
    if create_database():
        verify_database()
        print("\n✅ Setup complete! Next step: run 'python sample_data.py'")
    else:
        print("\n❌ Setup failed!")