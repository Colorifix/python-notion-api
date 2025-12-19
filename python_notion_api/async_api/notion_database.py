from typing import TYPE_CHECKING, List

from python_notion_api.async_api.utils import ensure_loaded
from python_notion_api.models.common import DataSourceObject
from python_notion_api.models.objects import Database

if TYPE_CHECKING:
    from python_notion_api.async_api.api import AsyncNotionAPI


class NotionDatabase:
    """Wrapper for a Notion database object.

    Args:
        api: Instance of the NotionAPI.
        database_id: Id of the database.
    """

    def __init__(self, api: "AsyncNotionAPI", database_id: str):
        self._api = api
        self._database_id = database_id
        self._object = None
        self._data_sources = None
        self._title = None

    @ensure_loaded
    def __getattr__(self, attr_key):
        return getattr(self._object, attr_key)

    @property
    def database_id(self) -> str:
        """Gets the database id."""
        return self._database_id.replace("-", "")

    @property
    @ensure_loaded
    def title(self) -> str:
        """Gets title of the database."""
        assert self._title is not None
        return self._title

    @property
    @ensure_loaded
    def data_sources(self) -> List[DataSourceObject]:
        """Gets all data sources of the database."""
        return self._data_sources

    async def reload(self):
        self._object = await self._api._get(
            endpoint=f"databases/{self._database_id}",
            cast_cls=Database,
        )

        if self._object is None:
            raise Exception(f"Error loading database {self._database_id}")

        self._data_sources = [
            DataSourceObject(**val) for val in self._object.data_sources
        ]
        self._title = "".join(rt.plain_text for rt in self._object.title)
