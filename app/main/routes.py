from flask import render_template, send_file, Response
from flask_login import login_required, current_user
from app.main import bp
from app.models import Customer, Deal
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
import tempfile
import os
import xlsxwriter
from io import BytesIO

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Основные счетчики
    customers_count = Customer.query.filter_by(user_id=current_user.id).count()
    deals_count = Deal.query.filter_by(user_id=current_user.id).count()
    
    # Последние 5 сделок
    recent_deals = Deal.query.filter_by(user_id=current_user.id).order_by(Deal.created_at.desc()).limit(5).all()
    
    # Расчет суммы всех сделок
    total_deal_amount = db.session.query(func.sum(Deal.amount)).filter(Deal.user_id==current_user.id).scalar() or 0
    
    # Количество сделок по статусам
    deal_statuses = db.session.query(Deal.status, func.count(Deal.id))\
        .filter(Deal.user_id==current_user.id)\
        .group_by(Deal.status)\
        .all()
    
    deal_status_data = {status: count for status, count in deal_statuses}
    
    # Данные для графика: новые клиенты за последние 7 дней
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    
    new_customers_last_week = db.session.query(
        func.date(Customer.created_at).label('date'),
        func.count(Customer.id).label('count')
    ).filter(
        Customer.user_id == current_user.id,
        Customer.created_at >= one_week_ago
    ).group_by(
        func.date(Customer.created_at)
    ).all()
    
    # Преобразуем в формат для графика
    dates = [(today - timedelta(days=i)).strftime('%d.%m') for i in range(7, 0, -1)]
    customer_counts = [0] * 7
    
    for date_obj, count in new_customers_last_week:
        # Проверяем, что date_obj является объектом даты
        if isinstance(date_obj, str):
            # Если дата - строка, преобразуем её в объект datetime.date
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            except ValueError:
                # Если формат не подходит, пропускаем эту запись
                continue
        
        days_ago = (today.date() - date_obj).days
        if 0 <= days_ago < 7:
            customer_counts[6 - days_ago] = count
    
    # Данные для графика: сумма сделок по месяцам
    current_year = today.year
    months_labels = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    
    monthly_deals = db.session.query(
        func.extract('month', Deal.created_at).label('month'),
        func.sum(Deal.amount).label('amount')
    ).filter(
        Deal.user_id == current_user.id,
        func.extract('year', Deal.created_at) == current_year
    ).group_by(
        func.extract('month', Deal.created_at)
    ).all()
    
    monthly_amounts = [0] * 12
    for month, amount in monthly_deals:
        if month is not None and amount is not None:
            month_idx = int(month) - 1
            if 0 <= month_idx < 12:
                monthly_amounts[month_idx] = float(amount)
    
    # Топ клиенты по сумме сделок
    top_customers = db.session.query(
        Customer.id, Customer.name, func.sum(Deal.amount).label('total')
    ).join(Deal, Deal.customer_id == Customer.id)\
    .filter(Deal.user_id == current_user.id)\
    .group_by(Customer.id, Customer.name)\
    .order_by(func.sum(Deal.amount).desc())\
    .limit(5)\
    .all()
    
    # Средний размер сделки
    avg_deal_amount = db.session.query(func.avg(Deal.amount))\
        .filter(Deal.user_id == current_user.id)\
        .scalar() or 0
    
    # Последние активности: новые клиенты и сделки
    recent_activities = []
    
    recent_customers = Customer.query.filter_by(user_id=current_user.id)\
        .order_by(Customer.created_at.desc())\
        .limit(3)\
        .all()
    
    for customer in recent_customers:
        recent_activities.append({
            'type': 'customer',
            'date': customer.created_at,
            'data': customer
        })
    
    for deal in recent_deals[:3]:
        recent_activities.append({
            'type': 'deal',
            'date': deal.created_at,
            'data': deal
        })
    
    # Сортировка активностей по дате (сначала новые)
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:5]  # Только 5 последних активностей
        
    return render_template('main/index.html', title='Главная',
                         customers_count=customers_count,
                         deals_count=deals_count,
                         recent_deals=recent_deals,
                         total_deal_amount=total_deal_amount,
                         avg_deal_amount=avg_deal_amount,
                         deal_status_data=deal_status_data,
                         dates=dates,
                         customer_counts=customer_counts,
                         months_labels=months_labels,
                         monthly_amounts=monthly_amounts,
                         top_customers=top_customers,
                         recent_activities=recent_activities)

@bp.route('/export-excel')
@login_required
def export_excel():
    # Создаем объект BytesIO для хранения Excel-файла в памяти
    output = BytesIO()
    
    # Создаем новую книгу Excel и добавляем рабочие листы
    workbook = xlsxwriter.Workbook(output)
    
    # Создаем форматы для заголовков и данных
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': '#3a86ff',
        'font_color': 'white'
    })
    
    data_format = workbook.add_format({
        'border': 1
    })
    
    currency_format = workbook.add_format({
        'border': 1,
        'num_format': '# ##0 ₽'
    })
    
    date_format = workbook.add_format({
        'border': 1,
        'num_format': 'dd.mm.yyyy'
    })
    
    # Экспорт клиентов
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    if customers:
        # Создаем лист для клиентов
        customers_sheet = workbook.add_worksheet("Клиенты")
        
        # Добавляем заголовки
        headers = ["ID", "Имя", "Email", "Телефон", "Компания", "Дата создания"]
        for col, header in enumerate(headers):
            customers_sheet.write(0, col, header, header_format)
        
        # Добавляем данные
        for row, customer in enumerate(customers, start=1):
            customers_sheet.write(row, 0, customer.id, data_format)
            customers_sheet.write(row, 1, customer.name, data_format)
            customers_sheet.write(row, 2, customer.email, data_format)
            customers_sheet.write(row, 3, customer.phone, data_format)
            customers_sheet.write(row, 4, customer.company, data_format)
            customers_sheet.write(row, 5, customer.created_at, date_format)
        
        # Устанавливаем ширину столбцов
        customers_sheet.set_column(0, 0, 8)  # ID
        customers_sheet.set_column(1, 1, 25) # Имя
        customers_sheet.set_column(2, 2, 30) # Email
        customers_sheet.set_column(3, 3, 15) # Телефон
        customers_sheet.set_column(4, 4, 25) # Компания
        customers_sheet.set_column(5, 5, 18) # Дата создания
    
    # Экспорт сделок
    deals = Deal.query.filter_by(user_id=current_user.id).all()
    if deals:
        # Создаем лист для сделок
        deals_sheet = workbook.add_worksheet("Сделки")
        
        # Добавляем заголовки
        headers = ["ID", "Название", "Клиент", "Сумма", "Статус", "Дата создания"]
        for col, header in enumerate(headers):
            deals_sheet.write(0, col, header, header_format)
        
        # Словарь для перевода статусов
        status_translation = {
            'new': 'Новая',
            'negotiation': 'В процессе',
            'won': 'Завершена',
            'lost': 'Потеряна'
        }
        
        # Добавляем данные
        for row, deal in enumerate(deals, start=1):
            deals_sheet.write(row, 0, deal.id, data_format)
            deals_sheet.write(row, 1, deal.title, data_format)
            deals_sheet.write(row, 2, deal.customer.name if deal.customer else "", data_format)
            deals_sheet.write(row, 3, deal.amount, currency_format)
            deals_sheet.write(row, 4, status_translation.get(deal.status, deal.status), data_format)
            deals_sheet.write(row, 5, deal.created_at, date_format)
        
        # Устанавливаем ширину столбцов
        deals_sheet.set_column(0, 0, 8)   # ID
        deals_sheet.set_column(1, 1, 30)  # Название
        deals_sheet.set_column(2, 2, 25)  # Клиент
        deals_sheet.set_column(3, 3, 15)  # Сумма
        deals_sheet.set_column(4, 4, 15)  # Статус
        deals_sheet.set_column(5, 5, 18)  # Дата создания
    
    # Аналитика по сделкам
    analytics_sheet = workbook.add_worksheet("Аналитика")
    
    # Заголовок
    analytics_sheet.merge_range('A1:C1', 'Аналитика по сделкам', header_format)
    
    # Основные метрики
    analytics_sheet.write(2, 0, "Метрика", header_format)
    analytics_sheet.write(2, 1, "Значение", header_format)
    
    # Общее количество клиентов
    analytics_sheet.write(3, 0, "Общее количество клиентов", data_format)
    analytics_sheet.write(3, 1, Customer.query.filter_by(user_id=current_user.id).count(), data_format)
    
    # Общее количество сделок
    analytics_sheet.write(4, 0, "Общее количество сделок", data_format)
    analytics_sheet.write(4, 1, Deal.query.filter_by(user_id=current_user.id).count(), data_format)
    
    # Общая сумма сделок
    total_amount = db.session.query(func.sum(Deal.amount)).filter(Deal.user_id==current_user.id).scalar() or 0
    analytics_sheet.write(5, 0, "Общая сумма сделок", data_format)
    analytics_sheet.write(5, 1, total_amount, currency_format)
    
    # Средняя сумма сделки
    avg_amount = db.session.query(func.avg(Deal.amount)).filter(Deal.user_id==current_user.id).scalar() or 0
    analytics_sheet.write(6, 0, "Средняя сумма сделки", data_format)
    analytics_sheet.write(6, 1, avg_amount, currency_format)
    
    # Количество сделок по статусам
    analytics_sheet.write(8, 0, "Статус сделки", header_format)
    analytics_sheet.write(8, 1, "Количество", header_format)
    analytics_sheet.write(8, 2, "Общая сумма", header_format)
    
    deal_statuses = db.session.query(
        Deal.status, 
        func.count(Deal.id).label('count'),
        func.sum(Deal.amount).label('total')
    ).filter(Deal.user_id==current_user.id).group_by(Deal.status).all()
    
    # Словарь для перевода статусов
    status_translation = {
        'new': 'Новая',
        'negotiation': 'В процессе',
        'won': 'Завершена',
        'lost': 'Потеряна'
    }
    
    for i, (status, count, total) in enumerate(deal_statuses, start=9):
        status_name = status_translation.get(status, status)
        analytics_sheet.write(i, 0, status_name, data_format)
        analytics_sheet.write(i, 1, count, data_format)
        analytics_sheet.write(i, 2, total or 0, currency_format)
    
    # Устанавливаем ширину столбцов
    analytics_sheet.set_column(0, 0, 30)
    analytics_sheet.set_column(1, 1, 15)
    analytics_sheet.set_column(2, 2, 15)
    
    # Сохраняем и закрываем книгу
    workbook.close()
    
    # Устанавливаем позицию в начало файла
    output.seek(0)
    
    # Генерируем имя файла с текущей датой
    filename = f"CRM_Export_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
    
    # Отправляем файл пользователю
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    ) 