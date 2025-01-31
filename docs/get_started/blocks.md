## Retrieve a block

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        block = await async_api.get_block(block_id='<BLOCK_ID>')
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    block = api.get_block(block_id='<BLOCK_ID>')
    ```

## Retrieve page blocks

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        page = await async_api.get_page(page_id='<PAGE_ID>')
        await for block in page.get_blocks():
            ...
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    page = api.get_page(page_id='<PAGE_ID>')

    blocks = page.get_blocks()

    for block in blocks:
        ...
    ```

## Get and add block children


=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        block = await async_api.get_block(block_id='<BLOCK_ID>')

        p = ParagraphBlock(
            rich_text=[RichTextObject.from_str("Some text to add through API")]
        )
        await block.add_child_block(content=[p])

        block = await block.get_children_block()
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    block = api.get_block(block_id='<BLOCK_ID>')

    p = ParagraphBlock(
        rich_text=[RichTextObject.from_str("Some text to add through API")]
    )
    block.add_child_block(content=[p])

    child_blocks = block.get_child_blocks()
    ```

## Update a block

All values must be updated at once.

=== "Async"

    ```python
    from python_notion_api.models.blocks import ParagraphBlock

    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        block = await async_api.get_block(block_id='<BLOCK_ID>')

        new_block = ParagraphBlock.from_obj({'object': 'block',
        'type': 'paragraph',
        'paragraph': {'rich_text': [
            {'plain_text': 'Text here not used for some reason', 'type': 'text',
            'text': {'content': 'This is the text that will be added', 'link': None}}]}
        })

        await block.set(new_block)
    ```

=== "Sync"


    ```python
    from python_notion_api.models.blocks import ParagraphBlock

    api = NotionAPI(access_token='<NOTION_TOKEN>')
    block = api.get_block(block_id='<BLOCK_ID>')

    new_block = ParagraphBlock.from_obj({'object': 'block',
    'type': 'paragraph',
    'paragraph': {'rich_text': [
        {'plain_text': 'Text here not used for some reason', 'type': 'text',
        'text': {'content': 'This is the text that will be added', 'link': None}}]}
    })

    block = api.get_block(block_id='<BLOCK_ID>')
    block.set(new_block)
    ```
