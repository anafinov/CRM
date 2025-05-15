from app import create_app, db
from app.models import User, Customer, Note, Deal

app = create_app()

with app.app_context():
    # Create all database tables
    db.create_all()
    print("Database tables created successfully!") 