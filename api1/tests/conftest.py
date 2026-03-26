import pytest
from datetime import date, datetime, timedelta
from app import create_app
from app.models import db as _db, Department, Manager, Group, RecommendationPeriod, RecommendationList


@pytest.fixture()
def app():
    """Создаёт экземпляр приложения с тестовой конфигурацией (SQLite in-memory)."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
    })

    with app.app_context():
        yield app
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def seed_data(app, db):
    """Заполняет БД тестовыми данными и возвращает словарь созданных объектов."""
    # Кафедры
    dept_it = Department(name='Кафедра информационных технологий', code='IT')
    dept_pm = Department(name='Кафедра прикладной математики', code='PM')
    db.session.add_all([dept_it, dept_pm])
    db.session.flush()

    # Руководители
    manager_ivanov = Manager(
        username='ivanov',
        full_name='Иванов Иван Иванович',
        role='Заведующий кафедрой',
        department_id=dept_it.id,
    )
    manager_sidorova = Manager(
        username='sidorova',
        full_name='Сидорова Анна Михайловна',
        role='Заведующий кафедрой',
        department_id=dept_pm.id,
    )
    db.session.add_all([manager_ivanov, manager_sidorova])
    db.session.flush()

    # Периоды
    today = date.today()
    active_period = RecommendationPeriod(
        name='Текущий семестр',
        start_date=today - timedelta(days=30),
        end_date=today + timedelta(days=30),
        is_active=True,
    )
    past_period = RecommendationPeriod(
        name='Прошлый семестр',
        start_date=today - timedelta(days=200),
        end_date=today - timedelta(days=60),
        is_active=False,
    )
    db.session.add_all([active_period, past_period])
    db.session.flush()

    # Группы
    group1 = Group(name='ИВТ-21', department_id=dept_it.id, course=4, students_count=25)
    group2 = Group(name='ИВТ-22', department_id=dept_it.id, course=3, students_count=28)
    group3 = Group(name='ПМ-21', department_id=dept_pm.id, course=4, students_count=20)
    db.session.add_all([group1, group2, group3])
    db.session.flush()

    # Рекомендательные списки (для текущего периода)
    rec1 = RecommendationList(
        group_id=group1.id,
        period_id=active_period.id,
        participation_status='confirmed',
        notes='Отличная группа',
    )
    rec2 = RecommendationList(
        group_id=group2.id,
        period_id=active_period.id,
        participation_status='pending',
    )
    rec3 = RecommendationList(
        group_id=group3.id,
        period_id=active_period.id,
        participation_status='rejected',
    )
    db.session.add_all([rec1, rec2, rec3])
    db.session.commit()

    return {
        'dept_it': dept_it,
        'dept_pm': dept_pm,
        'manager_ivanov': manager_ivanov,
        'manager_sidorova': manager_sidorova,
        'active_period': active_period,
        'past_period': past_period,
        'group1': group1,
        'group2': group2,
        'group3': group3,
        'rec1': rec1,
        'rec2': rec2,
        'rec3': rec3,
    }

    return {
        'dept_it': dept_it,
        'dept_pm': dept_pm,
        'manager_ivanov': manager_ivanov,
        'manager_sidorova': manager_sidorova,
        'active_period': active_period,
        'past_period': past_period,
        'group1': group1,
        'group2': group2,
        'group3': group3,
        'rec1': rec1,
        'rec2': rec2,
        'rec3': rec3,
    }
