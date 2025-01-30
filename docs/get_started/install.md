Python Notion API is available at PyPI under `python-notion-api`.

For example, if you are using `pip`, you can install it with

```console
$ pip install python-notion-api
```

You can now import the project and initialise the client by passing your token. We recommend using the Async version for extra super-powers.

=== "Async"

    ```python
    from python_notion_api import AsyncNotionAPI

    async_api = AsyncNotionAPI(access_token='<NOTION_TOKEN>')
    ```

=== "Sync"

    ```python
    from python_notion_api import NotionAPI

    api = NotionAPI(access_token='<NOTION_TOKEN>')
    ```

!!! info
    If you are not sure how to get your token, check out [this](https://www.notion.com/help/create-integrations-with-the-notion-api){:target="_blank"} article
