# Python Notion API

<img src="./img/logo.webp" alt="Logo" width="100"/>

Yet another client for Python Notion API...

which brings you:

    * Async calls allowing you to send multiple requests at once
    * Pydantic models that wrap pages and databases for simple use

## Quick start

```python
from python_notion_api import NotionAPI

api = NotionAPI(
    access_token='<NOTION_TOKEN>'
)
```

or

```python
from python_notion_api import AsyncNotionAPI

async_api = AsyncNotionAPI(
    access_token='<NOTION_TOKEN>'
)
```

## Notion Database

### Retrieve a database

```python
database = api.get_database(database_id='<DATABASE_ID>')
```

or

```python
async def main():
    database = await async_api.get_database(database_id='<DATABASE_ID>')
```

### Query

```python
database = api.get_database(database_id='<DATABASE_ID>')

for page in database.query():
    ...
```

or

```python
async def main():
    database = await async_api.get_database(database_id='<DATABASE_ID>')

    async for page in database.query():
        ...
```

### Filters

You can use filter classes in `python_notion_api.models.filters` to create property filters and pass them to the query.

```python
from python_notion_api.models.filters import SelectFilter

for page in database.query(
    filters=SelectFilter(property='<PROPERTY_NAME / PROPERTY_ID>', equals='<VALUE>')
)
```

Timestamp, 'and' and 'or' filters are supported:

```python
from python_notion_api.models.filters import SelectFilter, NumberFilter, CheckboxFilter
from python_notion_api.models.filters import and_filter, or_filter

for page in database.query(
    filters=or_filter([
        SelectFilter(property="Select", equals="xxx"),
        and_filter([
            NumberFilter(property="Number", greater_than=10),
            CheckboxFilter(property="Checkbox", equals=True)
        ])
    ])
)
```

You can read more on filters [here](https://developers.notion.com/reference/post-database-query-filter)

### Sorts

You can use `python_notion_api.models.sorts.Sort` class to create sorts and pass them to the query.

```python
from python_notion_api.models.sorts import Sort

for page in database.query(
    sorts=[
        Sort(property="Title"),
        Sort(property="Date", descending=True)
    ]
)
```

## Pages

### Retrieve a page

```python
page = api.get_page(page_id='<PAGE_ID>')
```

or

```python
async def main():
    page = await async_api.get_page(page_id='<PAGE_ID>')
```

### Create a page

```python
database = api.get_database(database_id='<DATABASE_ID>')

database.create_page(properties={
    'Number_property': 234,
    'Select_property': 'select1',
    'Checkbox_property': True,
    'Relation_property': ['<PAGE_ID>']
})
```

### Update page

```python
page = api.get_page(page_id='<PAGE_ID>')

page.set('Number_property', 234)

page.update(properties={'Select_property': 'select1', 'Checkbox_property': True})
```

### Archive page

```python
page = api.get_page(page_id='<PAGE_ID>')

page.alive = False

page.alive = True
```
or

```python

async def main():
    page = await async_api.get_page(page_id='<PAGE_ID>')

    await page.archive()

    print(page.is_alive)

    await page.unarchive()
```

### Retrieve a single page property item

```python
page.get('Property name').value
page.get('Relation property').value

for value in page.get('Relation property'):
    print(value)
```

### Retrieve page blocks


```python
blocks = page.get_blocks()

for block in blocks:
    print(block.block_type)
```

### Custom page properties
In some cases, we may not want the values directly returned by the API.
In particular, the values of rollups and formulas may be incorrect when retrieved through the API, but we can calculate the correct value by recreating the formulas and rollups in Python code.

To use custom page properties, create a subclass of NotionPage. Define a function to get each custom property (these must return a `PropertyValue`) and define the mapping from Notion property names to the function names.

```python
from python_notion_api.api import NotionPage
from python_notion_api.models import RichTextObject
from python_notion_api.models.values import RichTextPropertyValue

class MyPage(NotionPage):
    # Use this dictionary to map the property names to functions
    # Being explicit about the mapping so we don't restrict the property names in Notion
    special_properties = {
        'Value': 'special_value'
    }


    def special_value(self) -> RichTextPropertyItem:

        # self.get('Value') would just loop back here,
        # so use self._direct_get to retrieve the value returned by the API
        x = self._direct_get('Value').value

        # Then do whatever processing is required
        # Should return a PropertyValue to be compatible with downstream functions
        if x == 1:
            return RichTextPropertyValue(rich_text=RichTextObject(
                plain_text='One', type='text'))
        else:
            return RichTextPropertyValue(rich_text=RichTextObject(
                plain_text='Number unknown', type='text'))

```

This page class can be passed when querying a database or getting a page.

```python
page = api.get_page(page_id='<PAGE_ID>',
                    cast_cls=MyPage)


for page in database.query(cast_cls=MyPage, filters=NumberFilter(property='Value', equals=1)):
    print('Custom processing:', page.get('Value').value)
    print('Raw value:', page._direct_get('Value').value)
    break

## output
# Custom processing: One
# Raw value: 1.0

```

## Blocks

### Retrieve a block

```python
block = api.get_block(block_id='<BLOCK_ID>')
```

### Get and add block children

```python
p = ParagraphBlock(
    rich_text=[RichTextObject.from_str("Some text to add through API")]
)
block.add_child_block(content=[p])


child_blocks = block.get_child_blocks()
```

### Update a block

All values must be updated at once.

```python
from python_notion_api.models.blocks import ParagraphBlock, ParagraphBlockValue, RichTextObject

# Make new block with updated values
new_block = ParagraphBlock.from_obj({'object': 'block',
 'type': 'paragraph',
 'paragraph': {'rich_text': [
     {'plain_text': 'Text here not used for some reason', 'type': 'text',
     'text': {'content': 'This is the text that will be added', 'link': None}}]}
})

block = api.get_block(block_id='<BLOCK_ID>')
block.set(new_block)
```
