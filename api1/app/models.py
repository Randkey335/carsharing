from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Department(db.Model):
    """Модель кафедры"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    
    # Связи
    managers = db.relationship('Manager', backref='department', lazy='dynamic')
    groups = db.relationship('Group', backref='department', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code
        }


class Manager(db.Model):
    """Модель руководителя кафедры"""
    __tablename__ = 'managers'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), nullable=False)  # Заведующий, Заместитель и т.д.
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'department': self.department.to_dict() if self.department else None
        }


class RecommendationPeriod(db.Model):
    """Модель периода рекомендаций"""
    __tablename__ = 'recommendation_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Осенний семестр 2025
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Связи
    recommendations = db.relationship('RecommendationList', backref='period', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_active': self.is_active
        }


class Group(db.Model):
    """Модель учебной группы"""
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # ИВТ-21
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    course = db.Column(db.Integer, nullable=False)  # Курс обучения
    students_count = db.Column(db.Integer, default=0)
    
    # Связи
    recommendations = db.relationship('RecommendationList', backref='group', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'course': self.course,
            'students_count': self.students_count,
            'department_id': self.department_id
        }


class RecommendationList(db.Model):
    """Модель рекомендательного списка (связь группа-период с статусом)"""
    __tablename__ = 'recommendation_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('recommendation_periods.id'), nullable=False)
    participation_status = db.Column(db.String(50), nullable=False, default='pending')
    # Статусы: pending (ожидает), confirmed (подтверждено), rejected (отклонено), in_progress (в процессе)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group': self.group.to_dict() if self.group else None,
            'period': self.period.to_dict() if self.period else None,
            'participation_status': self.participation_status,
            'status_display': self._get_status_display(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes
        }
    
    def _get_status_display(self):
        """Возвращает человекочитаемый статус"""
        status_map = {
            'pending': 'Ожидает подтверждения',
            'confirmed': 'Подтверждено',
            'rejected': 'Отклонено',
            'in_progress': 'В процессе'
        }
        return status_map.get(self.participation_status, self.participation_status)
