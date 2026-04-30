from enum import Enum


class EventKindsEnum(str, Enum):
    COMMENT_CREATED = "comment.created"
    DOC_CREATED = "doc.created"
    DOC_DELETED = "doc.deleted"
    DOC_UPDATED = "doc.updated"
    TASK_ASSIGNEES_UPDATED = "task.assignees_updated"
    TASK_CREATED = "task.created"
    TASK_DELETED = "task.deleted"
    TASK_STATUS_UPDATED = "task.status_updated"
    TASK_UPDATED = "task.updated"

    def __str__(self) -> str:
        return str(self.value)
