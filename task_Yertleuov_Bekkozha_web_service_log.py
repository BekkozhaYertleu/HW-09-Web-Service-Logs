import re
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import pytz
import argparse  # Added argparse

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s", 
    datefmt="%Y%m%d_%H%M%S"
)
logger = logging.getLogger(__name__)

class WikipediaUnavailable(Exception):
    pass

def log_query_processing(func):
    """Декоратор для логирования начала и окончания обработки запроса."""
    def wrapper(*args, **kwargs):
        query = request.args.get('query')
        logger.debug("start processing query: %s", query)
        try:
            result = func(*args, **kwargs)
        finally:
            logger.debug("finish processing query: %s", query)
        return result
    return wrapper

@app.route('/api/search')
@log_query_processing
def search():
    """Обработка поискового запроса через Википедию."""
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    try:
        response = requests.get(f"https://en.wikipedia.org/w/index.php?search={query}")
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise WikipediaUnavailable()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if soup.find(class_="mw-search-nonefound"):
        article_count = 0
    else:
        result_stats = soup.find('div', {'class': 'results-info'})
        if result_stats:
            match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+) results', result_stats.text)
            article_count = int(match.group(1).replace(',', '') if match else 0
        else:
            article_count = 0
    
    logger.info("found %s articles for query: %s", article_count, query)
    return jsonify({"version": 1.0, "article_count": article_count})

@app.errorhandler(404)
def not_found(error):
    return "This route is not found", 404

@app.errorhandler(WikipediaUnavailable)
def handle_wikipedia_unavailable(error):
    return "Wikipedia Search Engine is unavailable", 503

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind')
    parser.add_argument('--port', default=5000, type=int, help='Port to bind')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=True)  # Use provided host/port
