from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.customers import bp
from app.customers.forms import CustomerForm, DealForm, NoteForm
from app.models import Customer, Deal, Note

@bp.route('/customers')
@login_required
def list():
    customers = Customer.query.filter_by(user_id=current_user.id).order_by(Customer.created_at.desc()).all()
    return render_template('customers/list.html', title='Клиенты', customers=customers)

@bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            company=form.company.data,
            user_id=current_user.id
        )
        db.session.add(customer)
        db.session.commit()
        flash('Клиент успешно добавлен')
        return redirect(url_for('customers.list'))
    return render_template('customers/edit.html', title='Новый клиент', form=form)

@bp.route('/customers/<int:id>')
@login_required
def customer(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    note_form = NoteForm()
    deal_form = DealForm()
    return render_template('customers/detail.html', title=customer.name,
                         customer=customer, note_form=note_form, deal_form=deal_form)

@bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.company = form.company.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('customers.customer', id=customer.id))
    return render_template('customers/edit.html', title='Редактировать клиента',
                         form=form, customer=customer)

@bp.route('/customers/<int:id>/add_note', methods=['POST'])
@login_required
def add_note(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            content=form.content.data,
            customer=customer,
            user_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()
        flash('Заметка добавлена')
    return redirect(url_for('customers.customer', id=id))

@bp.route('/customers/<int:id>/add_deal', methods=['POST'])
@login_required
def add_deal(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = DealForm()
    if form.validate_on_submit():
        deal = Deal(
            title=form.title.data,
            amount=form.amount.data,
            status=form.status.data,
            customer=customer,
            user_id=current_user.id
        )
        db.session.add(deal)
        db.session.commit()
        flash('Сделка создана')
    return redirect(url_for('customers.customer', id=id))

@bp.route('/deals')
@login_required
def deals():
    deals = Deal.query.filter_by(user_id=current_user.id).order_by(Deal.created_at.desc()).all()
    return render_template('customers/deals.html', title='Сделки', deals=deals) 