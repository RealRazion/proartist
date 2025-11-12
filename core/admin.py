from django.contrib import admin
from .models import (
    ActivityEntry,
    NewsPost,
    Profile,
    Project,
    ProjectAttachment,
    Task,
    TaskAttachment,
    TaskComment,
)

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(ProjectAttachment)
admin.site.register(TaskAttachment)
admin.site.register(TaskComment)
admin.site.register(ActivityEntry)
admin.site.register(NewsPost)

