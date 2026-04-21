"""
File Upload Validators für Django Models
Sichert Datei-Uploads mit Größen- und Typ-Validierung
"""

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
import os
import magic  # python-magic für Datei-Typ Validierung


# Maximale Dateigrößen
MAX_CHAT_FILE_SIZE = 5 * 1024 * 1024  # 5MB für Chat-Dateien
MAX_PROJECT_FILE_SIZE = 50 * 1024 * 1024  # 50MB für Projekt-Dateien
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB für Avatare

# Erlaubte Datei-Typen
ALLOWED_CHAT_TYPES = {
    'image/jpeg', 'image/png', 'image/webp', 'image/gif',
    'application/pdf',
    'text/plain', 'text/csv',
    'application/zip',
}

ALLOWED_PROJECT_TYPES = {
    'image/jpeg', 'image/png', 'image/webp',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'application/msword',
    'text/plain',
}

ALLOWED_AUDIO_TYPES = {
    'audio/mpeg', 'audio/wav', 'audio/aac', 'audio/ogg', 'audio/flac',
}

BLOCKED_EXTENSIONS = {'.exe', '.sh', '.bat', '.cmd', '.dll', '.so'}


def validate_file_size(file, max_size):
    """Validiert Datei-Größe"""
    if file.size > max_size:
        mb = max_size / (1024 * 1024)
        raise ValidationError(f'Datei zu groß. Maximum: {mb}MB')


def validate_file_type(file, allowed_types):
    """
    Validiert Datei-Typ basierend auf MIME-Type
    Nutzt python-magic für sicherere Validierung
    """
    try:
        # Versuche python-magic zu nutzen (sicherer)
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # Reset file pointer
    except:
        # Fallback auf Django default
        mime_type = file.content_type
    
    if mime_type not in allowed_types:
        allowed_str = ', '.join(allowed_types)
        raise ValidationError(
            f'Datei-Typ nicht erlaubt. Erlaubte Typen: {allowed_str}'
        )


def validate_file_extension(file):
    """Validiert Datei-Extension gegen Blacklist"""
    name, ext = os.path.splitext(file.name)
    if ext.lower() in BLOCKED_EXTENSIONS:
        raise ValidationError(f'Datei-Typ .{ext} nicht erlaubt')


def validate_chat_file(file):
    """Validator für Chat-Datei Uploads"""
    validate_file_extension(file)
    validate_file_size(file, MAX_CHAT_FILE_SIZE)
    validate_file_type(file, ALLOWED_CHAT_TYPES)


def validate_project_file(file):
    """Validator für Projekt-Datei Uploads"""
    validate_file_extension(file)
    validate_file_size(file, MAX_PROJECT_FILE_SIZE)
    validate_file_type(file, ALLOWED_PROJECT_TYPES)


def validate_audio_file(file):
    """Validator für Audio-Datei Uploads"""
    validate_file_extension(file)
    validate_file_size(file, MAX_PROJECT_FILE_SIZE)
    validate_file_type(file, ALLOWED_AUDIO_TYPES)


def validate_avatar_file(file):
    """Validator für Avatar-Bilder"""
    allowed_image_types = {'image/jpeg', 'image/png', 'image/webp'}
    validate_file_extension(file)
    validate_file_size(file, MAX_AVATAR_SIZE)
    validate_file_type(file, allowed_image_types)
