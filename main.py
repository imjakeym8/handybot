import asyncio
import handybot

class DummyContext:
    args = []

async def run():
    await handybot.post_metrics(
        update=handybot.Update, 
        context=DummyContext(), 
        handle="samplegroup998"
    )

asyncio.run(run())