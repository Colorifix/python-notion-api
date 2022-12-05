# A Python implementation of the Notion API

Object oriented API wrapper that uses Pydantic to convert Notion objects to Python objects and viceversa.

Current alternatives are:

- Client library for the official API, at the moment it doesn't resolve the objects to classes:
https://github.com/ramnes/notion-sdk-py
- Unofficial Python 3 client for Notion.so API v3, it doesn't use the official Notion API.
https://github.com/jamalex/notion-py

## Quick start

```python
from python_notion_api import NotionAPI

api = NotionAPI(
    access_token='secret_token'
)
```

## Notion Database

### Retrieve a database

```python
from python_notion_api import NotionAPI

api = NotionAPI(
    access_token='secret_token'
)

database = api.get_database(database_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
```

Returns a `NotionDatabase` object.

### Query

```python
from python_notion_api import NotionAPI

api = NotionAPI(
    access_token='secret_token'
)

database = api.get_database(database_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

for page in database.query():
    ...
```

Allows you to iterate over all pages in the database.

### Filters

You can use filter classes in `python_notion_api.models.filters` to create property filters and pass them to the query.

```python
from python_notion_api.models.filters import SelectFilter

res = database.query(
    filters=SelectFilter(property="Property Name", equals="xxx")
)
```

Timestamp, 'and' and 'or' filters are supported:

```python
from python_notion_api.models.filters import SelectFilter, NumberFilter, CheckboxFilter
from python_notion_api.models.filters import and_filter, or_filter

res = database.query(
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

res = database.query(
    sorts=[
        Sort(property="Title"),
        Sort(property="Date", descending=True)
    ]
)
```

## Pages

### Retrieve a page

```python
page = api.get_page(page_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
```

Will return a `NotionPage` object.

### Create a page

```python
from python_notion_api import NotionAPI

api = NotionAPI(
    access_token='secret_token'
)

database = api.get_database(database_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

database.create_page(
    properties={
        "Title": "New page"
    }
)
```

The properties of the new page are set using a dictionary with the column name as the key and the new property as the value. The value can be set with either the raw value (as a string, a number, or a datetime) or with a class from `python_notion_api.models.common` for storing the object (e.g. `DateObject`,  `SelectObject`, `RichTextObject`, `TextObject`).
E.g.

```python
database = api.get_database(database_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

database.create_page(properties={
    'Value': 234, 
    'Select_property': 'select1',
    'Checkbox_property': True,
    'Relation_property': ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx']
})
```

### Update page

Currently only supported for inividual properties.

You can create a page in a database and set the properties of the new page. Formuas are not supported.

```python
page = api.get_page(page_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

page.set('Property name', 'new value')
```

### Retrieve a page property item

When getting a property through `page.get` or `page.properties` the return type will
be either `PropertyValue` or `PropertyItemIterator` (for properties that can have multple values, i.e. relations, title, rich_text and people)

Each property type is wrapped into it's own class defined in `api.models.properties`. To get a human-readable 'simple' value that represents the propery, you can use `PropertyValue.value` attribute. To get a list of all property items values from `PropertyItemIterator` you can use
`PropertyItemIterator.value`. For rich_text and title property types `value` will return a concatenaded string.

```python
page.get('Property name').value
page.get('Relation property').value

for value in page.get('Relation property'):
    print(value)
```

### Retrieve page blocks

Each block type has its own class in `models.blocks`.

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
page = api.get_page(page_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 
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
block = api.get_block(block_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
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

block = api.get_block(block_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
block.set(new_block)
```

## Problems with rollups and formulas
These can only reference values 1 level deep. For any deeper reference, for example A references B which references C, the returned value will likely be incorrect. 
There is no error or warning when this occurs, so be careful!  

A subclass of NotionPage can be used to fully recreate rollups and formulas (see above).  

## File upload
The official Notion API doesn't yet support uploading files. As an alternative, it is possible to upload files to GDrive and use the 
link in a column of type File.

To configure it, set the env variable `GDRIVE_CONF` to the location of a json configuration file with the following structure:

```json
'GDRIVE': {
    'CLIENT_CONFIG_FILE': 'path_to_oauth_config_file'
    'CREDENTIALS': 'path_to_oauth_credentials_file',
    'SHARED_DRIVE': 'id_of_shared_drive_to_use',
}
```

Example:

```python
from python_notion_api import NotionAPI
from python_notion_api.models.common import File

api = NotionAPI(access_token='secret_token')
page = api.get_page(page_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
page.set('File Property', [File.from_file_path(file_path=file_path)])
```

## Requirements

This library requires `Python >= 3.7`. For full list of requirements, see the `pyproject.toml` file.
