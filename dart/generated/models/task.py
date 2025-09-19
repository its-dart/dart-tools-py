import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.priority import Priority
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment import Attachment
    from ..models.custom_properties import CustomProperties
    from ..models.task_relationships_type_0 import TaskRelationshipsType0


T = TypeVar("T", bound="Task")


@_attrs_define
class Task:
    """
    Attributes:
        id (str): The universal, unique ID of the task.
        html_url (str): The URL that can be used to open the task in the Dart web UI.
        title (str): The title, which is a short description of what needs to be done.
        parent_id (Union[None, str]): The universal, unique ID of the parent task. This can be null. These tasks have a
            parent-child relationship where the current task is the child and this task ID corresponds to the parent.
            Subtasks inherit context from their parent and are typically smaller units of work.
        dartboard (str): The full title of the dartboard, which is a project or list of tasks.
        type_ (str): The title of the type of the task.
        status (str): The status from the list of available statuses.
        description (str): A longer description of the task, which can include markdown formatting.
        attachments (list['Attachment']): The attachments, which is a list of attachments that are associated with the
            task.
        created_at (datetime.datetime): The date and time when the task was created in ISO format.
        updated_at (datetime.datetime): The date and time when the task was last updated in ISO format.
        assignees (Union[None, Unset, list[str]]): The names or emails of the users that the task is assigned to. Either
            this or assignee must be included, depending on whether the workspaces allows multiple assignees or not.
        assignee (Union[None, Unset, str]): The name or email of the user that the task is assigned to. Either this or
            assignees must be included, depending on whether the workspaces allows multiple assignees or not.
        tags (Union[Unset, list[str]]): Any tags that should be applied to the task, which can be used to filter and
            search for tasks. Tags are also known as labels or components and are strings that can be anything, but should
            be short and descriptive. This list can be empty.
        priority (Union[None, Priority, Unset]): The priority, which is a string that can be one of the specified
            options. This is used to sort tasks and determine which tasks should be done first.
        start_at (Union[None, Unset, str]): The start date, which is a date that the task should be started by in ISO
            format, like YYYY-MM-DD.
        due_at (Union[None, Unset, str]): The due date, which is a date that the task should be completed by in ISO
            format, like YYYY-MM-DD.
        size (Union[None, Unset, int, str]): The size, which represents the amount of work that needs to be done. This
            is used to determine how long the task will take to complete.
        time_tracking (Union[Unset, str]): The time tracking, which is a string that indicates the amount of time spent
            on the task in hh:mm:ss format (or an empty string if no time has been tracked).
        custom_properties (Union['CustomProperties', None, Unset]): The custom properties, which is a dict of custom
            properties that are associated with the task.
        task_relationships (Union['TaskRelationshipsType0', None, Unset]): The relationships associated with the task.
        created_by (Union[None, Unset, str]): The name or email (moniker) of the user that created the task.
        updated_by (Union[None, Unset, str]): The name or email (moniker) of the user that last updated the task.
    """

    id: str
    html_url: str
    title: str
    parent_id: Union[None, str]
    dartboard: str
    type_: str
    status: str
    description: str
    attachments: list["Attachment"]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    assignees: Union[None, Unset, list[str]] = UNSET
    assignee: Union[None, Unset, str] = UNSET
    tags: Union[Unset, list[str]] = UNSET
    priority: Union[None, Priority, Unset] = UNSET
    start_at: Union[None, Unset, str] = UNSET
    due_at: Union[None, Unset, str] = UNSET
    size: Union[None, Unset, int, str] = UNSET
    time_tracking: Union[Unset, str] = UNSET
    custom_properties: Union["CustomProperties", None, Unset] = UNSET
    task_relationships: Union["TaskRelationshipsType0", None, Unset] = UNSET
    created_by: Union[None, Unset, str] = UNSET
    updated_by: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.custom_properties import CustomProperties
        from ..models.task_relationships_type_0 import TaskRelationshipsType0

        id = self.id

        html_url = self.html_url

        title = self.title

        parent_id: Union[None, str]
        parent_id = self.parent_id

        dartboard = self.dartboard

        type_ = self.type_

        status = self.status

        description = self.description

        attachments = []
        for attachments_item_data in self.attachments:
            attachments_item = attachments_item_data.to_dict()
            attachments.append(attachments_item)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        assignees: Union[None, Unset, list[str]]
        if isinstance(self.assignees, Unset):
            assignees = UNSET
        elif isinstance(self.assignees, list):
            assignees = self.assignees

        else:
            assignees = self.assignees

        assignee: Union[None, Unset, str]
        if isinstance(self.assignee, Unset):
            assignee = UNSET
        else:
            assignee = self.assignee

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        priority: Union[None, Unset, str]
        if isinstance(self.priority, Unset):
            priority = UNSET
        elif isinstance(self.priority, Priority):
            priority = self.priority.value
        else:
            priority = self.priority

        start_at: Union[None, Unset, str]
        if isinstance(self.start_at, Unset):
            start_at = UNSET
        else:
            start_at = self.start_at

        due_at: Union[None, Unset, str]
        if isinstance(self.due_at, Unset):
            due_at = UNSET
        else:
            due_at = self.due_at

        size: Union[None, Unset, int, str]
        if isinstance(self.size, Unset):
            size = UNSET
        else:
            size = self.size

        time_tracking = self.time_tracking

        custom_properties: Union[None, Unset, dict[str, Any]]
        if isinstance(self.custom_properties, Unset):
            custom_properties = UNSET
        elif isinstance(self.custom_properties, CustomProperties):
            custom_properties = self.custom_properties.to_dict()
        else:
            custom_properties = self.custom_properties

        task_relationships: Union[None, Unset, dict[str, Any]]
        if isinstance(self.task_relationships, Unset):
            task_relationships = UNSET
        elif isinstance(self.task_relationships, TaskRelationshipsType0):
            task_relationships = self.task_relationships.to_dict()
        else:
            task_relationships = self.task_relationships

        created_by: Union[None, Unset, str]
        if isinstance(self.created_by, Unset):
            created_by = UNSET
        else:
            created_by = self.created_by

        updated_by: Union[None, Unset, str]
        if isinstance(self.updated_by, Unset):
            updated_by = UNSET
        else:
            updated_by = self.updated_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "htmlUrl": html_url,
                "title": title,
                "parentId": parent_id,
                "dartboard": dartboard,
                "type": type_,
                "status": status,
                "description": description,
                "attachments": attachments,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if assignees is not UNSET:
            field_dict["assignees"] = assignees
        if assignee is not UNSET:
            field_dict["assignee"] = assignee
        if tags is not UNSET:
            field_dict["tags"] = tags
        if priority is not UNSET:
            field_dict["priority"] = priority
        if start_at is not UNSET:
            field_dict["startAt"] = start_at
        if due_at is not UNSET:
            field_dict["dueAt"] = due_at
        if size is not UNSET:
            field_dict["size"] = size
        if time_tracking is not UNSET:
            field_dict["timeTracking"] = time_tracking
        if custom_properties is not UNSET:
            field_dict["customProperties"] = custom_properties
        if task_relationships is not UNSET:
            field_dict["taskRelationships"] = task_relationships
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if updated_by is not UNSET:
            field_dict["updatedBy"] = updated_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attachment import Attachment
        from ..models.custom_properties import CustomProperties
        from ..models.task_relationships_type_0 import TaskRelationshipsType0

        d = dict(src_dict)
        id = d.pop("id")

        html_url = d.pop("htmlUrl")

        title = d.pop("title")

        def _parse_parent_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        parent_id = _parse_parent_id(d.pop("parentId"))

        dartboard = d.pop("dartboard")

        type_ = d.pop("type")

        status = d.pop("status")

        description = d.pop("description")

        attachments = []
        _attachments = d.pop("attachments")
        for attachments_item_data in _attachments:
            attachments_item = Attachment.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_assignees(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                assignees_type_0 = cast(list[str], data)

                return assignees_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        assignees = _parse_assignees(d.pop("assignees", UNSET))

        def _parse_assignee(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        assignee = _parse_assignee(d.pop("assignee", UNSET))

        tags = cast(list[str], d.pop("tags", UNSET))

        def _parse_priority(data: object) -> Union[None, Priority, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                priority_type_0 = Priority(data)

                return priority_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Priority, Unset], data)

        priority = _parse_priority(d.pop("priority", UNSET))

        def _parse_start_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        start_at = _parse_start_at(d.pop("startAt", UNSET))

        def _parse_due_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        due_at = _parse_due_at(d.pop("dueAt", UNSET))

        def _parse_size(data: object) -> Union[None, Unset, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int, str], data)

        size = _parse_size(d.pop("size", UNSET))

        time_tracking = d.pop("timeTracking", UNSET)

        def _parse_custom_properties(
            data: object,
        ) -> Union["CustomProperties", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_properties_type_0 = CustomProperties.from_dict(data)

                return custom_properties_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CustomProperties", None, Unset], data)

        custom_properties = _parse_custom_properties(d.pop("customProperties", UNSET))

        def _parse_task_relationships(
            data: object,
        ) -> Union["TaskRelationshipsType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_task_relationships_type_0 = TaskRelationshipsType0.from_dict(data)

                return componentsschemas_task_relationships_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TaskRelationshipsType0", None, Unset], data)

        task_relationships = _parse_task_relationships(d.pop("taskRelationships", UNSET))

        def _parse_created_by(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        created_by = _parse_created_by(d.pop("createdBy", UNSET))

        def _parse_updated_by(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        updated_by = _parse_updated_by(d.pop("updatedBy", UNSET))

        task = cls(
            id=id,
            html_url=html_url,
            title=title,
            parent_id=parent_id,
            dartboard=dartboard,
            type_=type_,
            status=status,
            description=description,
            attachments=attachments,
            created_at=created_at,
            updated_at=updated_at,
            assignees=assignees,
            assignee=assignee,
            tags=tags,
            priority=priority,
            start_at=start_at,
            due_at=due_at,
            size=size,
            time_tracking=time_tracking,
            custom_properties=custom_properties,
            task_relationships=task_relationships,
            created_by=created_by,
            updated_by=updated_by,
        )

        task.additional_properties = d
        return task

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
