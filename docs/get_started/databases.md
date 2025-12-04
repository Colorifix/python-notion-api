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
