"""
Structured Logging Configuration für Django
Mit Correlation IDs für Request-Tracking
"""

import json
import uuid
import logging
from pythonjsonlogger import jsonlogger


class CorrelationIdFilter(logging.Filter):
    """Filter für Correlation IDs"""
    def filter(self, record):
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = getattr(
                logging._thread_locals if hasattr(logging, '_thread_locals') else None,
                'correlation_id',
                'no-correlation-id'
            )
        return True


class JsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON Formatter für strukturierte Logs"""
    def add_fields(self, log_record, record, message_dict):
        super(JsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Zusätzliche Felder
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
        
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        if hasattr(record, 'request_path'):
            log_record['request_path'] = record.request_path


def get_logging_config(log_level='INFO'):
    """Django LOGGING Konfiguration"""
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'correlation_id': {
                '()': CorrelationIdFilter,
            },
        },
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'json': {
                '()': JsonFormatter,
            },
            'simple': {
                'format': '{levelname} | {asctime} | {name} | {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple',
                'filters': ['correlation_id'],
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'json',
                'filters': ['correlation_id'],
                'level': log_level,
            },
            'debug_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/debug.log',
                'maxBytes': 10485760,
                'backupCount': 3,
                'formatter': 'verbose',
                'filters': ['correlation_id'],
                'level': 'DEBUG',
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/error.log',
                'maxBytes': 10485760,
                'backupCount': 5,
                'formatter': 'json',
                'filters': ['correlation_id'],
                'level': 'ERROR',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
            'core': {
                'handlers': ['console', 'file', 'debug_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'api': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['console', 'file', 'error_file'],
            'level': log_level,
        },
    }
