from bs4 import BeautifulSoup
import requests

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

if __name__ == '__main__':
    main()