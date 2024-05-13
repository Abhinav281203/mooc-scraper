from pyppeteer import launch
import asyncio
import json
import random

sessions = []
proxy_username = "ewsizjok"
proxy_password = "lhxgsphtva4d"
proxies = []

with open("proxies.txt", "r") as file:
    file_P = file.read().split("\n")
    for proxy in file_P:
        proxy = proxy.split(":")
        proxies.append((proxy[0], proxy[1]))


async def do_task(id, course):
    try:
        print("Starting", id)
        session = random.choice(sessions)
        page = await session.newPage()
        await page.authenticate(
            {"username": proxy_username, "password": proxy_password}
        )

        await page.goto(course["link"])
        await page.waitForNavigation()
        course["link"] = page.url

        await page.close()
        print("done", id)
    except Exception as e:
        await page.close()
        print(e, "retrying", id)
        await do_task(id, course)


async def scrape():
    with open("level_2/infosec_meta.json", "r") as file:
        data = json.load(file)

    for _ in range(20):
        x = random.choice(proxies)
        sessions.append(
            await launch({"headless": True, "args": [f"--proxy-server={x[0]}:{x[1]}"]})
        )

    for i in range(0, len(data), 300):
        upto = min(i + 300, len(data))
        tasks = []
        for idx, course in enumerate(data[i:upto]):
            if "www.classcentral.com/course" in course["link"]:
                tasks.append(do_task(i + idx, course))

        await asyncio.gather(*tasks)  # Await the tasks to complete

    for session in sessions:
        await session.close()  # Close all browser sessions

    with open("level_2/infosec_meta.json", "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    asyncio.run(scrape())
