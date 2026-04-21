"""
API Input Validation Mixins und Utilities
Zentrale Business-Logic Validierung auf Serializer Level
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import TASK_STATUS_CHOICES, PRIORITY_CHOICES


class TaskStatusValidator:
    """Validator für Task Status"""
    VALID_STATUSES = ['OPEN', 'IN_PROGRESS', 'REVIEW', 'DONE']
    
    def __call__(self, value):
        if value not in self.VALID_STATUSES:
            raise serializers.ValidationError(
                f"Task Status '{value}' ist nicht erlaubt. "
                f"Erlaubte Werte: {', '.join(self.VALID_STATUSES)}"
            )


class PriorityValidator:
    """Validator für Task Priority"""
    VALID_PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    def __call__(self, value):
        if value not in self.VALID_PRIORITIES:
            raise serializers.ValidationError(
                f"Priorität '{value}' ist nicht erlaubt. "
                f"Erlaubte Werte: {', '.join(self.VALID_PRIORITIES)}"
            )


class DueDateValidator:
    """Validator für Fälligkeitsdaten"""
    
    def __call__(self, value):
        from datetime import datetime, timedelta
        
        if value is None:
            return
        
        # Due date muss in der Zukunft liegen
        if value < datetime.now().date():
            raise serializers.ValidationError(
                "Fälligkeitsdatum kann nicht in der Vergangenheit liegen"
            )


class UniqueConstraintValidator:
    """
    Validator für eindeutige Constraints
    Kann mehrere Felder gleichzeitig prüfen
    """
    
    def __init__(self, model, fields, message=None):
        self.model = model
        self.fields = fields if isinstance(fields, list) else [fields]
        self.message = message
    
    def __call__(self, value):
        from django.db.models import Q
        
        query = Q()
        for field in self.fields:
            query |= Q(**{field: value})
        
        if self.model.objects.filter(query).exists():
            msg = self.message or f"Eine Instanz mit diesem Wert existiert bereits"
            raise serializers.ValidationError(msg)


class ValidatorMixin:
    """
    Mixin für Serializer mit automatischer Validierung
    
    Beispiel:
        class TaskSerializer(ValidatorMixin, serializers.ModelSerializer):
            status = serializers.CharField(validators=[TaskStatusValidator()])
            priority = serializers.CharField(validators=[PriorityValidator()])
            
            class Meta:
                model = Task
                fields = ['id', 'title', 'status', 'priority', 'due_date']
    """
    
    def validate_business_logic(self, data):
        """
        Override diese Methode für Custom Business-Logic Validierung
        Wird nach Field-Validierung aufgerufen
        """
        return data
    
    def validate(self, data):
        """Root validator - nutzt die business_logic Methode"""
        data = super().validate(data)
        return self.validate_business_logic(data)


class TaskCreateUpdateValidator(ValidatorMixin):
    """
    Spezielle Validierung für Task Create/Update
    """
    
    def validate_business_logic(self, data):
        """Spezifische Task Validierung"""
        
        # Wenn Status zu REVIEW oder DONE geändert wird
        # muss Task assigned sein
        if data.get('status') in ['REVIEW', 'DONE']:
            if not data.get('assignees'):
                raise serializers.ValidationError({
                    'assignees': 'Task muss zugewiesen sein, um Status zu ändern'
                })
        
        # Kann nicht mehrere Priority Levels haben
        if data.get('priority') == 'CRITICAL' and not data.get('due_date'):
            raise serializers.ValidationError({
                'due_date': 'Kritische Tasks müssen ein Fälligkeitsdatum haben'
            })
        
        return data


class ProjectCreateUpdateValidator(ValidatorMixin):
    """
    Spezielle Validierung für Project Create/Update
    """
    
    def validate_business_logic(self, data):
        """Spezifische Project Validierung"""
        
        # Projekt muss mindestens einen Owner haben
        if self.instance is None:  # Bei Create
            if not data.get('owners'):
                raise serializers.ValidationError({
                    'owners': 'Projekt muss mindestens einen Owner haben'
                })
        
        # Title muss eindeutig pro Team sein
        title = data.get('title')
        if title:
            from .models import Project
            from .access import ProjectAccessValidator
            
            # Prüfe Duplikate
            query = Project.objects.filter(title=title)
            if self.instance:
                query = query.exclude(id=self.instance.id)
            
            if query.exists():
                raise serializers.ValidationError({
                    'title': 'Ein Projekt mit diesem Namen existiert bereits'
                })
        
        return data
