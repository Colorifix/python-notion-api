# A Python implementation of the Notion API

## Quick start

```python
api = NotionAPI(
    access_token='secret_token'
)
```

## Notion Database

Currently only **Retrieve a database** action is fully supported. Querying is
supported, with filtering and sorting.

For filtering and sorting the input json object can be of [this format](https://developers.notion.com/reference/post-database-query-filter) for filtering and [this format](https://developers.notion.com/reference/post-database-query-sort) for sorting.

The is a `create_filter` method available in the NotionDatabase class for generating the correct filter format. Not all property formats are yet supported. Multiple properties will result in an AND filter. OR filters are not supported.

Filter properties are set such that the column name as the key and the set of query type and property as the value. Example below:

```python
database = api.get_database(database_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

sort_filter = database.create_filter(
    properties={
        "Value": ("equals", 12),
        "Select_property": ("equals", "select1"),
        "Name": ("contains", "Test")
    }
)

for page in database.query(sort_filter):
    ...
```

You can create a page in a database and set the properties of the new page. Not all property types are currently supported (files, status, rollups are not supported). 

The properties of the new page are set using a dictionary with the column name as the key and the new property as the value. The value can be set with either the raw value (as a string, a number, or a datatime), with a class from `notion_integration.api.models` for storing that value (e.g. `DatePropertyValue`,  `SelectValue`, `User`, `RichTextObject`), or with a `PropertyItem` or `PropertyItemIterator` class.  
E.g.

```python
database = api.get_database(database_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

database.create_page(properties={
    'Value': 234, 
    'Select_property': SelectValue(name='select1'),
    'Checkbox_property': CheckBoxPropertyItem(checkbox=True)
})
```

## Notion page

The following actions are supported for pages:

* Retrieve a page
* Retrieve a page property item
* Update page (limited to updating one property at a time)

```python
page = api.get_page(page_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

page.get('Property name')
page.set('Property name', 'new value')

page.to_dict()
page.properties
```

## Property items

When getting a property through `page.get` or `page.properties` the return type will
be either `PropertyItem` or `PropertyItemIterator` (for properties that can have multple values, i.e. relations, title, rich_text and people)

Each property type is wrapped into it's own class defined in `api.models.properties`. To get a human-readable 'simple' value that represents the propery, you can use `PropertyItem.value` attribute. To get a list of all property items values from `PropertyItemIterator` you can use
`PropertyItemIterator.all()`. For rich_text and title property types `.all()` will return a concatenaded string.

```python
page.get('Prroperty name').value
page.get('Relation property').all()

for value in page.get('Relation property'):
    print(value)
```

## Problems with rollups and formulas
These can only reference values 1 level deep. For any deeper reference, for example A references B which references C, the returned value will likely be incorrect. 
There is no error or warning when this occurs, so be careful!