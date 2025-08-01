from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.priority import Priority
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_properties import CustomProperties
    from ..models.task_relationships import TaskRelationships


T = TypeVar("T", bound="TaskUpdate")


@_attrs_define
class TaskUpdate:
    """
    Attributes:
        id (str): The universal, unique ID of the task.
        title (Union[Unset, str]): The title, which is a short description of what needs to be done.
        parent_id (Union[None, Unset, str]): The universal, unique ID of the parent task. This can be null.
        dartboard (Union[Unset, str]): The full title of the dartboard, which is a project or list of tasks.
        type_ (Union[Unset, str]): The title of the type of the task.
        status (Union[Unset, str]): The status from the list of available statuses.
        description (Union[Unset, str]): A longer description of the task, which can include markdown formatting.
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
        custom_properties (Union['CustomProperties', None, Unset]): The custom properties, which is a dict of custom
            properties that are associated with the task.
        task_relationships (Union['TaskRelationships', None, Unset]): The relationships associated with the task.
    """

    id: str
    title: Union[Unset, str] = UNSET
    parent_id: Union[None, Unset, str] = UNSET
    dartboard: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    assignees: Union[None, Unset, list[str]] = UNSET
    assignee: Union[None, Unset, str] = UNSET
    tags: Union[Unset, list[str]] = UNSET
    priority: Union[None, Priority, Unset] = UNSET
    start_at: Union[None, Unset, str] = UNSET
    due_at: Union[None, Unset, str] = UNSET
    size: Union[None, Unset, int, str] = UNSET
    custom_properties: Union["CustomProperties", None, Unset] = UNSET
    task_relationships: Union["TaskRelationships", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.custom_properties import CustomProperties
        from ..models.task_relationships import TaskRelationships

        id = self.id

        title = self.title

        parent_id: Union[None, Unset, str]
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        else:
            parent_id = self.parent_id

        dartboard = self.dartboard

        type_ = self.type_

        status = self.status

        description = self.description

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
        elif isinstance(self.task_relationships, TaskRelationships):
            task_relationships = self.task_relationships.to_dict()
        else:
            task_relationships = self.task_relationships

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id
        if dartboard is not UNSET:
            field_dict["dartboard"] = dartboard
        if type_ is not UNSET:
            field_dict["type"] = type_
        if status is not UNSET:
            field_dict["status"] = status
        if description is not UNSET:
            field_dict["description"] = description
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
        if custom_properties is not UNSET:
            field_dict["customProperties"] = custom_properties
        if task_relationships is not UNSET:
            field_dict["taskRelationships"] = task_relationships

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_properties import CustomProperties
        from ..models.task_relationships import TaskRelationships

        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title", UNSET)

        def _parse_parent_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_id = _parse_parent_id(d.pop("parentId", UNSET))

        dartboard = d.pop("dartboard", UNSET)

        type_ = d.pop("type", UNSET)

        status = d.pop("status", UNSET)

        description = d.pop("description", UNSET)

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
        ) -> Union["TaskRelationships", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                task_relationships_type_0 = TaskRelationships.from_dict(data)

                return task_relationships_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TaskRelationships", None, Unset], data)

        task_relationships = _parse_task_relationships(d.pop("taskRelationships", UNSET))

        task_update = cls(
            id=id,
            title=title,
            parent_id=parent_id,
            dartboard=dartboard,
            type_=type_,
            status=status,
            description=description,
            assignees=assignees,
            assignee=assignee,
            tags=tags,
            priority=priority,
            start_at=start_at,
            due_at=due_at,
            size=size,
            custom_properties=custom_properties,
            task_relationships=task_relationships,
        )

        task_update.additional_properties = d
        return task_update

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
