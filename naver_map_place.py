from selenium import webdriver
from bs4 import BeautifulSoup
import json


def get_naver_map_place(search_keyword):
    driver = webdriver.Chrome()  # Create a new Chrome browser instance
    driver.get(f'https://map.naver.com/v5/api/search?caller=pcweb&query={search_keyword}')  # Navigate to the URL
    driver.implicitly_wait(10)  # Wait for the page to load
    html = driver.page_source  # Get the page source

    soup = BeautifulSoup(html, 'html.parser')
    pre_element = soup.select_one('body > pre')
    place_json_data = json.loads(pre_element.text)

    driver.close()  # Close the browser
    return place_json_data


if __name__ == '__main__':
    search_keyword = '짜짜루 서울 강남구 역삼동'
    place_json_data = get_naver_map_place(search_keyword)
    print(place_json_data)
