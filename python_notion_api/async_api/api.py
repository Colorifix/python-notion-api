from typing import Literal, Dict, Any, Optional, Type, Generator

from math import floor

import json
import aiohttp
import asyncio

from loguru import logger


from python_notion_api.models.objects import (
    NotionObjectBase, User
)

from python_notion_api.models.properties import NotionObject

from python_notion_api.async_api.retry_strategy import RetryStrategy
from python_notion_api.async_api import NotionBlock, NotionPage, NotionDatabase


NotionObjectGenerator = Generator[NotionObject, None, None]


class MaxRetryError(Exception):
    pass


class AsyncNotionAPI:
    """Main class for Notion API wrapper.

    Args:
        access_token: Notion access token
        api_version: Version of the notion API
    """

    def __init__(
        self,
        access_token: str,
        api_version='2022-06-28',
        page_limit=20
    ):
        self._access_token = access_token
        self._base_url = "https://api.notion.com/v1/"
        self._api_version = api_version
        self._default_retry_strategy = RetryStrategy(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self._page_limit = page_limit

    @property
    def request_headers(self):
        return {
            'Authorization': f'Bearer {self._access_token}',
            'Notion-Version': f'{self._api_version}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    async def get_database(self, database_id: str) -> NotionDatabase:
        """ Wrapper for 'Retrieve a database' action.

        Args:
            database_id: Id of the database to fetch.
        """
        database = NotionDatabase(self, database_id)
        await database.reload()

        return database

    async def get_page(self, page_id, page_cast=NotionPage) -> NotionPage:
        """ Wrapper for 'Retrieve a dpage' action.

        Args:
            page_id: Id of the database to fetch.
            page_cast: A subclass of a NotionPage. Allows custom
            property retrieval
        """
        page = page_cast(api=self, page_id=page_id)
        await page.reload()

        return page

    async def get_block(self, block_id) -> NotionBlock:
        """ Wrapper for 'Retrieve a block' action.

        Args:
            block_id: Id of the block to fetch.
        """
        block = NotionBlock(self, block_id)
        await block.reload()

        return block

    async def me(self) -> User:
        return await self._get("users/me")

    async def _request_attempt(
            self,
            session: aiohttp.ClientSession,
            request_type: Literal['get', 'post', 'patch'],
            url: str = '',
            params: Dict[str, Any] = {},
            data: Optional[str] = None,
    ):
        """Attempt a request to url.

        Args:
            url: URL for the request.
            request_type: Type of the http request to make.
            data: Data to pass to the request.
            params: Params to pass to the request.
        """
        return await session.request(
            method=request_type,
            url=url,
            headers=self.request_headers,
            params=params,
            data=data
        )

    async def _request(
            self, request_type: Literal['get', 'post', 'patch'],
            endpoint: str = '',
            params: Dict[str, Any] = {},
            data: Optional[str] = None,
            cast_cls: Type[NotionObjectBase] = NotionObject,
            retry_strategy: Optional[RetryStrategy] = None
            ) -> Optional[NotionObject]:
        """Main request handler.

        Should not be called directly, for internal use only.

        Args:
            request_type: Type of the http request to make.
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            params: Params to pass to the request.
            data: Data to pass to the request.
            params: Params to pass to the request.
            cast_cls: A NotionObjectBase class to auto-cast the response of the
                request to.
        """
        retry_strategy = retry_strategy or self._default_retry_strategy

        url = self._base_url + endpoint

        logger.debug(f"Sending {request_type} request to {url}")

        response = None

        async with aiohttp.ClientSession() as session:
            for i in range(retry_strategy.total):
                response = await self._request_attempt(
                    request_type=request_type,
                    session=session,
                    url=url,
                    params=params,
                    data=data
                )

                response_data = await response.read()
                decoded_data = response_data.decode("utf-8")

                if response.status == 200:
                    return cast_cls.from_obj(json.loads(decoded_data))

                elif response.status not in retry_strategy.status_forcelist:
                    logger.error(
                        f"Request to {url} failed:"
                        f"\n{response.status}\n{decoded_data}"
                    )
                    raise Exception('Request failed')

                delay = min(
                    retry_strategy.backoff_factor * (2 ** (i)),
                    retry_strategy.max_backoff
                )

                logger.error(
                    f"Notion is busy ({response.status})."
                    f"Retrying ({i+1}) in {delay}s"
                )
                await asyncio.sleep(delay)

        logger.warning(
            f"Request failed after {retry_strategy.total}"
            " attempts."
        )
        raise MaxRetryError('Request failed')

    async def _post(
        self,
        endpoint: str,
        data: Optional[str] = None,
        cast_cls: Type[NotionObjectBase] = NotionObject,
        retry_strategy: Any = None
      ) -> Optional[NotionObject]:
        """Wrapper for post requests.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            data: Data to pass to the request.
            cast_cls: A NotionObjectBase class to auto-cast the response of the
                request to.
        """
        return await self._request(
            request_type='post',
            endpoint=endpoint,
            data=data,
            cast_cls=cast_cls,
            retry_strategy=retry_strategy
        )

    async def _get(
        self,
        endpoint: str,
        params: Dict[str, str] = {},
        cast_cls: Type[NotionObjectBase] = NotionObject
    ) -> Optional[NotionObject]:
        """Wrapper for post requests.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            params: Params to pass to the request.
            cast_cls: A NotionObjectBase class to auto-cast the response of the
                request to.
        """
        return await self._request(
            request_type='get',
            endpoint=endpoint,
            params=params,
            cast_cls=cast_cls,
        )

    async def _patch(
        self,
        endpoint: str,
        params: Dict[str, str] = {},
        data: Optional[str] = None,
        cast_cls=NotionObject
    ) -> NotionObject:
        """Wrapper for patch requests.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            params: Params to pass to the request.
            data: Data to pass to the request.
            cast_cls: A NotionObjectBase class to auto-cast the response of the
                request to.
        """
        return await self._request(
            request_type='patch',
            endpoint=endpoint,
            params=params,
            data=data,
            cast_cls=cast_cls
        )

    async def _post_iterate(
        self, endpoint: str,
        data: Dict[str, str] = {},
        page_limit: int = None
    ) -> NotionObjectGenerator:
        """Wrapper for post requests where expected return type is Pagination.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            data: Data to pass to the request.
        """
        has_more = True
        cursor = None
        page_size = page_limit or self._page_limit

        while has_more:
            data.update({
                'start_cursor': cursor,
                'page_size': page_size
            })

            if cursor is None:
                data.pop('start_cursor')

            while page_size > 0:
                try:
                    response = await self._post(
                        endpoint=endpoint,
                        data=json.dumps(data)
                    )

                    for item in response.results:
                        yield item

                    has_more = response.has_more
                    cursor = response.next_cursor

                    break
                except MaxRetryError as e:
                    page_size = floor(page_size/2)
                    logger.warning(
                        f"Retrying request with smaller page size({page_size})"
                    )
                    if page_size == 0:
                        raise e
                    data.update({
                        'page_size': page_size
                    })

    async def _get_iterate(
        self,
        endpoint: str,
        params: Dict[str, str] = {},
        page_limit: int = None
    ) -> NotionObjectGenerator:
        """Wrapper for get requests where expected return type is Pagination.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            params: Params to pass to the request.
        """
        has_more = True
        cursor = None
        page_size = page_limit or self._page_limit

        while has_more:
            params.update({
                'start_cursor': cursor,
                'page_size': page_size
            })

            if cursor is None:
                params.pop('start_cursor')

            while page_size > 0:
                try:
                    response = await self._get(
                        endpoint=endpoint,
                        params=params
                    )

                    if hasattr(response, 'property_item'):
                        # Required for rollups
                        property_item = response.property_item
                    else:
                        # property doesn't exist for Blocks
                        property_item = None

                    for item in response.results:
                        yield item, property_item

                    has_more = response.has_more
                    cursor = response.next_cursor

                    break
                except MaxRetryError as e:
                    page_size = floor(page_size/2)
                    logger.warning(
                        f"Retrying request with smaller page size({page_size})"
                    )
                    if page_size == 0:
                        raise e
                    params.update({
                        'page_size': page_size
                    })
