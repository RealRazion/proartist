from typing import Optional

from .models import ActivityEntry, Profile, Project, Task


def log_activity(
    event_type: str,
    title: str,
    description: str = "",
    *,
    actor: Optional[Profile] = None,
    severity: str = "INFO",
    project: Optional[Project] = None,
    task: Optional[Task] = None,
    metadata: Optional[dict] = None,
) -> ActivityEntry:
    """
    Persist a lightweight activity entry for the feed.
    """
    return ActivityEntry.objects.create(
        event_type=event_type,
        title=title,
        description=description,
        severity=severity,
        actor=actor,
        project=project,
        task=task,
        metadata=metadata or {},
    )
