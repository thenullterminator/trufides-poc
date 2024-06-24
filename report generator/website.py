import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_important_pages(base_url):
     important_pages = [
          "about", "contact", "terms", "privacy", "legal", "policy"
          # "disclaimer", "policy", "team", "services", "products", "faq", "help"
     ]
     
     important_pages_content = {}

     # Function to scrape and parse a page
     def scrape_page(url):
          response = requests.get(url)
          response.raise_for_status()
          return BeautifulSoup(response.content, 'html.parser')

     # Function to extract relevant content
     def extract_relevant_content(soup):
          # Extract content from main sections or specific divs
          main_content = soup.find('main')
          if main_content:
               return main_content.get_text(separator='\n', strip=True)
          
          # Fallback to specific divs
          content_divs = soup.find_all('div', class_=['content', 'main-content', 'post-content'])
          if content_divs:
               content = "\n".join([div.get_text(separator='\n', strip=True) for div in content_divs])
               return content
          
          # Fallback to body tag
          body_content = soup.find('body')
          if body_content:
               return body_content.get_text(separator='\n', strip=True)
          
          # Fallback to all text if no specific sections found
          return soup.get_text(separator='\n', strip=True)

     # Scrape the homepage to find links
     homepage_soup = scrape_page(base_url)
     important_pages_content['base'] = extract_relevant_content(homepage_soup)
     links = homepage_soup.find_all('a', href=True)

     for link in links:
          href = link['href']
          for page in important_pages:
               if page in href.lower():
                    full_url = urljoin(base_url, href)
                    page_soup = scrape_page(full_url)
                    important_pages_content[page] = extract_relevant_content(page_soup)
                    break

     return important_pages_content
