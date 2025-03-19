from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import random

wiki_nodes_df = pd.DataFrame(columns=['page_title', 'url', 'last_modified', 'categories'])
wiki_edges_df = pd.DataFrame(columns=['source', 'target'])

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

    return nodes_table

def filter_target_headings(target_headings):
    filtered_arr = []
    for heading in target_headings:
        if heading.text in ['See also', 'References']:
            break
        filtered_arr.append(heading)
    return filtered_arr

def main():
    global wiki_nodes_df
    global wiki_edges_df

    start_url = 'https://en.wikipedia.org/wiki/Artificial_intelligence'
    start_url_response = requests.get(start_url)

    current_url = start_url
    current_url_response = start_url_response    

    while len(wiki_nodes_df) < 10:
        soup = BeautifulSoup(current_url_response.text, 'lxml')

        # Extract current page metadata
        wiki_nodes_df = get_page_details(wiki_nodes_df, current_url)

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

                # Add visible <a> tags to edge table
                for link in rel_content:

                    # Skip disallowed pages(check on robots.txt)
                    if link[1].startswith('/w/') \
                        or link[1].startswith('/api/') \
                        or link[1].startswith('/trap/') \
                        or link[1].startswith('/wiki/Special:') \
                        or link[1].startswith('/wiki/Spezial:') \
                        or link[1].startswith('/wiki/Spesial:') \
                        or link[1].startswith('/wiki/Special%3A') \
                        or link[1].startswith('/wiki/Spezial%3A:') \
                        or link[1].startswith('/wiki/Spesial%3A') :
                        continue

                    if link[1].startswith('/wiki/'):
                        new_edge_data = {
                            'source': current_url,
                            'target': f'https://en.wikipedia.org{link[1]}',
                        }
                        wiki_edges_df = pd.concat([wiki_edges_df, pd.DataFrame([new_edge_data])], ignore_index=True)
                        print(wiki_edges_df)

                # TEMP TERMINATOR
                if len(wiki_edges_df[wiki_edges_df['source'] == current_url]) >= 10:
                    break

                time.sleep(random.uniform(1, 3))

        # Reassign current URL to the next available URL
        unvisited_pages = wiki_edges_df.loc[(~wiki_edges_df['target'].isin(wiki_nodes_df['url'])), 'target']
        print('UNVISITED PAGES:')
        print(unvisited_pages)

        if not unvisited_pages.empty:
            current_url = unvisited_pages.iloc[0]
        else:
            print('No more unvisited pages. Stopping the crawl.')
            break

        print(f'[DEBUG] Next URL: {current_url}')
        current_url_response = requests.get(current_url)

    print(wiki_nodes_df)
    print(wiki_edges_df)

    # Export extracted data to CSV
    wiki_nodes_df.to_csv('./extracted_data/wiki_nodes.csv', index=False)
    wiki_edges_df.to_csv('./extracted_data/wiki_edges.csv', index=False)

if __name__ == '__main__':
    main()