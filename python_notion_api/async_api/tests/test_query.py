import asyncio
import os

from python_notion_api.async_api.api import AsyncNotionAPI


async def main():
    api = AsyncNotionAPI(access_token=os.environ["NOTION_TOKEN"])

    db = await api.get_data_source(
        data_source_id="2cef2075b1dc80bab834000b42b068d7")

    async for page in db.query():
        print(await page.get("title"))


if __name__ == "__main__":
    asyncio.run(main())
