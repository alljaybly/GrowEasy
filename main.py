
import sqlite3
import os
import time
from datetime import datetime
import psutil

class GrowEasy:
    def __init__(self):
        """Initialize GrowEasy microfinance app"""
        self.db_name = 'groweasy.db'
        self.setup_database()
        print("✅ GrowEasy initialized successfully")
    
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
    
    def calculate_credit_score(self, savings, loans, income, expenses):
        """Calculate credit score using rule-based algorithm"""
        score = 50  # Base score
        
        # Savings ratio (higher is better)
        if income > 0:
            savings_ratio = savings / income
            score += min(30, savings_ratio * 100)
            debt_ratio = loans / income
            if debt_ratio > 2:  # Penalize >200% debt-to-income
                score -= 20
            score -= min(25, debt_ratio * 50)
        
        # Expense management (lower expenses relative to income is better)
        
            expense_ratio = expenses / income
            if expense_ratio < 0.5:
                score += 10
            elif expense_ratio > 0.8:
                score -= 15
        else:
            score -= 20
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
    
    def simulate_wifi_sync(self):
        """Simulate Wi-Fi synchronization with cloud server"""
        print("\n🔄 Starting Wi-Fi sync simulation...")
        time.sleep(1)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM transactions WHERE synced = 0')
        unsynced_count = cursor.fetchone()[0]
        
        if unsynced_count == 0:
            print("✅ All data is already synced")
            conn.close()
            return
        
        print(f"📤 Found {unsynced_count} unsynced transactions")
        for i in range(3):
            print(f"📡 Syncing... {((i+1)/3)*100:.0f}%")
            time.sleep(0.5)
        
        cursor.execute('UPDATE transactions SET synced = 1 WHERE synced = 0')
        conn.commit()
        conn.close()
        
        with open('sync_log.txt', 'a') as f:
            f.write(f"{datetime.now().isoformat()}: Synced {unsynced_count} transactions\n")
        
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
                self.simulate_wifi_sync()
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
            if savings < 0:
                print("❌ Savings cannot be negative")
                return                   
            loans = float(input("Outstanding Loans (R): "))
            if loans < 0:
                print("❌ Loans cannot be negative")
                return
            income = float(input("Monthly Income (R): "))
            if income < 0:
                print("❌ Income cannot be negative")
                return
            expenses = float(input("Monthly Expenses (R): "))
            if expenses < 0:
                print("❌ Expenses cannot be negative")
                return
            
            print("\n🤖 Calculating credit score...")
            time.sleep(1)  # Simulate processing
            
            credit_score = self.calculate_credit_score(savings, loans, income, expenses)
            
            if self.add_transaction(user_id, savings, loans, income, expenses):
                self.display_credit_result(credit_score, savings, loans, income, expenses)
                history = self.get_user_history(user_id)
                print(f"\n📋 Transaction History for {user_id}")
                print("-" * 60)
                print("Date\t\tSavings\tLoans\tIncome\tExpenses")
                print("-" * 60)
                for record in history:
                    savings, loans, income, expenses, timestamp = record
                    date = timestamp.split('T')[0]
                    print(f"{date}\tR{savings:.0f}\tR{loans:.0f}\tR{income:.0f}\tR{expenses:.0f}")
            
        except ValueError:
            print("❌ Please enter valid numbers")
    
    def display_credit_result(self, score, savings, loans, income, expenses):
        """Display credit score results"""
        print("\n" + "="*50)
        print("📊 CREDIT ASSESSMENT RESULTS")
        print("="*50)
        print(f"🎯 Credit Score: {score:.0f}/100")
        
        if score >= 80:
            print("🟢 Excellent - Low risk borrower")
            recommendation = "Approved for loans up to R{:.0f}".format(income * 3 if income > 0 else 1000)
        elif score >= 60:
            print("🟡 Good - Moderate risk borrower")
            recommendation = "Approved for loans up to R{:.0f}".format(income * 2 if income > 0 else 1000)
        elif score >= 40:
            print("🟠 Fair - Higher risk, consider smaller amounts")
            recommendation = "Approved for loans up to R{:.0f}".format(income * 1 if income > 0 else 1000)
        else:
            print("🔴 Poor - Focus on building savings first")
            recommendation = "Recommend savings program before loans"
        
        print(f"💡 Recommendation: {recommendation}")
        
        print("\n📈 Financial Summary:")
        print(f"💰 Savings: R{savings:,.2f}")
        print(f"💸 Loans: R{loans:,.2f}")
        debt_to_income = (loans / income * 100) if income > 0 else float('inf') if loans > 0 else 0
        print(f"📊 Debt-to-Income: {debt_to_income:.1f}%")
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
            date = timestamp.split('T')[0]
            print(f"{date}\tR{savings:.0f}\tR{loans:.0f}\tR{income:.0f}\tR{expenses:.0f}")
    
    def show_system_status(self):
        """Show system status and performance metrics"""
        print("\n💾 System Status")
        print("-" * 30)
        
        memory_mb = self.get_memory_usage()
        print(f"📱 Memory Usage: {memory_mb:.1f} MB")
        print(f"🎯 Target: <50 MB {'✅' if memory_mb < 50 else '⚠️'}")
        
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
        
        db_size = os.path.getsize(self.db_name) / 1024 if os.path.exists(self.db_name) else 0
        print(f"🗄️ Database Size: {db_size:.1f} KB")
        print("🤖 AI Model: Rule-based algorithm")

def main():
    """Main function to run GrowEasy application"""
    try:
        app = GrowEasy()
        app.run()
        print(app.get_user_history("1"))
    except KeyboardInterrupt:
        print("\n\n👋 GrowEasy closed by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")

if __name__ == "__main__":
    main()
