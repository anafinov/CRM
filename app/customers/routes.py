from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.customers import bp
from app.customers.forms import CustomerForm, DealForm, NoteForm, CustomerSearchForm, CustomerCategoryForm
from app.models import Customer, Deal, Note
from sqlalchemy import or_, and_, func
from datetime import datetime

@bp.route('/customers', methods=['GET', 'POST'])
@login_required
def list():
    # Форма поиска и фильтрации
    search_form = CustomerSearchForm()
    
    # Базовый запрос - все клиенты текущего пользователя
    query = Customer.query.filter_by(user_id=current_user.id)
    
    # Применяем фильтры если форма отправлена
    if search_form.validate_on_submit():
        # Поиск по тексту (имя, email, компания)
        if search_form.search.data:
            search_term = f"%{search_form.search.data}%"
            query = query.filter(or_(
                Customer.name.ilike(search_term),
                Customer.email.ilike(search_term),
                Customer.company.ilike(search_term)
            ))
        
        # Фильтр по компании
        if search_form.company.data:
            query = query.filter(Customer.company.ilike(f"%{search_form.company.data}%"))
        
        # Фильтр по дате создания
        if search_form.date_from.data:
            query = query.filter(Customer.created_at >= search_form.date_from.data)
        if search_form.date_to.data:
            query = query.filter(Customer.created_at <= search_form.date_to.data)
        
        # Фильтр по наличию сделок
        if search_form.has_deals.data == 'yes':
            query = query.join(Deal).group_by(Customer.id).having(func.count(Deal.id) > 0)
        elif search_form.has_deals.data == 'no':
            query = query.outerjoin(Deal).group_by(Customer.id).having(func.count(Deal.id) == 0)
    
    # Получаем список клиентов с сортировкой
    sort_by = request.args.get('sort', 'created_at')
    sort_dir = request.args.get('dir', 'desc')
    
    if sort_by == 'name':
        query = query.order_by(Customer.name.asc() if sort_dir == 'asc' else Customer.name.desc())
    elif sort_by == 'company':
        query = query.order_by(Customer.company.asc() if sort_dir == 'asc' else Customer.company.desc())
    else:  # По умолчанию сортировка по дате создания
        query = query.order_by(Customer.created_at.asc() if sort_dir == 'asc' else Customer.created_at.desc())
    
    # Выполняем запрос
    customers = query.all()
    
    # Считаем статистику
    customers_count = Customer.query.filter_by(user_id=current_user.id).count()
    active_customers = Customer.query.filter_by(user_id=current_user.id, category='active').count()
    vip_customers = Customer.query.filter_by(user_id=current_user.id, category='vip').count()
    
    return render_template('customers/list.html', 
                         title='Клиенты', 
                         customers=customers,
                         search_form=search_form,
                         customers_count=customers_count,
                         active_customers=active_customers,
                         vip_customers=vip_customers,
                         sort_by=sort_by,
                         sort_dir=sort_dir)

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
    category_form = CustomerCategoryForm()
    
    # Устанавливаем текущую категорию в форме
    if customer.category:
        category_form.category.data = customer.category
    
    return render_template('customers/detail.html', title=customer.name,
                         customer=customer, note_form=note_form, 
                         deal_form=deal_form, category_form=category_form)

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
        customer.website = form.website.data
        customer.address = form.address.data
        customer.source = form.source.data
        customer.tags = form.tags.data
        customer.next_follow_up = form.next_follow_up.data
        customer.description = form.description.data
        customer.category = form.category.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('customers.customer', id=customer.id))
    return render_template('customers/edit.html', title='Редактировать клиента',
                         form=form, customer=customer)

@bp.route('/customers/<int:id>/update_category', methods=['POST'])
@login_required
def update_category(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = CustomerCategoryForm()
    
    if form.validate_on_submit():
        customer.category = form.category.data
        # Обновляем дату последнего контакта
        customer.last_contact = datetime.utcnow()
        db.session.commit()
        flash(f'Категория клиента изменена на {dict(form.category.choices).get(form.category.data)}')
    
    return redirect(url_for('customers.customer', id=id))

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
        # Обновляем дату последнего контакта
        customer.last_contact = datetime.utcnow()
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
        # Обновляем дату последнего контакта и категорию клиента
        customer.last_contact = datetime.utcnow()
        if customer.category == 'potential':
            customer.category = 'active'
        db.session.commit()
        flash('Сделка создана')
    return redirect(url_for('customers.customer', id=id))

@bp.route('/deals')
@login_required
def deals():
    deals = Deal.query.filter_by(user_id=current_user.id).order_by(Deal.created_at.desc()).all()
    return render_template('customers/deals.html', title='Сделки', deals=deals)

@bp.route('/customers/categories')
@login_required
def categories():
    # Получаем статистику по категориям
    potential = Customer.query.filter_by(user_id=current_user.id, category='potential').count()
    active = Customer.query.filter_by(user_id=current_user.id, category='active').count()
    vip = Customer.query.filter_by(user_id=current_user.id, category='vip').count()
    inactive = Customer.query.filter_by(user_id=current_user.id, category='inactive').count()
    
    # Группируем клиентов по категориям
    potential_customers = Customer.query.filter_by(user_id=current_user.id, category='potential').all()
    active_customers = Customer.query.filter_by(user_id=current_user.id, category='active').all()
    vip_customers = Customer.query.filter_by(user_id=current_user.id, category='vip').all()
    inactive_customers = Customer.query.filter_by(user_id=current_user.id, category='inactive').all()
    
    return render_template('customers/categories.html', title='Категории клиентов',
                         potential=potential, active=active, vip=vip, inactive=inactive,
                         potential_customers=potential_customers, active_customers=active_customers,
                         vip_customers=vip_customers, inactive_customers=inactive_customers) 