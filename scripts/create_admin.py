import argparse
import sys
import os

# Add src to path so we can import shared modules
sys.path.append(os.getcwd())

from sqlmodel import Session, select, create_engine
from src.shared.models.auth import AdminUser
from src.shared.utils.auth import get_password_hash

# Use the same DB as the Auth Service (make sure this matches docker-compose or env)
# For local script execution, we might need to point to the file or postgres instance.
# If using Postgres in Docker, this script needs to run INSIDE the container or have port access.
# If using SQLite locally (dev), it works directly.

def create_admin(username, password, db_url=None):
    if not db_url:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            # Fallback to local sqlite if not specified
             db_url = "sqlite:///database.db"
    
    print(f"Connecting to database: {db_url}")
    engine = create_engine(db_url)
    
    with Session(engine) as session:
        # Check if exists
        existing_user = session.exec(select(AdminUser).where(AdminUser.username == username)).first()
        if existing_user:
            print(f"User '{username}' already exists. Updating password...")
            existing_user.hashed_password = get_password_hash(password)
            session.add(existing_user)
        else:
            print(f"Creating new user '{username}'...")
            new_user = AdminUser(username=username, hashed_password=get_password_hash(password))
            session.add(new_user)
        
        session.commit()
        print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an Admin User")
    parser.add_argument("--user", required=True, help="Username")
    parser.add_argument("--pass", dest="password", required=True, help="Password")
    parser.add_argument("--db", help="Database URL (optional)")
    
    args = parser.parse_args()
    create_admin(args.user, args.password, args.db)
