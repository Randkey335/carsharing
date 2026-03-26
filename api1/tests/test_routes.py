"""Тесты для API-маршрутов приложения."""


# ── /api/health ──────────────────────────────────────────────────────

class TestHealthCheck:
    def test_health_returns_200(self, client):
        resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'


# ── /api/departments ─────────────────────────────────────────────────

class TestGetDepartments:
    def test_returns_empty_list_when_no_data(self, client):
        resp = client.get('/api/departments')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['data'] == []

    def test_returns_all_departments(self, client, seed_data):
        resp = client.get('/api/departments')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        codes = {d['code'] for d in data['data']}
        assert codes == {'IT', 'PM'}

    def test_department_fields(self, client, seed_data):
        resp = client.get('/api/departments')
        dept = resp.get_json()['data'][0]
        assert 'id' in dept
        assert 'name' in dept
        assert 'code' in dept


# ── /api/periods ─────────────────────────────────────────────────────

class TestGetPeriods:
    def test_returns_empty_list_when_no_data(self, client):
        resp = client.get('/api/periods')
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []

    def test_returns_all_periods(self, client, seed_data):
        resp = client.get('/api/periods')
        data = resp.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2

    def test_periods_ordered_by_start_date_desc(self, client, seed_data):
        resp = client.get('/api/periods')
        periods = resp.get_json()['data']
        dates = [p['start_date'] for p in periods]
        assert dates == sorted(dates, reverse=True)

    def test_period_fields(self, client, seed_data):
        resp = client.get('/api/periods')
        period = resp.get_json()['data'][0]
        for field in ('id', 'name', 'start_date', 'end_date', 'is_active'):
            assert field in period


# ── /api/periods/current ─────────────────────────────────────────────

class TestGetCurrentPeriod:
    def test_returns_current_period(self, client, seed_data):
        resp = client.get('/api/periods/current')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Текущий семестр'
        assert data['data']['is_active'] is True

    def test_returns_404_when_no_active_period(self, client):
        resp = client.get('/api/periods/current')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['success'] is False


# ── /api/manager/<username>/groups ───────────────────────────────────

class TestGetManagerGroups:
    def test_returns_404_for_unknown_manager(self, client, seed_data):
        resp = client.get('/api/manager/unknown_user/groups')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'MANAGER_NOT_FOUND'

    def test_returns_404_when_no_active_period(self, client, db, seed_data):
        # Деактивируем текущий период
        period = seed_data['active_period']
        period.is_active = False
        db.session.commit()

        resp = client.get('/api/manager/ivanov/groups')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['error_code'] == 'NO_ACTIVE_PERIOD'

    def test_returns_groups_for_manager(self, client, seed_data):
        resp = client.get('/api/manager/ivanov/groups')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

        groups = data['data']['groups']
        # ivanov — кафедра IT, у неё 2 группы в рекомендательном списке
        assert len(groups) == 2
        names = {g['group_name'] for g in groups}
        assert names == {'ИВТ-21', 'ИВТ-22'}

    def test_manager_info_in_response(self, client, seed_data):
        resp = client.get('/api/manager/ivanov/groups')
        manager = resp.get_json()['data']['manager']
        assert manager['username'] == 'ivanov'
        assert manager['full_name'] == 'Иванов Иван Иванович'
        assert manager['role'] == 'Заведующий кафедрой'

    def test_department_info_in_response(self, client, seed_data):
        resp = client.get('/api/manager/ivanov/groups')
        dept = resp.get_json()['data']['department']
        assert dept['code'] == 'IT'

    def test_period_info_in_response(self, client, seed_data):
        resp = client.get('/api/manager/ivanov/groups')
        period = resp.get_json()['data']['period']
        assert period['name'] == 'Текущий семестр'
        assert period['is_active'] is True

    def test_statistics_in_response(self, client, seed_data):
        resp = client.get('/api/manager/ivanov/groups')
        stats = resp.get_json()['data']['statistics']
        assert stats['total'] == 2
        assert stats['confirmed'] == 1
        assert stats['pending'] == 1
        assert stats['rejected'] == 0
        assert stats['in_progress'] == 0

    def test_group_fields(self, client, seed_data):
        resp = client.get('/api/manager/ivanov/groups')
        group = resp.get_json()['data']['groups'][0]
        for field in ('group_id', 'group_name', 'course', 'students_count',
                      'participation_status', 'status_display',
                      'recommendation_id', 'notes', 'created_at', 'updated_at'):
            assert field in group

    def test_status_display_values(self, client, seed_data):
        resp = client.get('/api/manager/ivanov/groups')
        groups = resp.get_json()['data']['groups']
        display_map = {g['participation_status']: g['status_display'] for g in groups}
        assert display_map.get('confirmed') == 'Подтверждено'
        assert display_map.get('pending') == 'Ожидает подтверждения'

    def test_other_manager_sees_only_own_department(self, client, seed_data):
        resp = client.get('/api/manager/sidorova/groups')
        assert resp.status_code == 200
        groups = resp.get_json()['data']['groups']
        # sidorova — кафедра PM, у неё 1 группа
        assert len(groups) == 1
        assert groups[0]['group_name'] == 'ПМ-21'
