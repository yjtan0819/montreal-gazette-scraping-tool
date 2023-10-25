import requests
from bs4 import BeautifulSoup
import json
import argparse
from pathlib import Path

BASE_URL = "https://montrealgazette.com"

# Get the HTML content of a page
def get_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# Save the HTML content of a page to a file for caching
def save_html_to_file(url, file_path):
    html_content = get_page(url)
    with open(file_path, 'w') as file:
        file.write(html_content)

# Load the HTML content of a page from a file
def load_html_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Extract the links of the trending stories
def extract_trending_links():
    homepage_content = load_html_from_file("homepage.html")
    soup = BeautifulSoup(homepage_content, 'html.parser')
    
    trending_div = soup.find('div', class_='list-widget list-widget-trending')
    trending_ol = trending_div.find('ol')
    trending_li = trending_ol.find_all('li')
    
    links = []
    for li in trending_li:
        link = li.find('div', class_='article-card__details').find('a')['href']
        links.append(link)
    return links

# Extract the article information from the article page
# such as title, publication date, author, and blurb (summary)
def extract_article_info(article_url):
    article_content = load_html_from_file(article_url)
    soup = BeautifulSoup(article_content, 'html.parser')

    detail_div = soup.find('div', class_='article-header__detail__texts')
    meta_div = detail_div.find('div', class_='article-meta')

    article_title = detail_div.find('h1').text.strip()

    article_date_div = meta_div.find('div', class_='published-date')
    article_date = article_date_div.find('span', class_='published-date__since').text.strip()
    
    article_author_div = meta_div.find('div', class_='published-by')
    article_author = article_author_div.find('span', class_='published-by__author').text.strip()

    article_blurb = detail_div.find('p', class_='article-subtitle').text.strip()

    article_info = {
        "title": article_title,
        "publication_date": article_date,
        "author": article_author,
        "blurb": article_blurb
    }

    return article_info

def main(output_file):
    # Save the homepage HTML to a file for caching
    save_html_to_file("https://montrealgazette.com/category/news/", "homepage.html")
    
    trending_links = extract_trending_links()
    trending_articles = []

    for link in trending_links:
        if not Path(link.split('/')[-1]+".html").exists():
            save_html_to_file(BASE_URL+link, link.split('/')[-1]+".html")
        article_info = extract_article_info(link.split('/')[-1]+".html")
        trending_articles.append(article_info)

    # Save the trending articles to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(trending_articles, json_file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect trending stories from Montreal Gazette.")
    parser.add_argument("-o", help="Output file in JSON format", required=True)
    args = parser.parse_args()

    main(args.o)
