from flask import Blueprint, jsonify, request
from .models import db, Manager, Group, RecommendationList, RecommendationPeriod, Department
from datetime import date

api = Blueprint('api', __name__, url_prefix='/api')


def get_current_period():
    """Получить текущий активный период рекомендаций"""
    today = date.today()
    return RecommendationPeriod.query.filter(
        RecommendationPeriod.is_active == True,
        RecommendationPeriod.start_date <= today,
        RecommendationPeriod.end_date >= today
    ).first()


@api.route('/manager/<username>/groups', methods=['GET'])
def get_manager_groups(username):
    """
    API-метод для получения групп кафедры руководителя
    
    При запросе из браузера руководителя:
    1. Определяет его роль и принадлежность к кафедре
    2. Собирает из БД список групп его кафедры из рекомендательного списка на текущий период
    3. Возвращает данные в формате JSON
    
    Args:
        username: имя пользователя руководителя
    
    Returns:
        JSON с информацией о руководителе и списком групп
    """
    # 1. Определяем роль и принадлежность к кафедре
    manager = Manager.query.filter_by(username=username).first()
    
    if not manager:
        return jsonify({
            'success': False,
            'error': 'Руководитель не найден',
            'error_code': 'MANAGER_NOT_FOUND'
        }), 404
    
    # 2. Получаем текущий период
    current_period = get_current_period()
    
    if not current_period:
        return jsonify({
            'success': False,
            'error': 'Активный период рекомендаций не найден',
            'error_code': 'NO_ACTIVE_PERIOD'
        }), 404
    
    # 3. Собираем список групп кафедры из рекомендательного списка
    recommendations = RecommendationList.query.join(Group).filter(
        Group.department_id == manager.department_id,
        RecommendationList.period_id == current_period.id
    ).all()
    
    # 4. Формируем ответ
    groups_data = []
    for rec in recommendations:
        groups_data.append({
            'group_id': rec.group.id,
            'group_name': rec.group.name,
            'course': rec.group.course,
            'students_count': rec.group.students_count,
            'participation_status': rec.participation_status,
            'status_display': rec._get_status_display(),
            'recommendation_id': rec.id,
            'notes': rec.notes,
            'created_at': rec.created_at.isoformat() if rec.created_at else None,
            'updated_at': rec.updated_at.isoformat() if rec.updated_at else None
        })
    
    # Статистика по статусам
    status_stats = {
        'total': len(groups_data),
        'pending': sum(1 for g in groups_data if g['participation_status'] == 'pending'),
        'confirmed': sum(1 for g in groups_data if g['participation_status'] == 'confirmed'),
        'rejected': sum(1 for g in groups_data if g['participation_status'] == 'rejected'),
        'in_progress': sum(1 for g in groups_data if g['participation_status'] == 'in_progress')
    }
    
    return jsonify({
        'success': True,
        'data': {
            'manager': {
                'id': manager.id,
                'username': manager.username,
                'full_name': manager.full_name,
                'role': manager.role
            },
            'department': manager.department.to_dict(),
            'period': current_period.to_dict(),
            'groups': groups_data,
            'statistics': status_stats
        }
    })


@api.route('/departments', methods=['GET'])
def get_departments():
    """Получить список всех кафедр"""
    departments = Department.query.all()
    return jsonify({
        'success': True,
        'data': [d.to_dict() for d in departments]
    })


@api.route('/periods', methods=['GET'])
def get_periods():
    """Получить список всех периодов"""
    periods = RecommendationPeriod.query.order_by(
        RecommendationPeriod.start_date.desc()
    ).all()
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in periods]
    })


@api.route('/periods/current', methods=['GET'])
def get_current_period_route():
    """Получить текущий активный период"""
    period = get_current_period()
    if not period:
        return jsonify({
            'success': False,
            'error': 'Активный период не найден'
        }), 404
    
    return jsonify({
        'success': True,
        'data': period.to_dict()
    })


@api.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    return jsonify({
        'status': 'healthy',
        'message': 'API работает'
    })
