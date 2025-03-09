from bs4 import BeautifulSoup
import requests

def main():
    start_url = 'https://en.wikipedia.org/wiki/Artificial_intelligence'
    start_url_response = requests.get(start_url)

    soup = BeautifulSoup(start_url_response.text, 'lxml')
    print(soup.title.text)

if __name__ == '__main__':
    main()