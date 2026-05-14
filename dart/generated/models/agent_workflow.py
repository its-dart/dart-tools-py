from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_kind import EventKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_workflow_headers import AgentWorkflowHeaders


T = TypeVar("T", bound="AgentWorkflow")


@_attrs_define
class AgentWorkflow:
    """
    Attributes:
        id (str): The unique ID of the workflow.
        trigger (EventKind): * `tasks/create` - TASK_CREATE
            * `tasks/delete` - TASK_DELETE
            * `tasks/delete_fully` - TASK_DELETE_FULLY
            * `tasks/update_status` - TASK_UPDATE_STATUS
            * `tasks/update_title` - TASK_UPDATE_TITLE
            * `tasks/update_description` - TASK_UPDATE_DESCRIPTION
            * `tasks/update_priority` - TASK_UPDATE_PRIORITY
            * `tasks/update_size` - TASK_UPDATE_SIZE
            * `tasks/update_kind` - TASK_UPDATE_KIND
            * `tasks/update_start_at` - TASK_UPDATE_START_AT
            * `tasks/update_due_at` - TASK_UPDATE_DUE_AT
            * `tasks/update_recurrence` - TASK_UPDATE_RECURRENCE
            * `tasks/due_date_tomorrow` - TASK_DUE_DATE_TOMORROW
            * `tasks/update_reminder` - TASK_UPDATE_REMINDER
            * `tasks/reminder_now` - TASK_REMINDER_NOW
            * `tasks/update_assignees` - TASK_UPDATE_ASSIGNEES
            * `tasks/update_reviewers` - TASK_UPDATE_REVIEWERS
            * `tasks/update_subscriptions` - TASK_UPDATE_SUBSCRIPTIONS
            * `tasks/update_dartboard` - TASK_UPDATE_DARTBOARD
            * `tasks/update_tags` - TASK_UPDATE_TAGS
            * `tasks/update_relationships` - TASK_UPDATE_RELATIONSHIPS
            * `tasks/update_attachments` - TASK_UPDATE_ATTACHMENTS
            * `tasks/update_links` - TASK_UPDATE_LINKS
            * `tasks/update_docs` - TASK_UPDATE_DOCS
            * `tasks/comment` - TASK_COMMENT
            * `tasks/update_time_tracking` - TASK_UPDATE_TIME_TRACKING
            * `tasks/update_custom_property` - TASK_UPDATE_CUSTOM_PROPERTY
            * `tasks/update_other` - TASK_UPDATE_OTHER
            * `docs/create` - DOC_CREATE
            * `docs/update_title` - DOC_UPDATE_TITLE
            * `docs/update_other` - DOC_UPDATE_OTHER
            * `docs/delete` - DOC_DELETE
            * `pages/create` - PAGE_CREATE
            * `pages/update_title` - PAGE_UPDATE_TITLE
            * `pages/update_permissions` - PAGE_UPDATE_PERMISSIONS
            * `pages/update_other` - PAGE_UPDATE_OTHER
            * `pages/rollover` - DARTBOARD_ROLLOVER
            * `pages/delete` - PAGE_DELETE
            * `workspace/invite` - WORKSPACE_INVITE
            * `workspace/join` - WORKSPACE_JOIN
            * `workspace/update_role` - WORKSPACE_UPDATE_ROLE
            * `workspace/leave` - WORKSPACE_LEAVE
            * `workspace/update_property` - WORKSPACE_UPDATE_PROPERTY
            * `workspace/update_status` - WORKSPACE_UPDATE_STATUS
            * `workspace/update_other` - WORKSPACE_UPDATE_OTHER
            * `workspace/create` - WORKSPACE_CREATE
            * `workspace/data_import` - WORKSPACE_DATA_IMPORT
            * `workspace/data_export` - WORKSPACE_DATA_EXPORT
            * `workspace/delete` - WORKSPACE_DELETE
            * `workspace/upgrade` - WORKSPACE_UPGRADE
            * `workspace/downgrade_initialize` - WORKSPACE_DOWNGRADE_INITIALIZE
            * `workspace/downgrade_finalize` - WORKSPACE_DOWNGRADE_FINALIZE
            * `workspace/become_active` - WORKSPACE_BECOME_ACTIVE
            * `workspace/become_inactive` - WORKSPACE_BECOME_INACTIVE
            * `load/app` - LOAD_APP
            * `load/authenticate` - AUTHENTICATE
            * `load/unidle` - UNIDLE
            * `load/signup` - LOAD_SIGNUP
            * `profile/create` - PROFILE_CREATE
            * `profile/update` - PROFILE_UPDATE
            * `profile/delete` - PROFILE_DELETE
            * `profile/become_active` - PROFILE_BECOME_ACTIVE
            * `profile/become_inactive` - PROFILE_BECOME_INACTIVE
            * `onboarding/finish_step` - ONBOARDING_FINISH_STEP
            * `ai/props` - AI_PROPS
            * `ai/subtasks` - AI_SUBTASKS
            * `ai/content` - AI_CONTENT
            * `ai/translate` - AI_TRANSLATE
            * `ai/emoji` - AI_EMOJI
            * `ai/feedback` - AI_FEEDBACK
            * `ai/icon` - AI_ICON
            * `ai/report` - AI_REPORT
            * `ai/plan` - AI_PLAN
            * `ai/detect_duplicates` - AI_DETECT_DUPLICATES
            * `ai/filters` - AI_FILTERS
            * `ai/execute` - AI_EXECUTE
            * `ai/image` - AI_IMAGE
            * `help/resource_click` - HELP_RESOURCE_CLICK
            * `usage/submit_feedback` - USAGE_SUBMIT_FEEDBACK
            * `usage/undo` - USAGE_UNDO
            * `usage/redo` - USAGE_REDO
            * `usage/open_command_center` - USAGE_OPEN_COMMAND_CENTER
            * `usage/open_rightbar` - USAGE_OPEN_RIGHTBAR
            * `usage/open_fullscreen` - USAGE_OPEN_FULLSCREEN
            * `usage/open_task_overlay` - USAGE_OPEN_TASK_OVERLAY
            * `usage/copy_task_link` - USAGE_COPY_TASK_LINK
            * `usage/copy_branch` - USAGE_COPY_BRANCH
            * `usage/open_search` - USAGE_OPEN_SEARCH
            * `usage/nlp_raw_create` - USAGE_NLP_RAW_CREATE
            * `usage/nlp_raw_delete` - USAGE_NLP_RAW_DELETE
            * `usage/nlp_typeahead_open` - USAGE_NLP_TYPEAHEAD_OPEN
            * `usage/nlp_typeahead_accept` - USAGE_NLP_TYPEAHEAD_ACCEPT
            * `agents/requested` - AGENT_REQUESTED
            * `agents/started` - AGENT_STARTED
            * `agents/check_in` - AGENT_CHECK_IN
            * `agents/succeeded` - AGENT_SUCCEEDED
            * `agents/failed` - AGENT_FAILED
            * `agents/webhook_received` - AGENT_WEBHOOK_RECEIVED
            * `chats/message_received` - CHAT_MESSAGE_RECEIVED
        url (str): The URL to call when the workflow is triggered.
        headers (Union[Unset, AgentWorkflowHeaders]): Headers to include with the workflow request.
        body (Union[Unset, str]): The JSON body template for the workflow request.
        response_key (Union[Unset, str]): The JSON response key to use as the agent's comment.
    """

    id: str
    trigger: EventKind
    url: str
    headers: Union[Unset, "AgentWorkflowHeaders"] = UNSET
    body: Union[Unset, str] = UNSET
    response_key: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        trigger = self.trigger.value

        url = self.url

        headers: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        body = self.body

        response_key = self.response_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "trigger": trigger,
                "url": url,
            }
        )
        if headers is not UNSET:
            field_dict["headers"] = headers
        if body is not UNSET:
            field_dict["body"] = body
        if response_key is not UNSET:
            field_dict["responseKey"] = response_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_workflow_headers import AgentWorkflowHeaders

        d = dict(src_dict)
        id = d.pop("id")

        trigger = EventKind(d.pop("trigger"))

        url = d.pop("url")

        _headers = d.pop("headers", UNSET)
        headers: Union[Unset, AgentWorkflowHeaders]
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = AgentWorkflowHeaders.from_dict(_headers)

        body = d.pop("body", UNSET)

        response_key = d.pop("responseKey", UNSET)

        agent_workflow = cls(
            id=id,
            trigger=trigger,
            url=url,
            headers=headers,
            body=body,
            response_key=response_key,
        )

        agent_workflow.additional_properties = d
        return agent_workflow

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
