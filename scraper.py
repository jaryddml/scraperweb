import json
from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



class BaseScraper:
    def __init__(self, search_query):
        self.search_query = search_query

    def get_url(self):
        raise NotImplementedError("Subclasses must implement get_url method")

    def scrape(self):
        raise NotImplementedError("Subclasses must implement scrape method")


class JMBullionScraper(BaseScraper):
    def get_url(self):
        return f"https://www.jmbullion.com/search/?q={self.search_query}"

    def scrape(self):
        try:
            print("Fetching URL...")
            home_url = "https://www.jmbullion.com/"
            
        
            display = Display(visible=0, size=(800, 600)) #Change 0 to 1 for visible
            display.start()
            driver = webdriver.Chrome()
            driver.get(home_url)
            driver.get(self.get_url())
            # Wait for specific elements to load instead of time.sleep()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product")))
            
            print("URL fetched, parsing HTML...")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            print("HTML parsed, quitting driver...")
            driver.quit()
            display.stop()

            products = soup.find_all("div", class_="product type-product status-publish hentry mainproductIn cat-product first instock")
            results = []
            for product in products[:50]:
                title = product.find("span", class_="title")
                price = product.find("span", class_="price")
                link = product.find("a", href=True)['href'] if product.find("a", href=True) else None
                image_tag = product.find("img")
                image = image_tag['src'] if image_tag else None
                if title and price and link:
                    result = {
                        'title': title.text.strip(),
                        'price': price.text.strip(),
                        'link': link
                    }
                    if image:
                        result['image'] = image
                    results.append(result)
            print("Scraping completed.")
            return results
        except Exception as e:
            print("An error occurred:", e)


class APMEXScraper(BaseScraper):
    def get_url(self):
        return f"https://www.apmex.com/search?&q={self.search_query}"

    def scrape(self):
        try:
            print("Fetching URL...")
            URL = self.get_url()
            
            display = Display(visible=0, size=(800, 600))
            display.start()   
            driver = webdriver.Chrome()
            driver.get(URL)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-essential")))
            
            print("URL fetched, parsing HTML...")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            print("HTML parsed, quitting driver...")
            driver.quit()
            display.stop()

            products = soup.find_all("div", class_="product-essential")
            results = []
            for product in products[:50]:
                title = product.find("div", class_="mod-product-title")
                price = product.find("span", class_="price")
                link = product.find("a", class_="item-link")['href'] if product.find("a", class_="item-link") else None
                link = ("https://www.apmex.com/" + link)
                imagetag = product.find("img", class_="lazy")
                image = imagetag["src"] if imagetag else None
                if title and price and link:
                    result = {
                        'title': title.text.strip(),
                        'price': price.text.strip(),
                        'link': link
                    }
                    if image:
                        result['image'] = image
                    results.append(result)
            print("Scraping completed.")
            return results
        except Exception as e:
            print("An error occurred:", e)


def main():
    search_query = input("Enter search query for bullion and coin websites: ")

    scraper_classes = {
        'jmbullion': JMBullionScraper,
        'apmex': APMEXScraper,
    }


    #The lines below are never executed when running normally. Left in for debug reasons. 
    aggregated_results = []
    for website, scraper_class in scraper_classes.items():
        scraper = scraper_class(search_query)
        results = scraper.scrape()
        if results:
            aggregated_results.extend(results)

   
    with open("scraped_results.json", "w") as f:
        json.dump(aggregated_results, f)
    print("Results saved to scraped_results.json")


if __name__ == "__main__":
    main()
