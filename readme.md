# A Python implementation of the Notion API

## Quick start

```python
from api import NotionAPI

api = NotionAPI(
    access_token='secret_token'
)
```

## Notion Database

### Retrieve a database

```python
from api import NotionAPI

api = NotionAPI(
    access_token='secret_token'
)

database = api.get_database(database_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
```

Returns a `NotionDatabase` object.

### Query

```python
from api import NotionAPI

api = NotionAPI(
    access_token='secret_token'
)

database = api.get_database(database_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

for page in database.query():
    ...
```

Allows you to iterate over all pages in the database.

### Filters

You can use filter classes in `api.models.filters` to create property filters and pass them to the query.

```python
from api.models.filters import SelectFilter

res = database.query(
    filters=SelectFilter(property="Property Name", equals="xxx")
)
```

Timestamp, 'and' and 'or' filters are supported:

```python
from api.models.filters import SelectFilter, NumberFilter, CheckboxFilter
from api.models.filters import and_filter, or_filter

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

You can use `api.models.sorts.Sort` class to create sorts and pass them to the query.

```python
from api.models.sorts import Sort

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
from api import NotionAPI

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

### Update page

Currently only supported for inividual properties.

You can create a page in a database and set the properties of the new page. Not all property types are currently supported (files, status, rollups are not supported). 

```python
page = api.get_page(page_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

page.set('Property name', 'new value')
```

### Retrieve a page property item


When getting a property through `page.get` or `page.properties` the return type will
be either `PropertyItem` or `PropertyItemIterator` (for properties that can have multple values, i.e. relations, title, rich_text and people)

Each property type is wrapped into it's own class defined in `api.models.properties`. To get a human-readable 'simple' value that represents the propery, you can use `PropertyItem.value` attribute. To get a list of all property items values from `PropertyItemIterator` you can use
`PropertyItemIterator.value`. For rich_text and title property types `value` will return a concatenaded string.

```python
page.get('Prroperty name').value
page.get('Relation property').all()

for value in page.get('Relation property'):
    print(value)
```

## Problems with rollups and formulas
These can only reference values 1 level deep. For any deeper reference, for example A references B which references C, the returned value will likely be incorrect. 
There is no error or warning when this occurs, so be careful!