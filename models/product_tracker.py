import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import os

class ProductTracker:
    def __init__(self, db_path="product_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create shopkeepers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopkeepers (
                user_id TEXT PRIMARY KEY,
                shop_name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                sku TEXT NOT NULL,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                initial_quantity INTEGER NOT NULL,
                current_quantity INTEGER NOT NULL,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES shopkeepers (user_id),
                UNIQUE(user_id, sku)
            )
        ''')
        
        # Create sale_events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL, -- 'sale', 'restock', 'adjustment'
                quantity_changed INTEGER NOT NULL, -- positive for restock, negative for sale
                price_per_unit REAL,
                total_amount REAL,
                remaining_quantity INTEGER NOT NULL,
                event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                FOREIGN KEY (user_id) REFERENCES shopkeepers (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_shopkeeper(self, user_id: str, shop_name: str, password: str, email: str, 
                          phone: str, location: str) -> bool:
        """Register a new shopkeeper"""
        try:
            # Validate required fields
            if not email:
                print("Error: Email is required")
                return False
            
            if not phone:
                print("Error: Phone is required")
                return False
                
            if not location:
                print("Error: Location is required")
                return False
            
            # Validate email format (must be Gmail)
            if not email.endswith('@gmail.com') or '@' not in email:
                print("Error: Email must be a valid Gmail address")
                return False
            
            # Validate phone format (digits only)
            if not phone.isdigit() or len(phone) < 10 or len(phone) > 15:
                print("Error: Phone must contain only digits (10-15 digits)")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add password column if it doesn't exist
            cursor.execute("PRAGMA table_info(shopkeepers)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'password' not in columns:
                cursor.execute('ALTER TABLE shopkeepers ADD COLUMN password TEXT')
            
            cursor.execute('''
                INSERT OR REPLACE INTO shopkeepers (user_id, shop_name, password, email, phone, location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, shop_name, password, email, phone, location))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error registering shopkeeper: {e}")
            return False
    
    def authenticate_shopkeeper(self, user_id: str, password: str) -> Dict:
        """Authenticate a shopkeeper"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add password column if it doesn't exist
            cursor.execute("PRAGMA table_info(shopkeepers)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'password' not in columns:
                cursor.execute('ALTER TABLE shopkeepers ADD COLUMN password TEXT')
                # Set default password for existing demo user
                cursor.execute('UPDATE shopkeepers SET password = ? WHERE user_id = ?', 
                             ('demo123', 'demo_shopkeeper_001'))
            
            cursor.execute('''
                SELECT user_id, shop_name, email, phone, location 
                FROM shopkeepers 
                WHERE user_id = ? AND password = ?
            ''', (user_id, password))
            
            shopkeeper = cursor.fetchone()
            conn.close()
            
            if shopkeeper:
                return {
                    "success": True,
                    "user_id": shopkeeper[0],
                    "shop_name": shopkeeper[1],
                    "email": shopkeeper[2],
                    "phone": shopkeeper[3],
                    "location": shopkeeper[4]
                }
            else:
                return {"success": False, "error": "Invalid credentials"}
                
        except Exception as e:
            print(f"Error authenticating shopkeeper: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    def add_product(self, user_id: str, sku: str, product_name: str, category: str, 
                   initial_quantity: int) -> Dict:
        """Add a new product to shopkeeper's inventory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if product already exists for this shopkeeper
            cursor.execute('''
                SELECT product_id FROM products WHERE user_id = ? AND sku = ?
            ''', (user_id, sku))
            
            existing = cursor.fetchone()
            if existing:
                return {"success": False, "error": "Product with this SKU already exists"}
            
            # Add the product with explicit date
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO products (user_id, sku, product_name, category, initial_quantity, current_quantity, date_added)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, sku, product_name, category, initial_quantity, initial_quantity, current_date))
            
            product_id = cursor.lastrowid
            
            # Record the initial stock event with explicit date
            cursor.execute('''
                INSERT INTO sale_events (product_id, user_id, event_type, quantity_changed, 
                                       remaining_quantity, notes, event_date)
                VALUES (?, ?, 'initial_stock', ?, ?, 'Initial product submission', ?)
            ''', (product_id, user_id, initial_quantity, initial_quantity, current_date))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "product_id": product_id,
                "message": "Product added successfully"
            }
        except Exception as e:
            print(f"Error adding product: {e}")
            return {"success": False, "error": str(e)}
    
    def record_sale_event(self, user_id: str, sku: str, event_type: str, 
                         quantity_changed: int, price_per_unit: float = None,
                         notes: str = None) -> Dict:
        """Record a sale, restock, or adjustment event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the product
            cursor.execute('''
                SELECT product_id, current_quantity FROM products 
                WHERE user_id = ? AND sku = ?
            ''', (user_id, sku))
            
            product = cursor.fetchone()
            if not product:
                return {"success": False, "error": "Product not found"}
            
            product_id, current_quantity = product
            
            # Calculate new quantity
            new_quantity = current_quantity + quantity_changed
            if new_quantity < 0:
                return {"success": False, "error": "Insufficient stock"}
            
            # Calculate total amount
            total_amount = None
            if price_per_unit:
                total_amount = abs(quantity_changed) * price_per_unit
            
            # Record the event
            cursor.execute('''
                INSERT INTO sale_events (product_id, user_id, event_type, quantity_changed,
                                       price_per_unit, total_amount, remaining_quantity, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (product_id, user_id, event_type, quantity_changed, price_per_unit, 
                  total_amount, new_quantity, notes))
            
            # Update product quantity
            cursor.execute('''
                UPDATE products SET current_quantity = ? WHERE product_id = ?
            ''', (new_quantity, product_id))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "new_quantity": new_quantity,
                "message": f"{event_type} recorded successfully"
            }
        except Exception as e:
            print(f"Error recording sale event: {e}")
            return {"success": False, "error": str(e)}
    
    def get_shopkeeper_products(self, user_id: str) -> List[Dict]:
        """Get all products for a shopkeeper"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT product_id, sku, product_name, category, initial_quantity, 
                       current_quantity, date_added
                FROM products 
                WHERE user_id = ?
                ORDER BY date_added DESC
            ''', (user_id,))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    "product_id": row[0],
                    "sku": row[1],
                    "product_name": row[2],
                    "category": row[3],
                    "initial_quantity": row[4],
                    "current_quantity": row[5],
                    "date_added": row[6]
                })
            
            conn.close()
            return products
        except Exception as e:
            print(f"Error getting shopkeeper products: {e}")
            return []
    
    def get_product_history(self, user_id: str, sku: str = None, 
                          start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get sale/update history for products"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT p.sku, p.product_name, p.category, se.event_type, se.quantity_changed,
                       se.price_per_unit, se.total_amount, se.remaining_quantity, se.event_date, se.notes
                FROM sale_events se
                JOIN products p ON se.product_id = p.product_id
                WHERE se.user_id = ?
            '''
            params = [user_id]
            
            if sku:
                query += " AND p.sku = ?"
                params.append(sku)
            
            if start_date:
                query += " AND se.event_date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND se.event_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY se.event_date DESC"
            
            cursor.execute(query, params)
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "sku": row[0],
                    "product_name": row[1],
                    "category": row[2],
                    "event_type": row[3],
                    "quantity_changed": row[4],
                    "price_per_unit": row[5],
                    "total_amount": row[6],
                    "remaining_quantity": row[7],
                    "event_date": row[8],
                    "notes": row[9]
                })
            
            conn.close()
            return history
        except Exception as e:
            print(f"Error getting product history: {e}")
            return []
    
    def export_history_csv(self, user_id: str, sku: str = None, 
                          start_date: str = None, end_date: str = None) -> str:
        """Export product history to CSV"""
        try:
            history = self.get_product_history(user_id, sku, start_date, end_date)
            
            if not history:
                return None
            
            df = pd.DataFrame(history)
            
            # Create exports directory if it doesn't exist
            os.makedirs("exports", exist_ok=True)
            
            filename = f"exports/product_history_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            
            return filename
        except Exception as e:
            print(f"Error exporting history: {e}")
            return None
    
    def get_shopkeeper_stats(self, user_id: str) -> Dict:
        """Get summary statistics for a shopkeeper"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total products
            cursor.execute('''
                SELECT COUNT(*) FROM products WHERE user_id = ?
            ''', (user_id,))
            total_products = cursor.fetchone()[0]
            
            # Total sales value
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM sale_events 
                WHERE user_id = ? AND event_type = 'sale' AND total_amount IS NOT NULL
            ''', (user_id,))
            total_sales_value = cursor.fetchone()[0]
            
            # Total items sold
            cursor.execute('''
                SELECT COALESCE(SUM(ABS(quantity_changed)), 0) 
                FROM sale_events 
                WHERE user_id = ? AND event_type = 'sale'
            ''', (user_id,))
            total_items_sold = cursor.fetchone()[0]
            
            # Current inventory value (estimate)
            cursor.execute('''
                SELECT COALESCE(SUM(current_quantity), 0) 
                FROM products 
                WHERE user_id = ?
            ''', (user_id,))
            current_inventory_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_products": total_products,
                "total_sales_value": total_sales_value,
                "total_items_sold": total_items_sold,
                "current_inventory_count": current_inventory_count
            }
        except Exception as e:
            print(f"Error getting shopkeeper stats: {e}")
            return {} 