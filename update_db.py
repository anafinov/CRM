from app import create_app, db
from app.models import Customer
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Add new columns to Customer table
    with db.engine.connect() as conn:
        # Check if columns exist
        columns = conn.execute(text("PRAGMA table_info(customer)")).fetchall()
        column_names = [col[1] for col in columns]
        
        # Add new columns if they don't exist
        if 'category' not in column_names:
            conn.execute(text("ALTER TABLE customer ADD COLUMN category VARCHAR(20) DEFAULT 'potential'"))
            print("Added category column")
        
        if 'address' not in column_names:
            conn.execute(text("ALTER TABLE customer ADD COLUMN address VARCHAR(200)"))
            print("Added address column")
            
        if 'website' not in column_names:
            conn.execute(text("ALTER TABLE customer ADD COLUMN website VARCHAR(100)"))
            print("Added website column")
            
        if 'source' not in column_names:
            conn.execute(text("ALTER TABLE customer ADD COLUMN source VARCHAR(50)"))
            print("Added source column")
            
        if 'last_contact' not in column_names:
            conn.execute(text("ALTER TABLE customer ADD COLUMN last_contact DATETIME"))
            print("Added last_contact column")
            
        if 'next_follow_up' not in column_names:
            conn.execute(text("ALTER TABLE customer ADD COLUMN next_follow_up DATETIME"))
            print("Added next_follow_up column")
            
        if 'description' not in column_names:
            conn.execute(text("ALTER TABLE customer ADD COLUMN description TEXT"))
            print("Added description column")
            
        if 'tags' not in column_names:
            conn.execute(text("ALTER TABLE customer ADD COLUMN tags VARCHAR(200)"))
            print("Added tags column")

        # Check for Deal table expected_close_date, description, and probability columns
        deal_columns = conn.execute(text("PRAGMA table_info(deal)")).fetchall()
        deal_column_names = [col[1] for col in deal_columns]
        
        if 'expected_close_date' not in deal_column_names:
            conn.execute(text("ALTER TABLE deal ADD COLUMN expected_close_date DATETIME"))
            print("Added expected_close_date column to Deal table")
            
        if 'description' not in deal_column_names:
            conn.execute(text("ALTER TABLE deal ADD COLUMN description TEXT"))
            print("Added description column to Deal table")
            
        if 'probability' not in deal_column_names:
            conn.execute(text("ALTER TABLE deal ADD COLUMN probability INTEGER DEFAULT 50"))
            print("Added probability column to Deal table")
        
        # Commit the changes
        conn.commit()
    
    print("Database schema updated successfully.") 