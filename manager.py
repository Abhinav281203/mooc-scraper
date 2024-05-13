import asyncio
from pyppeteer import launch
import random
import scraper
import json

proxies = []

with open("proxies.txt", "r") as file:
    proxies = file.read().split("\n")

# import sys
# sys.exit()


# Returns the sessions with inserted proxies
def get_args(proxy):
    x = proxy.split(":")
    return {"headless": True, "args": [f"--proxy-server={x[0]}:{x[1]}"]}


# Creates sessions, executes scraper.main(sessions)
# Gets list of json, dump them and close sessions
async def main():
    sessions = []
    for i in range(17):
        proxy = random.choice(proxies)
        browser = await launch(get_args(proxy))
        # browser = await launch({"headless": True})
        sessions.append(browser)

    start = 0
    end = 163
    batch_size = 100
    # 90 - working fine
    # 100 - okay okay
    # 150 - too much time than usual

    for i in range(start, end, batch_size):
        upto = min(i + batch_size, end)  # Set upto as the step size

        print(f"from {i} and {upto}")
        level_1_details = await scraper.main(sessions, number_start=i, upto=upto)

        with open("infosec.json", "r") as file:
            existing_data = json.load(file)
        existing_data.extend(level_1_details)
        with open("infosec.json", "w") as file:
            json.dump(existing_data, file, indent=4)

        print("-" * 1000)
        print("-" * 1000)

    for browser in sessions:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
