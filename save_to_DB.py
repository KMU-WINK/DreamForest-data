import csv

import mysql.connector
import re
import time

from naver_map_place import get_search_list, get_first_place_id, get_store_info, parsing_store_info, get_review, \
    parsing_review
import secret_key


def remove_parentheses(string):
    return re.sub(r"\([^)]*\)", "", string)


SLEEP_TIME = 1

with open('stores.csv', 'w', newline='', encoding='utf-8') as stores_csv_file:
    with open('reviews.csv', 'w', newline='', encoding='utf-8') as reviews_csv_file:

        # Connect to the database
        cnx = mysql.connector.connect(user=secret_key.db_user, password=secret_key.db_password,
                                      host=secret_key.db_host, database=secret_key.db_database)
        cursor = cnx.cursor()
        query = ("SELECT id, store_name, parcel_address FROM store ORDER BY id")
        cursor.execute(query)

        crawling_success_count = 0
        crawling_error_count = 0

        for (id, store_name, parcel_address) in cursor:
            # print(id, store_name, parcel_address)

            if parcel_address is None or parcel_address == "None" or store_name is None:
                continue

            dong_match = re.search(r"^(서울 [^\s]+구 [^\s]+동)", parcel_address)

            if dong_match is None:
                crawling_error_count += 1
                continue

            dong_address = dong_match.group(1)

            search_keywords = [f"{dong_address} {remove_parentheses(store_name)}",
                               f"{remove_parentheses(store_name)} {dong_address}"]

            is_crawling_success = False

            for search_keyword in search_keywords:

                print("search_keyword:", search_keyword)

                place_search_data = get_search_list(search_keyword)
                time.sleep(SLEEP_TIME)
                place_id = get_first_place_id(place_search_data)
                print("place_id:", place_id)

                if place_id is None:
                    print("네이버 지도에서 장소를 찾지 못해 다른 키워드로 재검색합니다.")
                    print()
                    continue

                else:
                    place_info = get_store_info(place_id)
                    time.sleep(SLEEP_TIME)
                    # print("place_info:", place_info)

                    parsing_place = parsing_store_info(place_info)
                    time.sleep(SLEEP_TIME)
                    print("parsing_place:", parsing_place)

                    review_data = get_review(place_id)
                    time.sleep(SLEEP_TIME)
                    print("review_data:", review_data)

                    review_stats, parsing_reviews = parsing_review(review_data)
                    time.sleep(SLEEP_TIME)
                    print("review_stats:", review_stats)
                    print("parsing_reviews:", parsing_reviews)
                    print("\n")

                    # Make stores.csv (start)
                    stores_dict = {"id": id}
                    stores_dict.update(parsing_place)
                    stores_dict.update(review_stats)
                    stores_writer = csv.DictWriter(stores_csv_file, fieldnames=stores_dict.keys())
                    if reviews_csv_file.tell() == 0:
                        stores_writer.writeheader()
                    stores_writer.writerow(stores_dict)
                    # Make stores.csv (end)

                    # Make reviews.csv (start)
                    reviews_dict = {"stores_id": id}
                    for review in parsing_reviews:
                        reviews_dict.update(review)
                        reviews_writer = csv.DictWriter(reviews_csv_file, fieldnames=reviews_dict.keys())
                        if reviews_csv_file.tell() == 0:
                            reviews_writer.writeheader()
                        reviews_writer.writerow(reviews_dict)
                    # Make reviews.csv (end)

                    is_crawling_success = True
                    crawling_success_count += 1
                    break

            if not is_crawling_success:
                crawling_error_count += 1

crawling_number = crawling_success_count + crawling_error_count
print(
    f"crawling success rate: {round(crawling_success_count / crawling_number)}% ({crawling_success_count}/{crawling_number})")

cursor.close()  # Close the cursor
cnx.close()  # Close the connection
