import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import json


def get_search_list(search_keyword):
    options = webdriver.ChromeOptions()

    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("lang=ko_KR")
    options.add_argument(
        f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36')
    driver = webdriver.Chrome(chrome_options=options)  # Create a new Chrome browser instance

    driver.get(f'https://map.naver.com/v5/api/search?caller=pcweb&query={search_keyword}')  # Navigate to the URL
    driver.implicitly_wait(10)  # Wait for the page to load
    html = driver.page_source  # Get the page source

    soup = BeautifulSoup(html, 'html.parser')
    pre_element = soup.select_one('body > pre')
    place_json_data = json.loads(pre_element.text)

    driver.close()  # Close the browser
    return place_json_data


def get_first_place_id(place_json_data):
    place_result = place_json_data['result']['place']
    if place_result is None:
        return None
    first_place_id = place_result['list'][0]['id']
    return first_place_id


def get_store_info(place_id):
    response = requests.get(f"https://map.naver.com/v5/api/sites/summary/{place_id}")

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data


if __name__ == '__main__':
    search_keyword = '서울 강남구 역삼동 짜짜루'
    place_json_data = get_search_list(search_keyword)
    place_id = get_first_place_id(place_json_data)
    print("place_id:", place_id)
    if place_id is not None:
        place_info = get_store_info(place_id)
        print("place_info:", place_info)
