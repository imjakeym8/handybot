import asyncio
import handybot
import datetime

class DummyContext:
    args = []

async def monthly_run(groupusername: list[str]):
    for each in groupusername:
        await handybot.post_monthly_metrics(
            update=handybot.Update, 
            context=DummyContext(), 
            handle=each
        )
        print(f"finished metrics for {each}.")
    print(f"Finished at {datetime.datetime.now(datetime.timezone.utc)}")

my_handles = ["cookie_dao","bair_ai","certikcommunity","solidusaichat","bitdo_ge","miradaai","plutonaichat","hypergptai","initverseph","satoshidexai","stakelayer"]
asyncio.run(monthly_run(my_handles))