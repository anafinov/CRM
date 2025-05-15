from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, SubmitField, DateField, URLField
from wtforms.validators import DataRequired, Email, Optional, URL

class CustomerForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Optional()])
    company = StringField('Компания', validators=[Optional()])
    website = URLField('Веб-сайт', validators=[Optional(), URL()])
    address = StringField('Адрес', validators=[Optional()])
    source = StringField('Источник', validators=[Optional()])
    tags = StringField('Теги (через запятую)', validators=[Optional()])
    next_follow_up = DateField('Следующий контакт', validators=[Optional()], format='%Y-%m-%d')
    description = TextAreaField('Дополнительная информация', validators=[Optional()])
    category = SelectField('Категория', choices=[
        ('potential', 'Потенциальный'),
        ('active', 'Активный'),
        ('vip', 'VIP'),
        ('inactive', 'Неактивный')
    ], validators=[Optional()])
    submit = SubmitField('Сохранить')

class CustomerSearchForm(FlaskForm):
    search = StringField('Поиск по имени, email или компании')
    company = StringField('Компания')
    date_from = DateField('Дата от', validators=[Optional()], format='%Y-%m-%d')
    date_to = DateField('Дата до', validators=[Optional()], format='%Y-%m-%d')
    has_deals = SelectField('Наличие сделок', choices=[
        ('', 'Все клиенты'),
        ('yes', 'С активными сделками'),
        ('no', 'Без сделок')
    ], validators=[Optional()])
    submit = SubmitField('Применить')

class DealForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    amount = FloatField('Сумма', validators=[Optional()])
    status = SelectField('Статус', choices=[
        ('new', 'Новая'),
        ('negotiation', 'В переговорах'),
        ('won', 'Выиграна'),
        ('lost', 'Проиграна')
    ])
    submit = SubmitField('Сохранить')

class NoteForm(FlaskForm):
    content = TextAreaField('Заметка', validators=[DataRequired()])
    submit = SubmitField('Добавить')

class CustomerCategoryForm(FlaskForm):
    category = SelectField('Категория', choices=[
        ('potential', 'Потенциальный'),
        ('active', 'Активный'),
        ('vip', 'VIP'),
        ('inactive', 'Неактивный')
    ])
    submit = SubmitField('Обновить категорию') 