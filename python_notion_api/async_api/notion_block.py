from typing import List

from pydantic import BaseModel

from python_notion_api.async_api.iterators import AsyncBlockIterator
from python_notion_api.async_api.utils import ensure_loaded
from python_notion_api.models.objects import Block


class NotionBlock:
    """wrapper for notion block object

    Args:
        api: Instance of the NotionAPI.
        block_id: Id of the block.
    """

    def __init__(self, api, block_id):
        self._api = api
        self._block_id = block_id
        self._object = None

    async def reload(self):
        self._object = await self._api._get(endpoint=f"blocks/{self.block_id}")

    class AddChildrenRequest(BaseModel):
        children: List[Block]

    @ensure_loaded
    def __getattr__(self, attr_key):
        return getattr(self._object, attr_key)

    @property
    def block_id(self) -> str:
        return self._block_id.replace("-", "")

    async def get_child_blocks(self) -> AsyncBlockIterator:
        """
        Get an iterater of all blocks in the block
        Returns:

        """
        generator = await self._api._get_iterate(
            endpoint=f"blocks/{self._block_id}/children"
        )
        return AsyncBlockIterator(generator)

    async def add_child_block(
        self, content: List[Block], reload_block: bool = False
    ) -> AsyncBlockIterator:
        """Wrapper for add new blocks to an existing page.

        Args:
            content: Content of the new block.
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
        """
        Updates the content of a Block. The entire content is replaced.
        Args:
            block: Block with the new values.
        """

        data = block.patch_json()

        new_block = await self._api._patch(
            endpoint=f"blocks/{self.block_id}", data=data
        )

        if reload_block:
            await self.reload()

        return new_block
