import asyncio
from scraper import JMBullionScraper, APMEXScraper

async def scrape_website(website, search_query):
    scraper_class = {
        'jmbullion': JMBullionScraper,
        'apmex': APMEXScraper,
    }[website]
    scraper = scraper_class(search_query)
    return await asyncio.get_event_loop().run_in_executor(None, scraper.scrape)

async def main():
    search_query = input("Enter search query for bullion and coin websites: ")
    websites = ['jmbullion', 'apmex']

    tasks = [scrape_website(website, search_query) for website in websites]
    results = await asyncio.gather(*tasks)

    aggregated_results = []
    for result in results:
        aggregated_results.extend(result)

    #processes aggregated results here NOT scraper.py

if __name__ == "__main__":
    asyncio.run(main())