import asyncio
from redis_client import create_redis_client

async def main():
    redis = create_redis_client()
        
    await asyncio.sleep(2)
    
    print("Hello from py-scheduler!")


if __name__ == "__main__":
    asyncio.run(main())
