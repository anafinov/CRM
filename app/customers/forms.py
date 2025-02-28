from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

class CustomerForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Optional()])
    company = StringField('Компания', validators=[Optional()])
    submit = SubmitField('Сохранить')

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