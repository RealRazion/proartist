"""
Zentrale Project Access Validator
Verhindert Duplikation von Permission-Logik
"""

from .models import Profile, ProjectParticipant


class ProjectAccessValidator:
    """
    Zentrale Autorisierer für Projekt-Zugriffe
    
    Definiert konsistente Zugriffs-Level:
    - view: Kann Projekt ansehen
    - manage: Kann Projekt konfigurieren
    - manage_tasks: Kann Tasks erstellen/editieren
    - delete: Kann Projekt löschen
    """
    
    LEVELS = {
        'view': 1,
        'manage': 2,
        'manage_tasks': 2,
        'delete': 3,
    }
    
    @staticmethod
    def _is_team_profile(profile):
        """Prüft ob Profile ein Team-Profile ist"""
        if profile is None:
            return False
        return profile.roles.filter(key='TEAM').exists()
    
    @staticmethod
    def _is_project_owner(profile, project):
        """Prüft ob Profile der Projekt-Owner ist"""
        return project.owners.filter(id=profile.id).exists()
    
    @staticmethod
    def _is_project_participant(profile, project):
        """Prüft ob Profile ein Projekt-Teilnehmer ist"""
        return ProjectParticipant.objects.filter(
            profile=profile,
            project=project,
            can_view=True
        ).exists()
    
    @staticmethod
    def validate_access(profile, project, required_level='view'):
        """
        Validiert Zugriff auf Projekt
        
        Args:
            profile: User Profile Object
            project: Project Object  
            required_level: 'view', 'manage', 'manage_tasks', 'delete'
        
        Returns:
            bool: True wenn Zugriff erlaubt, False sonst
        """
        if profile is None or project is None:
            return False
        
        level = ProjectAccessValidator.LEVELS.get(required_level, 1)
        
        # Team Profiles haben vollen Zugriff
        if ProjectAccessValidator._is_team_profile(profile):
            return True
        
        # Project Owners
        if ProjectAccessValidator._is_project_owner(profile, project):
            if level <= 2:
                return True
            if level == 3:
                return True
        
        # Projekt Participants
        if ProjectAccessValidator._is_project_participant(profile, project):
            if required_level == 'view':
                return True
            
            # Manage/Edit Berechtigungen für Participants
            participant = ProjectParticipant.objects.get(
                profile=profile,
                project=project
            )
            if required_level == 'manage' and participant.can_manage:
                return True
            if required_level == 'manage_tasks' and participant.can_edit_tasks:
                return True
        
        return False
    
    @staticmethod
    def can_view(profile, project):
        """Shorthand: Kann Projekt angesehen werden?"""
        return ProjectAccessValidator.validate_access(profile, project, 'view')
    
    @staticmethod
    def can_manage(profile, project):
        """Shorthand: Kann Projekt verwaltet werden?"""
        return ProjectAccessValidator.validate_access(profile, project, 'manage')
    
    @staticmethod
    def can_manage_tasks(profile, project):
        """Shorthand: Können Projekt-Tasks verwaltet werden?"""
        return ProjectAccessValidator.validate_access(profile, project, 'manage_tasks')
    
    @staticmethod
    def can_delete(profile, project):
        """Shorthand: Kann Projekt gelöscht werden?"""
        return ProjectAccessValidator.validate_access(profile, project, 'delete')
    
    @staticmethod
    def get_access_level(profile, project):
        """
        Bestimmt das Zugriffs-Level eines Profiles auf ein Projekt
        
        Returns: 'admin', 'owner', 'participant', 'none'
        """
        if ProjectAccessValidator._is_team_profile(profile):
            return 'admin'
        
        if ProjectAccessValidator._is_project_owner(profile, project):
            return 'owner'
        
        if ProjectAccessValidator._is_project_participant(profile, project):
            return 'participant'
        
        return 'none'
