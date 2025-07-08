
import sqlite3
import numpy as np
import json
import os
import time
from datetime import datetime
import psutil
import tflite_runtime.interpreter as tflite

class GrowEasy:
    def __init__(self):
        """Initialize GrowEasy microfinance app"""
        self.db_name = 'groweasy.db'
        self.model_path = 'credit_model.tflite'
        self.interpreter = None
        self.setup_database()
        self.setup_model()
        
    def setup_database(self):
        """Setup SQLite database for offline storage"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                savings REAL NOT NULL,
                loans REAL NOT NULL,
                income REAL NOT NULL,
                expenses REAL NOT NULL,
                timestamp TEXT NOT NULL,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT,
                group_name TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    def setup_model(self):
        """Setup TensorFlow Lite model for credit scoring"""
        if not os.path.exists(self.model_path):
            self.create_simple_model()
        
        try:
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            print("✅ TensorFlow Lite model loaded successfully")
        except Exception as e:
            print(f"⚠️ Model loading failed: {e}")
            self.interpreter = None
    
    def create_simple_model(self):
        """Create a simple TensorFlow Lite model for demonstration"""
        # This creates a basic model file for demonstration
        # In production, you'd train this on real financial data
        model_data = b'\x18\x00\x00\x00TFL3\x00\x00\x0e\x00\x18\x00\x04\x00\x08\x00\x0c\x00\x10\x00\x14\x00\x0e\x00\x00\x00'
        
        try:
            with open(self.model_path, 'wb') as f:
                # Create a minimal valid TFLite model structure
                f.write(model_data)
            print("✅ Demo model created")
        except Exception as e:
            print(f"⚠️ Could not create model: {e}")
    
    def calculate_credit_score(self, savings, loans, income, expenses):
        """Calculate credit score using AI model or fallback algorithm"""
        try:
            if self.interpreter:
                # Prepare input data
                input_data = np.array([[savings, loans, income, expenses]], dtype=np.float32)
                
                # Get input/output details
                input_details = self.interpreter.get_input_details()
                output_details = self.interpreter.get_output_details()
                
                # Set input tensor
                self.interpreter.set_tensor(input_details[0]['index'], input_data)
                
                # Run inference
                self.interpreter.invoke()
                
                # Get output
                output_data = self.interpreter.get_tensor(output_details[0]['index'])
                score = float(output_data[0]) * 100
                
                return max(0, min(100, score))
        except Exception as e:
            print(f"⚠️ AI model inference failed: {e}")
        
        # Fallback algorithm for credit scoring
        return self.fallback_credit_score(savings, loans, income, expenses)
    
    def fallback_credit_score(self, savings, loans, income, expenses):
        """Fallback credit scoring algorithm"""
        # Simple rule-based scoring
        score = 50  # Base score
        
        # Savings ratio (higher is better)
        if income > 0:
            savings_ratio = savings / income
            score += min(30, savings_ratio * 100)
        
        # Debt-to-income ratio (lower is better)
        if income > 0:
            debt_ratio = loans / income
            score -= min(25, debt_ratio * 50)
        
        # Expense management (lower expenses relative to income is better)
        if income > 0:
            expense_ratio = expenses / income
            if expense_ratio < 0.5:
                score += 10
            elif expense_ratio > 0.8:
                score -= 15
        
        # Absolute savings amount
        if savings > 1000:
            score += 10
        elif savings > 500:
            score += 5
        
        return max(0, min(100, score))
    
    def add_user(self, user_id, name, phone="", group_name=""):
        """Add new user to the system"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, name, phone, group_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, phone, group_name, datetime.now().isoformat()))
            
            conn.commit()
            print(f"✅ User {name} added successfully")
            return True
        except Exception as e:
            print(f"❌ Error adding user: {e}")
            return False
        finally:
            conn.close()
    
    def add_transaction(self, user_id, savings, loans, income, expenses):
        """Add new transaction to local database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO transactions (user_id, savings, loans, income, expenses, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, savings, loans, income, expenses, datetime.now().isoformat()))
            
            conn.commit()
            print("✅ Transaction saved locally")
            return True
        except Exception as e:
            print(f"❌ Error saving transaction: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_history(self, user_id):
        """Get transaction history for a user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT savings, loans, income, expenses, timestamp
            FROM transactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (user_id,))
        
        history = cursor.fetchall()
        conn.close()
        return history
    
    def sync_data(self):
        """Simulate Wi-Fi synchronization with cloud server"""
        print("\n🔄 Starting Wi-Fi sync simulation...")
        time.sleep(1)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Get unsynced transactions
        cursor.execute('SELECT COUNT(*) FROM transactions WHERE synced = 0')
        unsynced_count = cursor.fetchone()[0]
        
        if unsynced_count == 0:
            print("✅ All data is already synced")
            conn.close()
            return
        
        print(f"📤 Found {unsynced_count} unsynced transactions")
        
        # Simulate network delay
        for i in range(3):
            print(f"📡 Syncing... {((i+1)/3)*100:.0f}%")
            time.sleep(0.5)
        
        # Mark all as synced
        cursor.execute('UPDATE transactions SET synced = 1 WHERE synced = 0')
        conn.commit()
        conn.close()
        
        print("✅ Sync completed successfully!")
        print(f"📊 {unsynced_count} transactions uploaded to cloud")
    
    def get_memory_usage(self):
        """Get current memory usage for monitoring"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb
    
    def display_main_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("🌱 GROWEASY - Microfinance Credit Assistant")
        print("="*50)
        print("1. 👤 Add New User")
        print("2. 💰 Record Transaction & Get Credit Score")
        print("3. 📊 View User History")
        print("4. 🔄 Sync Data (Wi-Fi)")
        print("5. 💾 System Status")
        print("6. ❌ Exit")
        print("="*50)
    
    def run(self):
        """Main application loop"""
        print("🌱 Welcome to GrowEasy - Offline Microfinance Assistant")
        print("💡 Designed for low-resource environments")
        print(f"📱 Memory usage: {self.get_memory_usage():.1f} MB")
        
        while True:
            self.display_main_menu()
            choice = input("\n👉 Enter your choice (1-6): ").strip()
            
            if choice == '1':
                self.handle_add_user()
            elif choice == '2':
                self.handle_transaction()
            elif choice == '3':
                self.handle_view_history()
            elif choice == '4':
                self.sync_data()
            elif choice == '5':
                self.show_system_status()
            elif choice == '6':
                print("\n👋 Thank you for using GrowEasy!")
                print("💚 Empowering financial inclusion in rural communities")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def handle_add_user(self):
        """Handle adding a new user"""
        print("\n📝 Add New User")
        print("-" * 20)
        
        user_id = input("User ID: ").strip()
        if not user_id:
            print("❌ User ID cannot be empty")
            return
        
        name = input("Full Name: ").strip()
        if not name:
            print("❌ Name cannot be empty")
            return
        
        phone = input("Phone Number (optional): ").strip()
        group_name = input("Savings Group Name (optional): ").strip()
        
        self.add_user(user_id, name, phone, group_name)
    
    def handle_transaction(self):
        """Handle transaction recording and credit scoring"""
        print("\n💰 Record Transaction & Credit Assessment")
        print("-" * 40)
        
        user_id = input("User ID: ").strip()
        if not user_id:
            print("❌ User ID cannot be empty")
            return
        
        try:
            print("\n💵 Enter financial information:")
            savings = float(input("Current Savings (R): "))
            loans = float(input("Outstanding Loans (R): "))
            income = float(input("Monthly Income (R): "))
            expenses = float(input("Monthly Expenses (R): "))
            
            # Calculate credit score
            print("\n🤖 Calculating credit score...")
            time.sleep(1)  # Simulate processing
            
            credit_score = self.calculate_credit_score(savings, loans, income, expenses)
            
            # Save transaction
            if self.add_transaction(user_id, savings, loans, income, expenses):
                self.display_credit_result(credit_score, savings, loans, income, expenses)
            
        except ValueError:
            print("❌ Please enter valid numbers")
    
    def display_credit_result(self, score, savings, loans, income, expenses):
        """Display credit score results"""
        print("\n" + "="*50)
        print("📊 CREDIT ASSESSMENT RESULTS")
        print("="*50)
        print(f"🎯 Credit Score: {score:.0f}/100")
        
        # Score interpretation
        if score >= 80:
            print("🟢 Excellent - Low risk borrower")
            recommendation = "Approved for loans up to R{:.0f}".format(income * 3)
        elif score >= 60:
            print("🟡 Good - Moderate risk borrower")
            recommendation = "Approved for loans up to R{:.0f}".format(income * 2)
        elif score >= 40:
            print("🟠 Fair - Higher risk, consider smaller amounts")
            recommendation = "Approved for loans up to R{:.0f}".format(income * 1)
        else:
            print("🔴 Poor - Focus on building savings first")
            recommendation = "Recommend savings program before loans"
        
        print(f"💡 Recommendation: {recommendation}")
        
        # Financial summary
        print("\n📈 Financial Summary:")
        print(f"💰 Savings: R{savings:,.2f}")
        print(f"💸 Loans: R{loans:,.2f}")
        print(f"📊 Debt-to-Income: {(loans/income*100) if income > 0 else 0:.1f}%")
        print(f"💾 Memory Usage: {self.get_memory_usage():.1f} MB")
        print("="*50)
    
    def handle_view_history(self):
        """Handle viewing user transaction history"""
        print("\n📊 View User History")
        print("-" * 20)
        
        user_id = input("User ID: ").strip()
        if not user_id:
            print("❌ User ID cannot be empty")
            return
        
        history = self.get_user_history(user_id)
        
        if not history:
            print(f"📭 No transaction history found for user {user_id}")
            return
        
        print(f"\n📋 Transaction History for {user_id}")
        print("-" * 60)
        print("Date\t\tSavings\tLoans\tIncome\tExpenses")
        print("-" * 60)
        
        for record in history:
            savings, loans, income, expenses, timestamp = record
            date = timestamp.split('T')[0]  # Extract date part
            print(f"{date}\tR{savings:.0f}\tR{loans:.0f}\tR{income:.0f}\tR{expenses:.0f}")
    
    def show_system_status(self):
        """Show system status and performance metrics"""
        print("\n💾 System Status")
        print("-" * 30)
        
        memory_mb = self.get_memory_usage()
        print(f"📱 Memory Usage: {memory_mb:.1f} MB")
        print(f"🎯 Target: <50 MB {'✅' if memory_mb < 50 else '⚠️'}")
        
        # Database stats
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM transactions')
        transaction_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM transactions WHERE synced = 0')
        unsynced_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"👥 Users: {user_count}")
        print(f"💳 Transactions: {transaction_count}")
        print(f"📤 Unsynced: {unsynced_count}")
        
        # File sizes
        db_size = os.path.getsize(self.db_name) / 1024 if os.path.exists(self.db_name) else 0
        print(f"🗄️ Database Size: {db_size:.1f} KB")
        
        print(f"🤖 AI Model: {'✅ Loaded' if self.interpreter else '❌ Fallback mode'}")

def main():
    """Main function to run GrowEasy application"""
    try:
        app = GrowEasy()
        print(f"App memory usage: {app.get_memory_usage():.1f} MB")
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 GrowEasy closed by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")

if __name__ == "__main__":
    main()
