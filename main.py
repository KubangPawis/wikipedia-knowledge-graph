from bs4 import BeautifulSoup
import requests
import time
import random

def get_page_details(page_url):
    url_page_response = requests.get(page_url)

    # Page Title, URL
    wiki_page_soup = BeautifulSoup(url_page_response.text, 'lxml')
    page_title = wiki_page_soup.title.text
    print(f'Page Title: {page_title}')
    print(f'Page URL: {url_page_response.url}')

    # Page Latest Change - History
    page_url_title = page_url.split('/')[-1]
    url_history_response = requests.get(f'https://en.wikipedia.org/w/index.php?title={page_url_title}&action=history')
    wiki_history_soup = BeautifulSoup(url_history_response.text, 'lxml')
    history_content = wiki_history_soup.find('section', id='pagehistory')
    latest_change_group = history_content.find('ul', class_='mw-contributions-list')
    latest_change_instance = latest_change_group.find('li')
    latest_date_container = latest_change_instance.find('bdi')
    latest_date = latest_date_container.find('a', class_='mw-changeslist-date').text

    print(f'Latest Date: {latest_date}')

def filter_target_headings(target_headings):
    filtered_arr = []
    for heading in target_headings:
        if heading.text in ['See also', 'References']:
            break
        filtered_arr.append(heading)
    return filtered_arr

def main():
    start_url = 'https://en.wikipedia.org/wiki/Artificial_intelligence'
    start_url_response = requests.get(start_url)
    soup = BeautifulSoup(start_url_response.text, 'lxml')
    
    # Extract current page metadata
    get_page_details(start_url)

    # Main content area
    wikipage_content = soup.find('div', id='mw-content-text')

    # Get only content-based headings
    page_headings = wikipage_content.find_all('div', class_='mw-heading2')
    target_headings = filter_target_headings(page_headings)
    
    for heading in target_headings:
        print(heading.text)

    # Get all <p> tag siblings next to the target_headings
    for heading in target_headings:
        print(f'\n{heading.text}\n')

        # Terminate if current sibling is not a part of the current heading
        for sibling in heading.find_next_siblings():
            if 'mw-heading2' in sibling.get('class', []):
                break

            # Get all <a> tags in each sibling (exclude citation <a> tags)
            rel_content = [(a.text.strip(), a['href']) for a in sibling.find_all('a') 
                           if 'href' in a.attrs
                           and a.text.strip()
                           and not a['href'].startswith('#cite')]
            print(rel_content)

            time.sleep(random.uniform(1, 3))

if __name__ == '__main__':
    main()