## Retrieve a page

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        page = await async_api.get_page(page_id='<PAGE_ID>')
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    page = api.get_page(page_id='<PAGE_ID>')
    ```

## Create a page

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        database = await async_api.get_database(database_id='<DATABASE_ID>')

        await database.create_page(properties={
            'Number_property': 234,
            'Select_property': 'select1',
            'Checkbox_property': True,
            'Relation_property': ['<PAGE_ID>']
        })
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    database = api.get_database(database_id='<DATABASE_ID>')

    database.create_page(properties={
        'Number_property': 234,
        'Select_property': 'select1',
        'Checkbox_property': True,
        'Relation_property': ['<PAGE_ID>']
    })
    ```

## Update page

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        page = await async_api.get_page(page_id='<PAGE_ID>')

        await page.set('Number_property', 234)
        await page.update(properties={'Select_property': 'select1', 'Checkbox_property': True})
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    page = api.get_page(page_id='<PAGE_ID>')

    page.set('Number_property', 234)

    page.update(properties={'Select_property': 'select1', 'Checkbox_property': True})
    ```

## Archive page

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        page = await async_api.get_page(page_id='<PAGE_ID>')

        await page.archive()

        print(page.is_alive)

        await page.unarchive()
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    page = api.get_page(page_id='<PAGE_ID>')

    page.alive = False

    page.alive = True
    ```

## Retrieve a single page property item

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        page = await async_api.get_page(page_id='<PAGE_ID>')

        await page.get('Property name').value
        await for value in page.get('Relation property'):
            print(value)
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    page = api.get_page(page_id='<PAGE_ID>')

    page.get('Property name').value

    for value in page.get('Relation property'):
        print(value)
    ```

## Custom pages
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
```
