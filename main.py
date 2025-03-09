from bs4 import BeautifulSoup
import requests
import time
import random

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