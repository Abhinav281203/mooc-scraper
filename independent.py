from pyppeteer import launch
import asyncio
import json
import random

proxies = []

with open("proxies.txt", "r") as file:
    file_P = file.read().split("\n")
    for proxy in file_P:
        proxy = proxy.split(":")
        proxies.append((proxy[0], proxy[1]))

# import sys
# sys.exit()

# ewsizjok:lhxgsphtva4d
proxy_username = "ewsizjok"
proxy_password = "lhxgsphtva4d"
pateince = {}

# Browser / Chromium windows
sessions = []
to_close_sessions = []


# Gives a random session from the available session
def get_random_session():
    return random.choice(sessions)


# Takes a session and a course and write metadata to JSON
async def real_scrape_details(id, course):
    # repeating the same page forever
    if id not in pateince:
        pateince[id] = 1
    else:
        if pateince[id] > 5:
            print("Tried this too many times", id)
            return
        pateince[id] += 1

    if len(sessions) != 20:
        for i in to_close_sessions:
            if len(i.pages()) == 0:
                print("This is to_close_sessions, and has no active pages")
                print("Killing the session and adding new one")
                await i.close()
                x = random.choice(proxies)
                sessions.append(
                    await launch(
                        {"headless": True, "args": [f"--proxy-server={x[0]}:{x[1]}"]}
                    )
                )

    video = False
    try:
        session = get_random_session()
        page = await session.newPage()
        await page.authenticate(
            {"username": proxy_username, "password": proxy_password}
        )
        await page.goto(course["link"])
        # First, to know whether it is video course we check for this element
        # and if yes we set video to True
        if await page.evaluate(
            "() => { return document.querySelector('.js-start-course') !== null }"
        ):
            video = True
            raise Exception("Video encountered")

        await page.waitForSelector(".course-details-item")

        # If the element that has the metadata exists
        if await page.evaluate(
            "() => { return document.querySelector('.course-details-item') !== null }"
        ):
            # Attributes are a list of keys value pairs that tells metadata
            attributes = await page.querySelectorAll(".course-details-item")
            await page.waitForSelector(".medium-up-hidden.text-2.color-gray")
            await page.waitForSelector(".text-2.line-tight")

            for attribute in attributes:
                name = await page.evaluate(
                    """(element) => {
                            return element.getAttribute("class");
                        }""",
                    attribute,
                )
                # Any value that leads to null
                if "small-down-hidden" in name.lower():
                    continue

                key = await page.evaluate(
                    """(element) => {
                            return element.firstElementChild.querySelector('.text-2').textContent;
                        }""",
                    attribute,
                )
                value = await page.evaluate(
                    """(element) => {
                            return element.children[1].querySelector('.text-2').textContent;
                        }""",
                    attribute,
                )

                key = key.strip().lower()
                value = value.strip().lower()

                # values of languages and subtitles should be a list
                if key == "languages" or key == "subtitles":
                    course[key] = [lang.strip() for lang in value.split(",")]
                else:
                    course[key] = value
        # elif await page.evaluate('''() => { return document.querySelector('.js-start-course') !== null }'''):
        # print("Video course. won't be useful", course["link"])

        # Getting the link of the "go to class"
        link_extension = await page.evaluate(
            """() => {
                    const element = document.querySelector('[data-track-click="course_go_to_class"]');
                    if (element) {
                        return element.getAttribute('href');
                    } else {
                        return null;
                    }
                }"""
        )

        # Visiting the original link of course through the alias link
        # and update the link field
        await page.goto("https://www.classcentral.com" + link_extension)
        await page.waitForNavigation()
        course["link"] = page.url

        await page.close()
        with open("level_2/infosec_meta.json", "r") as file:
            cs_meta = json.load(file)
        cs_meta.append(course)
        with open("level_2/infosec_meta.json", "w") as file:
            json.dump(cs_meta, file, indent=4)

        print("Written", id)
    except Exception as e:
        rate_limited = False
        if "Navigation" not in str(e):
            rate_limited = await page.evaluate(
                """() => {
                    const element = document.querySelector('.cf-error-details');
                    if (element) {
                        return element.getAttribute('href');
                    } else {
                        return null;
                    }
                }"""
            )
        await page.close()

        if rate_limited:
            print(
                "Temporarily banned, moving to to_close_sessions and removing from sessions"
            )
            to_close_sessions.append(session)
            sessions.remove(session)
        # Termination occurs only two cases
        # 1. Video link, 2. Human verification
        # We want to stop only when it is a video course, incase of blocking
        # We close this page and try it with a different session with different proxy
        if video:
            print(e, "leaving", id)
            return
        print("retrying", id)
        await real_scrape_details(id, course)


# Takes a batch_size level_1_details and try to get metadata using random sessions
async def scrape_details(start_idx, details):
    start = 0
    end = len(details)
    batch_size = len(details) // len(sessions)
    if batch_size == 0:
        batch_size = len(details)

    print(f"Start - {start} end - {end} batch_size - {batch_size}")
    for i in range(start, end, batch_size):
        upto = min(i + batch_size, end)
        print(f"Sending in {start_idx+i} to {start_idx+upto}")
        meta_data_tasks = [
            real_scrape_details(start_idx + i + index, course=course)
            for index, course in enumerate(details[i:upto])
        ]
        await asyncio.gather(*meta_data_tasks)


async def main():
    for _ in range(20):
        x = random.choice(proxies)
        sessions.append(
            await launch({"headless": True, "args": [f"--proxy-server={x[0]}:{x[1]}"]})
        )
    print("Got new sessions")

    with open("level_1/infosec.json", "r") as file:
        level_1_data = json.load(file)

    start = 1795
    end = len(level_1_data)
    batch_size = 500

    for i in range(start, end, batch_size):
        upto = min(i + batch_size, end)
        distributing_task = []
        distributing_task.append(scrape_details(i, level_1_data[i:upto]))
        await asyncio.gather(*distributing_task)

    for session in sessions:
        await session.close()


if __name__ == "__main__":
    # asyncio.get_event_loop().run_until_complete(main())
    asyncio.run(main())
