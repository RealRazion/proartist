PLATFORM_REGISTRY = [
    {"slug": "dashboard", "name": "Dashboard", "allow_non_team_users": True},
    {"slug": "todo", "name": "Todo", "allow_non_team_users": False},
    {"slug": "contests", "name": "Contests", "allow_non_team_users": True},
    {"slug": "music", "name": "Music", "allow_non_team_users": True},
    {"slug": "plugin-guides", "name": "Plugin Guides", "allow_non_team_users": True},
    {"slug": "api-center", "name": "API Center", "allow_non_team_users": False},
    {"slug": "locations", "name": "Locations", "allow_non_team_users": True},
    {"slug": "finance", "name": "Finance", "allow_non_team_users": True},
    {"slug": "content-studio", "name": "Content Studio", "allow_non_team_users": True},
    {"slug": "content-schedule", "name": "Content Schedule", "allow_non_team_users": True},
    {"slug": "fitness", "name": "Fitness", "allow_non_team_users": True},
    {"slug": "admin", "name": "Admin", "allow_non_team_users": False},
    {"slug": "manage-platforms", "name": "Platform Control", "allow_non_team_users": False},
    {"slug": "testing", "name": "Testing", "allow_non_team_users": False},
]


PLATFORM_REGISTRY_BY_SLUG = {entry["slug"]: entry for entry in PLATFORM_REGISTRY}


def is_system_platform(slug):
    return str(slug or "") in PLATFORM_REGISTRY_BY_SLUG
