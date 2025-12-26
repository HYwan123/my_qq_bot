from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

async def job_1():
    await asyncio.sleep(1)
    print("finish job")

async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(job_1, trigger='cron', second='*/10')
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())