"""Тесты для моделей базы данных."""
from app.models import Department, Manager, Group, RecommendationPeriod, RecommendationList


class TestDepartment:
    def test_to_dict(self, app, db):
        dept = Department(name='Тестовая кафедра', code='TST')
        db.session.add(dept)
        db.session.commit()
        d = dept.to_dict()
        assert d['name'] == 'Тестовая кафедра'
        assert d['code'] == 'TST'
        assert 'id' in d


class TestManager:
    def test_to_dict_includes_department(self, app, db):
        dept = Department(name='Кафедра', code='KF')
        db.session.add(dept)
        db.session.flush()
        mgr = Manager(username='test', full_name='Тестов Тест', role='Роль', department_id=dept.id)
        db.session.add(mgr)
        db.session.commit()
        d = mgr.to_dict()
        assert d['username'] == 'test'
        assert d['department']['code'] == 'KF'


class TestRecommendationPeriod:
    def test_to_dict(self, app, db, seed_data):
        period = seed_data['active_period']
        d = period.to_dict()
        assert d['is_active'] is True
        assert 'start_date' in d
        assert 'end_date' in d


class TestGroup:
    def test_to_dict(self, app, db, seed_data):
        group = seed_data['group1']
        d = group.to_dict()
        assert d['name'] == 'ИВТ-21'
        assert d['course'] == 4
        assert d['students_count'] == 25


class TestRecommendationList:
    def test_to_dict(self, app, db, seed_data):
        rec = seed_data['rec1']
        d = rec.to_dict()
        assert d['participation_status'] == 'confirmed'
        assert d['status_display'] == 'Подтверждено'
        assert d['group']['name'] == 'ИВТ-21'
        assert d['period']['name'] == 'Текущий семестр'

    def test_status_display_pending(self, app, db, seed_data):
        rec = seed_data['rec2']
        assert rec._get_status_display() == 'Ожидает подтверждения'

    def test_status_display_rejected(self, app, db, seed_data):
        rec = seed_data['rec3']
        assert rec._get_status_display() == 'Отклонено'

    def test_status_display_unknown_returns_raw(self, app, db, seed_data):
        rec = seed_data['rec1']
        rec.participation_status = 'custom_status'
        assert rec._get_status_display() == 'custom_status'
