import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from scraper import JMBullionScraper, APMEXScraper

app = Flask(__name__)

def save_to_json(data):
    with open("scraped_results.json", "w") as f:
        json.dump(data, f)

def load_from_json():
    try:
        with open("scraped_results.json", "r") as f:
            data = json.load(f)
            # Filter out items with no price
            filtered_data = [item for item in data if item.get('price')]
            return filtered_data
    except FileNotFoundError:
        return []

# Function to sort results based on price(For some reason at 3am I decided I need two sort functions. All I know is that it works like this)
def sort_results(data, sort_by):
    def get_price_value(item):
        price_str = item.get('price', '').replace('$', '').replace(',', '').strip()
        return float(price_str) if price_str else float('inf')  # Return infinity if price is empty

    if sort_by == "price_asc":
        return sorted(data, key=lambda x: get_price_value(x))
    elif sort_by == "price_desc":
        return sorted(data, key=lambda x: get_price_value(x), reverse=True)
    else:
        return data

# Function to sort results by price
def sort_results_by_price(data, sort_order):
    def get_price_value(item):
        price_str = item.get('price', '').replace('$', '').replace(',', '').strip()
        return float(price_str) if price_str else float('inf')  # Return infinity if price is empty

    sorted_data = sorted(data, key=lambda x: get_price_value(x))
    if sort_order == 'desc':
        sorted_data.reverse()
    return sorted_data


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']

    scraper_classes = {
        'jmbullion': JMBullionScraper,
        'apmex': APMEXScraper,
    }

    aggregated_results = []

    for website, scraper_class in scraper_classes.items():
        scraper = scraper_class(search_query)
        results = scraper.scrape()
        if results:
            aggregated_results.extend(results)

    # Filter out items with no prices
    aggregated_results = [item for item in aggregated_results if item.get('price')]

    save_to_json(aggregated_results)
    return redirect(url_for('results', search_query=search_query))

@app.route('/results')
def results():
    search_query = request.args.get('search_query')
    sort_by = request.args.get('sort_by')

    if search_query:
        scraper_classes = {
            'jmbullion': JMBullionScraper,
            'apmex': APMEXScraper,
        }

        aggregated_results = []

        for website, scraper_class in scraper_classes.items():
            scraper = scraper_class(search_query)
            results = scraper.scrape()
            if results:
                aggregated_results.extend(results)

        # Filter out items with no prices
        aggregated_results = [item for item in aggregated_results if item.get('price')]

        save_to_json(aggregated_results)
    else:
        aggregated_results = load_from_json()

    if sort_by:
        aggregated_results = sort_results(aggregated_results, sort_by)

    return render_template('results.html', results=aggregated_results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
