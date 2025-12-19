from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import ProjectSerializer, TaskSerializer


def _broadcast(group, payload):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        group,
        {"type": "updates.message", "payload": payload},
    )


def notify_project_event(project, action):
    data = ProjectSerializer(project, context={"request": None}).data
    _broadcast(
        "projects_all",
        {
            "entity": "project",
            "action": action,
            "data": data,
        },
    )


def notify_task_event(task, action):
    data = TaskSerializer(task, context={"request": None}).data
    _broadcast(
        "tasks_all",
        {
            "entity": "task",
            "action": action,
            "data": data,
        },
    )
