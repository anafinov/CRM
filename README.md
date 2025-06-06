# Инструкция по установке CRM системы

## Предварительные требования

1. Установите Python 3.8 или выше с сайта [python.org](https://www.python.org/downloads/)

## Шаги установки

1. Распакуйте файлы проекта в удобное место

2. Откройте командную строку (терминал) и перейдите в папку проекта:
```bash
cd путь/к/папке/CRM
```

3. Создайте виртуальное окружение:
```bash
python -m venv .venv
```

4. Активируйте виртуальное окружение:
- Для Windows:
```bash
.venv\Scripts\activate
```
- Для Linux/Mac:
```bash
source .venv/bin/activate
```

5. Установите зависимости:
```bash
pip install -r requirements.txt
```

6. (Опционально) Создайте файл `.env` в корневой папке проекта со следующим содержимым:
```
SECRET_KEY=ваш-секретный-ключ
```

7. Инициализируйте базу данных:
```bash
python create_db.py
```

Этот шаг нужно выполнить только один раз при первоначальной настройке базы данных. Скрипт создаст все необходимые таблицы в базе данных.

8. Запустите приложение:
```bash
python run.py
```

9. Откройте браузер и перейдите по адресу: http://localhost:5000

## Первые шаги после установки

1. Зарегистрируйте нового пользователя через веб-интерфейс
2. Войдите в систему
3. Начните добавлять клиентов и сделки

## Управление базой данных

### Инициализация базы данных
Скрипт `create_db.py` используется для создания всех таблиц в базе данных. Его нужно запустить только один раз при первоначальной настройке системы. Повторный запуск этого скрипта не повредит существующей базе данных.

### Обновление базы данных
Если после обновления появилась ошибка с отсутствующими колонками в базе данных, выполните:
```bash
python update_db.py
```

Этот скрипт добавит новые колонки в существующие таблицы, не затрагивая имеющиеся данные.

## Функциональность CRM

### Клиенты
- Управление контактами клиентов
- Категоризация клиентов (потенциальные, активные, VIP, неактивные)
- Расширенная информация о клиентах (веб-сайт, источник, теги и т.д.)
- Поиск и фильтрация клиентов

### Сделки
- Отслеживание сделок по статусам
- Связь сделок с клиентами
- Расчет вероятности закрытия сделок

### Аналитика
- Ключевые метрики на главной странице
- Графики продаж и новых клиентов
- Отчеты по категориям клиентов

### Экспорт данных
- Экспорт данных в Excel
- Формирование отчетов по клиентам и сделкам

## Поддержка

При возникновении проблем обращайтесь к разработчику. 