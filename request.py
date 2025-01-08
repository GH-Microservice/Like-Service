import asyncio
import httpx
import time

# Константы
URL = "http://localhost:8085/like-service/api/v1/get-likes/3/"
TOTAL_REQUESTS = 300000
CONCURRENT_REQUESTS = 200  # Одновременных запросов

async def send_request(client: httpx.AsyncClient, url: str):
    """Функция для отправки одного запроса."""
    try:
        response = await client.get(url)
        print(f"Response {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Основной асинхронный метод."""
    start_time = time.time()
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        async def limited_request():
            async with semaphore:
                await send_request(client, URL)

        tasks = [limited_request() for _ in range(TOTAL_REQUESTS)]
        await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Sent {TOTAL_REQUESTS} requests in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
