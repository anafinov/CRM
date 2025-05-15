from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    customers = db.relationship('Customer', backref='user', lazy='dynamic')
    notes = db.relationship('Note', backref='user', lazy='dynamic')
    deals = db.relationship('Deal', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.relationship('Note', backref='customer', lazy='dynamic')
    deals = db.relationship('Deal', backref='customer', lazy='dynamic')
    
    # Новые поля для расширенной информации о клиенте
    category = db.Column(db.String(20), default='potential')  # potential, active, vip, inactive
    address = db.Column(db.String(200))
    website = db.Column(db.String(100))
    source = db.Column(db.String(50))  # откуда пришел клиент
    last_contact = db.Column(db.DateTime)  # дата последнего контакта
    next_follow_up = db.Column(db.DateTime)  # дата следующего контакта
    description = db.Column(db.Text)  # дополнительная информация
    tags = db.Column(db.String(200))  # теги через запятую
    
    @property
    def total_deal_amount(self):
        """Возвращает общую сумму сделок клиента"""
        return sum(deal.amount or 0 for deal in self.deals)
    
    @property
    def active_deals_count(self):
        """Возвращает количество активных сделок"""
        return self.deals.filter(Deal.status.in_(['new', 'negotiation'])).count()

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='new')  # new, negotiation, won, lost
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Новые поля для расширенной информации о сделке
    expected_close_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    probability = db.Column(db.Integer, default=50)  # вероятность закрытия в %

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 