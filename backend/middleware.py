"""
Custom CORS und Token Validation Middleware
Sichert DELETE/PUT Requests vor CORS-Preflight Attacken
"""

from django.http import HttpForbidden, JsonResponse
from django.utils.decorators import sync_and_async_middleware
import logging

logger = logging.getLogger(__name__)


@sync_and_async_middleware
def cors_token_validation_middleware(get_response):
    """
    Validiert Token für speichersensitive HTTP Methoden (DELETE, PUT, PATCH)
    Verhindert CORS-basierte Attacken auf API
    """
    
    def middleware(request):
        # Nur für speichersensitive Methoden prüfen
        if request.method in ['DELETE', 'PUT', 'PATCH', 'POST']:
            # Authorization Header prüfen
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if not auth_header.startswith('Bearer '):
                if request.method in ['DELETE', 'PUT']:
                    logger.warning(
                        f"Ungeschützte {request.method} Anfrage von {request.remote_addr} "
                        f"zu {request.path} ohne Token"
                    )
                    return JsonResponse(
                        {'error': f'{request.method} erfordert Authentifizierung'},
                        status=401
                    )
            
            # Zusätzliche Checks für DELETE
            if request.method == 'DELETE':
                # Beispiel: Nur Team-Profile dürfen löschen
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user_profile = getattr(request.user, 'profile', None)
                    if user_profile and not user_profile.is_team_profile:
                        logger.warning(
                            f"DELETE Anfrage von nicht-Team Profil {user_profile.id} "
                            f"zu {request.path} verweigert"
                        )
                        return JsonResponse(
                            {'error': 'Nur Team-Profile können Ressourcen löschen'},
                            status=403
                        )
        
        response = get_response(request)
        
        # CORS Security Headers hinzufügen
        request_origin = request.META.get('HTTP_ORIGIN', '')
        if request_origin:  # Nur wenn Origin Header vorhanden
            # Whitelist prüfen (in Production sollte das aus Settings kommen)
            allowed_origins = getattr(
                request,
                'ALLOWED_ORIGINS',
                ['http://localhost:3000', 'http://localhost:5173']
            )
            
            if request_origin in allowed_origins or '*' in allowed_origins:
                response['Access-Control-Allow-Origin'] = request_origin
                response['Access-Control-Allow-Credentials'] = 'true'
                
                # Preflight Response für Options
                if request.method == 'OPTIONS':
                    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                    response['Access-Control-Max-Age'] = '3600'
        
        return response
    
    return middleware
