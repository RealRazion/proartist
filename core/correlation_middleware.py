"""
Correlation ID Middleware für Request Tracking
"""

import uuid
import logging
import threading

logger = logging.getLogger(__name__)

# Thread-lokale Speicher für Correlation IDs
_thread_locals = threading.local()


def get_correlation_id():
    """Besorgt die aktuelle Correlation ID"""
    return getattr(_thread_locals, 'correlation_id', None)


def set_correlation_id(correlation_id):
    """Setzt die Correlation ID"""
    _thread_locals.correlation_id = correlation_id


class CorrelationIdMiddleware:
    """
    Middleware die automatisch Correlation IDs für jeden Request generiert
    Ermöglicht Request-Tracking durch Logs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Correlation ID setzen (oder vorhandene nutzen)
        correlation_id = request.META.get('HTTP_X_CORRELATION_ID')
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        set_correlation_id(correlation_id)
        
        # Zur Request hinzufügen
        request.correlation_id = correlation_id
        
        # Zum Logger hinzufügen
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'correlation_id': correlation_id,
                'user_id': request.user.id if request.user.is_authenticated else None,
                'request_path': request.path,
                'method': request.method,
            }
        )
        
        response = self.get_response(request)
        
        # Response ID als Header setzen (für Client Tracking)
        response['X-Correlation-ID'] = correlation_id
        
        # Request abgeschlossen loggen
        logger.info(
            f"Request completed: {request.method} {request.path} {response.status_code}",
            extra={
                'correlation_id': correlation_id,
                'status_code': response.status_code,
                'path': request.path,
            }
        )
        
        return response
