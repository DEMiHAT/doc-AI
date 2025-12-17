import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.config import engine, init_db, drop_db
from app.models.database_models import Base


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")


def check_database_url():
    """Check if DATABASE_URL is set"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print_error("DATABASE_URL not found in environment")
        print_info("Please create a .env file with DATABASE_URL")
        print_info("Example: DATABASE_URL=postgresql://docai_user:docai_pass@localhost:5432/docai_db")
        return False

    # Hide password in display
    try:
        safe_url = db_url.split('@')[0].split(':')[:-1]
        safe_url = ':'.join(safe_url) + ':***@' + db_url.split('@')[1]
        print_info(f"Database URL: {safe_url}")
    except:
        print_info("Database URL found (cannot parse)")

    return True


def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print_success("Database connection successful!")
            print_info(f"PostgreSQL version: {version.split(',')[0]}")
            return True
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        print("\nPossible solutions:")
        print("1. Make sure PostgreSQL is running")
        print("   Docker: docker-compose up -d postgres")
        print("   macOS: brew services start postgresql@15")
        print("   Linux: sudo systemctl start postgresql")
        print("\n2. Check your DATABASE_URL in .env file")
        print("\n3. Verify database exists:")
        print("   psql -U postgres -c 'CREATE DATABASE docai_db;'")
        return False


def create_tables():
    """Create all database tables"""
    try:
        print_info("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if tables:
            print_success(f"Created {len(tables)} tables:")
            for table in tables:
                print(f"   • {table}")
        else:
            print_warning("No tables were created")
            return False

        return True

    except Exception as e:
        print_error(f"Failed to create tables: {str(e)}")
        return False


def drop_tables():
    """Drop all database tables"""
    try:
        print_warning("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print_success("All tables dropped")
        return True
    except Exception as e:
        print_error(f"Failed to drop tables: {str(e)}")
        return False


def show_table_info():
    """Show information about existing tables"""
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            print_info("No tables found in database")
            return

        print_info(f"Found {len(tables)} tables:")

        for table in tables:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]

            columns = inspector.get_columns(table)
            print(f"\n📋 {table} ({count} rows)")
            print(f"   Columns: {len(columns)}")
            for col in columns[:5]:  # Show first 5 columns
                print(f"   • {col['name']}: {col['type']}")
            if len(columns) > 5:
                print(f"   ... and {len(columns) - 5} more")

    except Exception as e:
        print_error(f"Error reading table info: {str(e)}")


def insert_sample_data():
    """Insert sample data for testing"""
    try:
        from sqlalchemy.orm import sessionmaker
        from app.models.database_models import Document, Extraction, LineItem
        from datetime import datetime

        Session = sessionmaker(bind=engine)
        session = Session()

        print_info("Creating sample document...")

        # Create sample document
        sample_doc = Document(
            file_id="sample_001",
            filename="sample_invoice.pdf",
            file_type="application/pdf",
            file_size=1024000,
            status="completed",
            document_type="invoice",
            classification_confidence=0.95,
            ocr_text="Sample invoice text...",
            ocr_completed_at=datetime.utcnow()
        )
        session.add(sample_doc)
        session.flush()

        # Create sample extraction
        sample_extraction = Extraction(
            document_id=sample_doc.id,
            invoice_number="INV-001",
            invoice_date="2024-01-15",
            vendor_name="Sample Vendor Inc.",
            customer_name="Sample Customer LLC",
            subtotal_amount=1000.00,
            tax_amount=100.00,
            total_amount=1100.00,
            currency="USD",
            summary="Sample invoice for testing purposes"
        )
        session.add(sample_extraction)

        # Create sample line items
        line_items = [
            LineItem(
                document_id=sample_doc.id,
                description="Product A",
                quantity=10,
                unit_price=50.00,
                total_price=500.00,
                line_number=1
            ),
            LineItem(
                document_id=sample_doc.id,
                description="Product B",
                quantity=5,
                unit_price=100.00,
                total_price=500.00,
                line_number=2
            )
        ]

        for item in line_items:
            session.add(item)

        session.commit()
        print_success("Sample data inserted successfully")
        print_info("Sample file_id: sample_001")
        session.close()

        return True

    except Exception as e:
        print_error(f"Failed to insert sample data: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False


def main():
    """Main setup function"""
    print_header("🗄️  DocAI Database Setup")

    # Check DATABASE_URL
    if not check_database_url():
        sys.exit(1)

    # Test connection
    print("\n📡 Testing database connection...")
    if not test_connection():
        sys.exit(1)

    # Show current tables
    print("\n📊 Current database state:")
    show_table_info()

    # Menu
    print("\n" + "=" * 60)
    print("What would you like to do?")
    print("=" * 60)
    print("\n1. Create tables (fresh installation)")
    print("2. Drop and recreate tables (⚠️  DELETES ALL DATA)")
    print("3. Show table information")
    print("4. Insert sample data")
    print("5. Exit")

    choice = input("\nChoice (1-5): ").strip()

    if choice == "1":
        print_header("Creating Tables")
        if create_tables():
            print_success("Database setup complete!")

            # Ask about sample data
            add_sample = input("\nWould you like to add sample data? (y/n): ").strip().lower()
            if add_sample == 'y':
                insert_sample_data()

            print("\n" + "=" * 60)
            print("✅ Setup Complete!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Start backend:  uvicorn main:app --reload")
            print("2. Start frontend: cd frontend && npm run dev")
            print("3. Visit: http://localhost:5173")
            print("\nTo check database:")
            print("   psql -U docai_user -d docai_db")
            print("\nTo view tables:")
            print("   python setup_database.py  (choose option 3)")
            print()
        else:
            sys.exit(1)

    elif choice == "2":
        print_header("Drop and Recreate Tables")
        print_warning("⚠️  THIS WILL DELETE ALL DATA!")
        confirm = input("\nType 'YES' to confirm: ").strip()

        if confirm == "YES":
            if drop_tables():
                print()
                if create_tables():
                    print_success("Database reset complete!")

                    # Ask about sample data
                    add_sample = input("\nWould you like to add sample data? (y/n): ").strip().lower()
                    if add_sample == 'y':
                        insert_sample_data()
                else:
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            print_info("Operation cancelled")

    elif choice == "3":
        print_header("Table Information")
        show_table_info()
        print()

    elif choice == "4":
        print_header("Insert Sample Data")
        insert_sample_data()
        print()
        show_table_info()
        print()

    elif choice == "5":
        print_info("Exiting without changes")
        print()

    else:
        print_error("Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)