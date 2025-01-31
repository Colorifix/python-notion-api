from typing import TYPE_CHECKING, List

from pydantic.v1 import BaseModel

from python_notion_api.async_api.iterators import AsyncBlockIterator
from python_notion_api.async_api.utils import ensure_loaded
from python_notion_api.models.objects import Block

if TYPE_CHECKING:
    from python_notion_api.async_api.api import AsyncNotionAPI


class NotionBlock:
    """Wrapper for a Notion block object

    Args:
        api: Instance of the NotionAPI.
        block_id: Id of the block.
    """

    def __init__(self, api: "AsyncNotionAPI", block_id: str):
        self._api = api
        self._block_id = block_id
        self._object = None

    async def reload(self):
        """Reloads the block from Notion."""
        self._object = await self._api._get(endpoint=f"blocks/{self.block_id}")

    class AddChildrenRequest(BaseModel):
        children: List[Block]

    @ensure_loaded
    def __getattr__(self, attr_key):
        return getattr(self._object, attr_key)

    @property
    def block_id(self) -> str:
        """Gets the block id."""
        return self._block_id.replace("-", "")

    async def get_child_blocks(self) -> AsyncBlockIterator:
        """Gets all children blocks.

        Returns:
            An iterator of all children blocks in the block.
        """
        generator = await self._api._get_iterate(
            endpoint=f"blocks/{self._block_id}/children"
        )
        return AsyncBlockIterator(generator)

    async def add_child_block(
        self, content: List[Block], reload_block: bool = False
    ) -> AsyncBlockIterator:
        """Adds new blocks as children.

        Args:
            content: Content of the new block.

        Returns:
            An iterator of the newly created blocks.
        """

        request = NotionBlock.AddChildrenRequest(children=content)

        data = request.json(
            by_alias=True, exclude_unset=True, exclude_none=True
        )

        new_blocks = await self._api._patch(
            endpoint=f"blocks/{self.block_id}/children", data=data
        )

        if reload_block:
            await self.reload()

        return AsyncBlockIterator(iter(new_blocks.results))

    async def set(self, block: Block, reload_block: bool = False) -> Block:
        """Updates the content of a Block.

        The entire content is replaced.

        Args:
            block: Block with the new values.

        Returns:
            The updated block.
        """

        data = block.patch_json()

        new_block = await self._api._patch(
            endpoint=f"blocks/{self.block_id}", data=data
        )

        if reload_block:
            await self.reload()

        return new_block
