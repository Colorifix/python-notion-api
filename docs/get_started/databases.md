## Retrieve a database

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        database = await async_api.get_database(database_id='<DATABASE_ID>')
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    database = api.get_database(database_id='<DATABASE_ID>')
    ```

## Query

=== "Async"

    ```python
    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        database = await async_api.get_database(database_id='<DATABASE_ID>')

        async for page in database.query():
            ...
    ```

=== "Sync"

    ```python
    api = NotionAPI(access_token='<NOTION_TOKEN>')
    database = api.get_database(database_id='<DATABASE_ID>')

    for page in database.query():
        ...
    ```

### Filters

You can use filter classes in `python_notion_api.models.filters` to create property filters and pass them to the query.

=== "Async"

    ```python
    from python_notion_api.models.filters import SelectFilter

    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        database = await async_api.get_database(database_id='<DATABASE_ID>')

        await for page in database.query(
            filters=SelectFilter(property='<PROPERTY_NAME / PROPERTY_ID>', equals='<VALUE>')
        ):
            ...
    ```

=== "Sync"

    ```python
    from python_notion_api.models.filters import SelectFilter

    api = NotionAPI(access_token='<NOTION_TOKEN>')
    database = api.get_database(database_id='<DATABASE_ID>')

    for page in database.query(
        filters=SelectFilter(property='<PROPERTY_NAME / PROPERTY_ID>', equals='<VALUE>')
    ):
        ...
    ```

'and' and 'or' filters are supported:

=== "Async"

    ```python
    from python_notion_api.models.filters import SelectFilter, or_filter, and_filter

    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        database = await async_api.get_database(database_id='<DATABASE_ID>')

        await for page in database.query(
            filters=or_filter([
                SelectFilter(property="Select", equals="xxx"),
                and_filter([
                    NumberFilter(property="Number", greater_than=10),
                    CheckboxFilter(property="Checkbox", equals=True)
                ])
            ])
        ):
            ...
    ```

=== "Sync"

    ```python
    from python_notion_api.models.filters import SelectFilter, or_filter, and_filter

    api = NotionAPI(access_token='<NOTION_TOKEN>')
    database = api.get_database(database_id='<DATABASE_ID>')

    for page in database.query(
        filters=or_filter([
            SelectFilter(property="Select", equals="xxx"),
            and_filter([
                NumberFilter(property="Number", greater_than=10),
                CheckboxFilter(property="Checkbox", equals=True)
            ])
        ])
    )
        ...
    ```

You can read more on filters [here](https://developers.notion.com/reference/post-database-query-filter){:target="_blank"}

### Sorts

You can use `python_notion_api.models.sorts.Sort` class to create sorts and pass them to the query.

=== "Async"

    ```python
    from python_notion_api.models.sorts import Sort

    async def main():
        async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
        database = await async_api.get_database(database_id='<DATABASE_ID>')

        await for page in database.query(
            sorts=[
                Sort(property="Title"),
                Sort(property="Date", descending=True)
            ]
        ):
    ```

=== "Sync"

    ```python
    from python_notion_api.models.sorts import Sort

    api = NotionAPI(access_token='<NOTION_TOKEN>')
    database = api.get_database(database_id='<DATABASE_ID>')

    for page in database.query(
        sorts=[
            Sort(property="Title"),
            Sort(property="Date", descending=True)
        ]
    )
    ```
