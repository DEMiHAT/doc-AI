# backend/check_postgres.py

"""
PostgreSQL Connection Diagnostic Tool
Run this to check if your PostgreSQL setup is working correctly
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step, text):
    print(f"\n{step}. {text}")


def print_success(text):
    print(f"   ✅ {text}")


def print_error(text):
    print(f"   ❌ {text}")


def print_info(text):
    print(f"   ℹ️  {text}")


def check_environment():
    """Check if DATABASE_URL is set"""
    print_step(1, "Checking Environment Variables")

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # Hide password in output
        safe_url = db_url.split('@')[0].split(':')[:-1]
        safe_url = ':'.join(safe_url) + ':***@' + db_url.split('@')[1]
        print_success(f"DATABASE_URL found")
        print_info(f"URL: {safe_url}")
        return db_url
    else:
        print_error("DATABASE_URL not found in environment")
        print_info("Please create a .env file with DATABASE_URL")
        print_info("Example: DATABASE_URL=postgresql://docai_user:docai_pass@localhost:5432/docai_db")
        return None


def check_packages():
    """Check if required packages are installed"""
    print_step(2, "Checking Python Packages")

    packages = {
        'sqlalchemy': 'SQLAlchemy',
        'psycopg2': 'psycopg2-binary',
        'dotenv': 'python-dotenv'
    }

    missing = []
    for module, package in packages.items():
        try:
            __import__(module)
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            missing.append(package)

    if missing:
        print_info(f"Install missing packages: pip install {' '.join(missing)}")
        return False
    return True


def check_connection(db_url):
    """Try to connect to PostgreSQL"""
    print_step(3, "Testing PostgreSQL Connection")

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(db_url)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print_success("Connected successfully!")
            print_info(f"PostgreSQL version: {version.split(',')[0]}")
            return engine

    except ImportError:
        print_error("SQLAlchemy not installed")
        print_info("Run: pip install sqlalchemy psycopg2-binary")
        return None

    except Exception as e:
        print_error(f"Connection failed: {str(e)}")

        if "could not connect" in str(e).lower():
            print_info("PostgreSQL might not be running")
            print_info("Docker: docker-compose up -d postgres")
            print_info("macOS: brew services start postgresql@15")
            print_info("Linux: sudo systemctl start postgresql")

        elif "password authentication failed" in str(e).lower():
            print_info("Check your database credentials")
            print_info("Docker default: docai_user / docai_pass")

        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            print_info("Database does not exist")
            print_info("Create it with: python setup_database.py")

        return None


def check_tables(engine):
    """Check if tables exist"""
    print_step(4, "Checking Database Tables")

    try:
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = ['documents', 'extractions', 'line_items', 'processing_logs']

        if not tables:
            print_error("No tables found")
            print_info("Run: python setup_database.py")
            return False

        for table in expected_tables:
            if table in tables:
                # Count rows
                from sqlalchemy import text
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                print_success(f"Table '{table}' exists ({count} rows)")
            else:
                print_error(f"Table '{table}' missing")

        missing = [t for t in expected_tables if t not in tables]
        if missing:
            print_info("Run: python setup_database.py")
            return False

        return True

    except Exception as e:
        print_error(f"Error checking tables: {str(e)}")
        return False


def check_docker():
    """Check if Docker PostgreSQL is running"""
    print_step("Extra", "Checking Docker Status (if applicable)")

    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=docai_postgres'],
            capture_output=True,
            text=True
        )

        if 'docai_postgres' in result.stdout:
            print_success("Docker container 'docai_postgres' is running")
            return True
        else:
            print_info("Docker container not found")
            print_info("Start it with: docker-compose up -d postgres")
            return False

    except FileNotFoundError:
        print_info("Docker not installed or not in PATH")
        return False
    except Exception as e:
        print_info(f"Could not check Docker status: {e}")
        return False


def test_crud_operations(engine):
    """Test basic CRUD operations"""
    print_step(5, "Testing CRUD Operations")

    try:
        from app.models.database_models import Document
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime

        Session = sessionmaker(bind=engine)
        session = Session()

        # Create
        test_doc = Document(
            file_id="test_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
            filename="test_document.pdf",
            file_type="application/pdf",
            status="test"
        )
        session.add(test_doc)
        session.commit()
        print_success("Create operation successful")

        # Read
        found = session.query(Document).filter_by(file_id=test_doc.file_id).first()
        if found:
            print_success("Read operation successful")

        # Delete
        session.delete(found)
        session.commit()
        print_success("Delete operation successful")

        session.close()
        return True

    except Exception as e:
        print_error(f"CRUD test failed: {str(e)}")
        return False


def main():
    print_header("PostgreSQL Setup Diagnostic Tool")
    print_info("This tool will check your PostgreSQL setup")

    # Check environment
    db_url = check_environment()
    if not db_url:
        sys.exit(1)

    # Check packages
    if not check_packages():
        sys.exit(1)

    # Check Docker (optional)
    check_docker()

    # Test connection
    engine = check_connection(db_url)
    if not engine:
        sys.exit(1)

    # Check tables
    tables_ok = check_tables(engine)

    # Test CRUD
    if tables_ok:
        test_crud_operations(engine)

    # Summary
    print_header("Diagnostic Complete")

    if tables_ok:
        print_success("All checks passed! Your PostgreSQL setup is ready.")
        print_info("You can now start the backend: uvicorn main:app --reload")
    else:
        print_error("Some checks failed. Please fix the issues above.")
        print_info("Most likely you need to run: python setup_database.py")

    print()


if __name__ == "__main__":
    main()