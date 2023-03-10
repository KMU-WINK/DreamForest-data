import csv
import time
from datetime import datetime
import re

import mysql.connector
import pytz

from naver_map_place import get_search_list, get_first_place_id, get_store_info, parsing_store_info, get_review, \
    parsing_review
import secret_key
import config


def remove_parentheses(string):
    return re.sub(r"\([^)]*\)", "", string)


with open(config.store_csv_path, 'w', newline='', encoding='utf-8') as stores_csv_file:
    with open(config.review_csv_path, 'w', newline='', encoding='utf-8') as reviews_csv_file:

        # Connect to the database
        cnx = mysql.connector.connect(user=secret_key.db_user, password=secret_key.db_password,
                                      host=secret_key.db_host, database=secret_key.db_database)
        cursor = cnx.cursor()

        store_query_string = "SELECT id, store_name, parcel_address"
        store_query_string += " FROM store"
        store_query_string += " WHERE store_name IS NOT NULL"
        store_query_string += " AND parcel_address IS NOT NULL"
        store_query_string += " AND (naver_updated_at <= DATE_SUB(NOW(), INTERVAL 7 DAY) OR naver_updated_at IS NULL)"
        store_query_string += f" AND id >= {config.start_id} "
        store_query_string += " ORDER BY id"
        store_query_string += f" LIMIT {config.crawling_num}"

        store_select_query = (store_query_string)
        cursor.execute(store_select_query)

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
                time.sleep(config.sleep_time)
                place_id = get_first_place_id(place_search_data)
                print("place_id:", place_id)

                if place_id is None:
                    print("네이버 지도에서 장소를 찾지 못해 다른 키워드로 재검색합니다.")
                    print()
                    # Update naver_updated_at in store table (start)
                    update_cnx_1 = mysql.connector.connect(user=secret_key.db_user, password=secret_key.db_password,
                                                           host=secret_key.db_host, database=secret_key.db_database)
                    update_cursor_1 = update_cnx_1.cursor()

                    kst = pytz.timezone('Asia/Seoul')  # Create a timezone object for KST
                    naver_update_time = datetime.now(tz=kst)  # Get the current date and time in KST

                    stores_update_dic_1 = {"naver_updated_at": naver_update_time}

                    stores_update_query_1 = "UPDATE store SET {} WHERE id = {}".format(
                        ", ".join("{}=%s".format(k) for k in stores_update_dic_1), id)
                    print("sql:", stores_update_query_1)

                    value_list_1 = [v for v in stores_update_dic_1.values()]
                    update_cursor_1.execute(stores_update_query_1, value_list_1)

                    update_cnx_1.commit()
                    print(update_cursor_1.rowcount, "record(s) affected in store table")

                    update_cursor_1.close()  # Close the cursor
                    update_cnx_1.close()  # Close the connection
                    # Update naver_updated_at in store table (end)

                    continue

                else:
                    place_info = get_store_info(place_id)
                    time.sleep(config.sleep_time)
                    # print("place_info:", place_info)

                    parsing_place = parsing_store_info(place_info)
                    time.sleep(config.sleep_time)
                    print("parsing_place:", parsing_place)

                    review_data = get_review(place_id)
                    time.sleep(config.sleep_time)
                    print("review_data:", review_data)

                    review_stats, parsing_reviews = parsing_review(review_data)
                    time.sleep(config.sleep_time)
                    print("review_stats:", review_stats)
                    print("parsing_reviews:", parsing_reviews)

                    # Make crawling_data/store.csv (start)
                    kst = pytz.timezone('Asia/Seoul')  # Create a timezone object for KST
                    naver_update_time = datetime.now(tz=kst)  # Get the current date and time in KST

                    stores_dict = {"id": id, "naver_place_id": place_id, "naver_updated_at": naver_update_time}
                    stores_dict.update(parsing_place)
                    stores_dict.update(review_stats)
                    stores_writer = csv.DictWriter(stores_csv_file, fieldnames=stores_dict.keys())
                    if reviews_csv_file.tell() == 0:
                        stores_writer.writeheader()
                    stores_writer.writerow(stores_dict)
                    # Make crawling_data/store.csv (end)

                    # Update store table (start)
                    update_cnx = mysql.connector.connect(user=secret_key.db_user, password=secret_key.db_password,
                                                         host=secret_key.db_host, database=secret_key.db_database)
                    update_cursor = update_cnx.cursor()

                    stores_update_dic = {"naver_place_id": place_id,
                                         "naver_updated_at": naver_update_time}
                    stores_update_dic.update(parsing_place)
                    stores_update_dic.update(review_stats)

                    stores_update_query = "UPDATE store SET {} WHERE id = {}".format(
                        ", ".join("{}=%s".format(k) for k in stores_update_dic), id)
                    print("sql:", stores_update_query)

                    value_list = [v for v in stores_update_dic.values()]
                    update_cursor.execute(stores_update_query, value_list)

                    update_cnx.commit()
                    print(update_cursor.rowcount, "record(s) affected in store table")

                    update_cursor.close()  # Close the cursor
                    update_cnx.close()  # Close the connection
                    # Update store table (end)

                    # Make crawling_data/reviews.csv (start)
                    reviews_dict = {"store_id": id, "naver_place_id": place_id}
                    for review in parsing_reviews:
                        reviews_dict.update(review)
                        reviews_writer = csv.DictWriter(reviews_csv_file, fieldnames=reviews_dict.keys())
                        if reviews_csv_file.tell() == 0:
                            reviews_writer.writeheader()
                        reviews_writer.writerow(reviews_dict)
                        # Make crawling_data/reviews.csv (end)

                    # TODO: cnx 와 cursor 중복 연결 제거
                    # Delete naver_reviews table (start)
                    review_delete_cnx = mysql.connector.connect(user=secret_key.db_user,
                                                                password=secret_key.db_password,
                                                                host=secret_key.db_host,
                                                                database=secret_key.db_database)
                    review_delete_cursor = review_delete_cnx.cursor()

                    review_delete_query = f"DELETE FROM naver_reviews WHERE store_id = {id}"
                    print("review_delete_query:", review_delete_query)
                    review_delete_cursor.execute(review_delete_query)
                    review_delete_cnx.commit()

                    review_delete_cursor.close()  # Close the cursor
                    review_delete_cnx.close()  # Close the connection

                    # Delete naver_reviews  table (end)

                    # Insert naver_reviews table (start) # TODO: Make crawling_data/reviews.csv와 한번에 처리하기. (performance)
                    review_insert_cnx = mysql.connector.connect(user=secret_key.db_user,
                                                                password=secret_key.db_password,
                                                                host=secret_key.db_host,
                                                                database=secret_key.db_database)
                    review_insert_cursor = review_insert_cnx.cursor()

                    for review in parsing_reviews:
                        review_insert_dic = {"store_id": id, "naver_place_id": place_id}
                        review_insert_dic.update(review)
                        # print("reviews_dict:", reviews_dict)

                        review_insert_query = "INSERT INTO naver_reviews ({}) VALUES ({})".format(
                            ", ".join(review_insert_dic.keys()), ", ".join("%s" for _ in review_insert_dic))
                        print("review_insert_query:", review_insert_query)
                        review_insert_cursor.execute(review_insert_query, list(review_insert_dic.values()))
                        review_insert_cnx.commit()

                    review_insert_cursor.close()  # Close the cursor
                    review_insert_cnx.close()  # Close the connection
                    # Insert naver_reviews table (end)

                    print("\n")
                    is_crawling_success = True
                    crawling_success_count += 1
                    break

            if not is_crawling_success:
                crawling_error_count += 1

crawling_number = crawling_success_count + crawling_error_count
print(
    f"crawling success rate: {round(crawling_success_count / crawling_number * 100)}% ({crawling_success_count}/{crawling_number})")

cursor.close()  # Close the cursor
cnx.close()  # Close the connection
