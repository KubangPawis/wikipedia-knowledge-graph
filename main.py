from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import random

wiki_nodes_df = pd.DataFrame(columns=['page_title', 'url', 'last_modified', 'categories'])

def get_page_details(nodes_table, page_url):
    url_page_response = requests.get(page_url)

    # Page Title, URL
    wiki_page_soup = BeautifulSoup(url_page_response.text, 'lxml')
    page_title = wiki_page_soup.title.text
    wiki_page_url = url_page_response.url
    print(f'Page Title: {page_title}')
    print(f'Page URL: {wiki_page_url}')

    # Page Categories
    cat_container = wiki_page_soup.find('div', id='mw-normal-catlinks', class_='mw-normal-catlinks')
    categories = [cat.text for cat in cat_container.find_all('a') 
                  if cat['title'].startswith('Category:')]
    
    print('Page Categories:', ', '.join(categories))

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

    # Data Dictionary
    new_page_data = {
        'page_title': page_title,
        'url': wiki_page_url,
        'categories': categories,
        'last_modified': latest_date,
    }

    # Append current page metadata to Page Node Table
    nodes_table = pd.concat([nodes_table, pd.DataFrame([new_page_data])], ignore_index=True)
    print(nodes_table)

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
    get_page_details(wiki_nodes_df, start_url)

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