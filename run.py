from app import create_app, db
from app.models import User, Customer, Note, Deal

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Customer': Customer,
        'Note': Note,
        'Deal': Deal
    }

if __name__ == '__main__':
    app.run(debug=True) 