import mysql.connector
import re

from naver_map_place import get_search_list, get_first_place_id, get_store_info
import secret_key


def remove_parentheses(string):
    return re.sub(r"\([^)]*\)", "", string)


def printInfo(place_info, string):
    value = place_info[string]

    if type(value) == list and len(value) == 0:
        return -1
    if value is None or value == '' or value == ' ' or value == 'None' or value == '[]':
        return -1

    print(f"{string}: {place_info[string]}")


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
        continue

    dong_address = dong_match.group(1)

    # search_keyword = '짜짜루 서울 강남구 역삼동'
    search_keyword = f"{dong_address} {remove_parentheses(store_name)}"
    print("search_keyword:", search_keyword)

    try:
        place_json_data = get_search_list(search_keyword)
        place_id = get_first_place_id(place_json_data)
        print("place_id:", place_id)
        place_info = get_store_info(place_id)

        printInfo(place_info, "name")
        printInfo(place_info, "x")
        printInfo(place_info, "y")
        printInfo(place_info, "address")
        printInfo(place_info, "phone")
        printInfo(place_info, "categories")
        printInfo(place_info, "bizHour")
        printInfo(place_info, "menus")
        printInfo(place_info, "menuImages")
        printInfo(place_info, "reviewCount")
        crawling_success_count += 1


    except:
        print("crawling error")
        crawling_error_count += 1
        pass

    print("\n")

cursor.close()  # Close the cursor
cnx.close()  # Close the connection
