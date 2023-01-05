import mysql.connector
import re

from naver_map_place import get_search_list, get_first_place_id, get_store_info, parsing_store_info
import secret_key


def remove_parentheses(string):
    return re.sub(r"\([^)]*\)", "", string)


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

        place_json_data = get_search_list(search_keyword)
        place_id = get_first_place_id(place_json_data)
        print("place_id:", place_id)

        if place_id is None:
            print("네이버 지도에서 장소를 찾지 못해 다른 키워드로 재검색합니다.")
            print()
            continue

        else:
            place_info = get_store_info(place_id)

            parsing_place = parsing_store_info(place_info)
            print("parsing_place:", parsing_place)

            print("\n")
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
