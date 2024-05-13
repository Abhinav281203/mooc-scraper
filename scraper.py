import asyncio
import random

proxy_username = "ewsizjok"
proxy_password = "lhxgsphtva4d"


# Gets a random session opens the page and scrapes 15 links
async def scrape_page(sessions, page_no):
    try:
        print("starting", page_no)
        session = random.choice(sessions)
        page = await session.newPage()
        await page.authenticate(
            {"username": proxy_username, "password": proxy_password}
        )
        await page.goto(
            f"https://www.classcentral.com/subject/infosec?page={page_no}",
            {"waitUntil": "domcontentloaded"},
        )
        await page.waitForSelector(".course-list-course")
        courses = await page.querySelectorAll(".course-list-course")

        details = []
        for course in courses:
            detail = {}
            # Name
            detail["name"] = await page.evaluate(
                "(element) => element.textContent",
                await course.querySelector(".text-1"),
            )
            # Class central link
            detail["link"] = "https://www.classcentral.com" + await page.evaluate(
                '(element) => element.getAttribute("href")',
                await course.querySelector(".course-name"),
            )
            details.append(detail)

        print(page_no, end=" ")
        await page.close()
        return details
    except Exception as e:
        print(e)
        await page.close()
        # We need not to stop because the get data regardless of video courses here
        # Error only occurs when blocked, Therefore, close this page and
        # Try again with another session which has different Proxy
        return await scrape_page(sessions, page_no)


async def main(sessions, number_start, upto):
    list_of_details = []

    tasks = []
    for page_no in range(number_start, upto):
        tasks.append(scrape_page(sessions, page_no))

    results = await asyncio.gather(*tasks)  # Wait till all tasks has completed
    for result in results:
        list_of_details.extend(result)  # Get output of all tasks

    return list_of_details
