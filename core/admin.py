from django.contrib import admin
from .models import (
    ActivityEntry,
    NewsPost,
    Profile,
    Project,
    ProjectAttachment,
    RegistrationRequest,
    Task,
    TaskAttachment,
    TaskComment,
    Song,
    SongVersion,
    GrowProGoal,
    GrowProUpdate,
)

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(ProjectAttachment)
admin.site.register(TaskAttachment)
admin.site.register(TaskComment)
admin.site.register(ActivityEntry)
admin.site.register(NewsPost)
admin.site.register(RegistrationRequest)
admin.site.register(Song)
admin.site.register(SongVersion)
admin.site.register(GrowProGoal)
admin.site.register(GrowProUpdate)

