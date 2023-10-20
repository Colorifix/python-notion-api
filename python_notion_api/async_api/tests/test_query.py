import os
from python_notion_api.async_api import AsyncNotionAPI

import asyncio


async def main():
    api = AsyncNotionAPI(access_token=os.environ["NOTION_TOKEN"])

    db = await api.get_database(database_id="c0802577c79645e5af855f0ca46148b2")

    async for page in db.query():
        print(await page.get('title'))

if __name__ == "__main__":
    asyncio.run(main())
