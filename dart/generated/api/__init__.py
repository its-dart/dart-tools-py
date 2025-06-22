"""Contains methods for accessing the API"""

from .comment import create_comment, list_comments
from .config import get_config
from .dartboard import retrieve_dartboard
from .doc import create_doc, delete_doc, list_docs, retrieve_doc, update_doc
from .folder import retrieve_folder
from .task import create_task, delete_task, list_tasks, retrieve_task, update_task
from .view import retrieve_view
