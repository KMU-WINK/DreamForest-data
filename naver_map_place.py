import requests
from requests_html import HTMLSession
import pytz

import json
from datetime import datetime


def get_search_list(search_keyword, language="ko"):
    with HTMLSession() as s:
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": f"{language}",
            "Content-Type": "application/json",
        }

        url = f"https://map.naver.com/v5/api/search?caller=pcweb&query={search_keyword}"
        print("url:", url)

        result = s.get(url, headers=headers)
        if result.status_code == 200:
            return json.loads(result.text)
        else:
            raise Exception(f"Error: {result.status_code}")


def get_first_place_id(place_json_data):
    place_result = place_json_data['result']['place']
    if place_result is None:
        return None
    first_place_id = place_result['list'][0]['id']
    return first_place_id


def get_store_info(place_id, language="ko"):
    with HTMLSession() as s:
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": f"{language}",
            "Content-Type": "application/json",
        }

        result = s.get(f"https://map.naver.com/v5/api/sites/summary/{place_id}",
                       headers=headers)

        if result.status_code == 200:
            return json.loads(result.text)
        else:
            raise Exception(f"Error: {result.status_code}")


def parsing_store_info(place_info):
    parsing_place = {}

    get_naver_keys = ["name", "x", "y", "address", "phone", "categories", "bizHour", "menus", "menuImages",
                      "reviewCount"]

    my_column_keys = ["naver_store_name", "naver_x", "naver_y", "naver_parcel_address", "naver_phone",
                      "naver_categories",
                      "naver_biz_hour", "naver_menus", "naver_menu_images",
                      "naver_blog_review_count"]
    # Initialize the parsing_place dictionary with the keys
    for my_key in my_column_keys:
        parsing_place[my_key] = None

    for i in range(len(get_naver_keys)):
        naver_key = get_naver_keys[i]
        my_key = my_column_keys[i]

        value = place_info[naver_key]

        if type(value) == list and len(value) == 0:
            continue
        if value is None or value == '' or value == ' ' or value == 'None' or value == '[]':
            continue

        if naver_key == "menuImages":
            menu_images = []
            for menu_image in value:
                menu_images.append(menu_image["imageUrl"])
            parsing_place[my_key] = json.dumps(menu_images, ensure_ascii=False)
            continue

        if type(value) == list or type(value) == dict:
            value = json.dumps(value, ensure_ascii=False)

        parsing_place[my_key] = value

    return parsing_place


def get_review(place_id, language="ko"):
    with HTMLSession() as s:
        data = [
            {
                "operationName": "getVisitorReviews",
                "variables": {
                    "input": {
                        "businessId": f"{place_id}",
                        "bookingBusinessId": None,
                        "businessType": "restaurant",
                        "size": 3,
                        "page": 1,
                        "includeContent": True,
                        "cidList": [
                            "220036",
                            "220037",
                            "220053",
                            "1004760",
                            "1004452"
                        ]
                    }
                },
                "query": "query getVisitorReviews($input: VisitorReviewsInput) {\n  visitorReviews(input: $input) {\n    items {\n      id\n      rating\n      author {\n        id\n        nickname\n        from\n        imageUrl\n        objectId\n        url\n        review {\n          totalCount\n          imageCount\n          avgRating\n          __typename\n        }\n        theme {\n          totalCount\n          __typename\n        }\n        __typename\n      }\n      body\n      thumbnail\n      media {\n        type\n        thumbnail\n        __typename\n      }\n      tags\n      status\n      visitCount\n      viewCount\n      visited\n      created\n      reply {\n        editUrl\n        body\n        editedBy\n        created\n        replyTitle\n        isReported\n        isSuspended\n        __typename\n      }\n      originType\n      item {\n        name\n        code\n        options\n        __typename\n      }\n      isFollowing\n      language\n      highlightOffsets\n      translatedText\n      businessName\n      receiptInfoUrl\n      __typename\n    }\n    starDistribution {\n      score\n      count\n      __typename\n    }\n    hideProductSelectBox\n    total\n    __typename\n  }\n}\n"
            },
            {
                "operationName": "getVisitorReviewStats",
                "variables": {
                    "businessType": "restaurant",
                    "id": f"{place_id}",
                    "itemId": "0"
                },
                "query": "query getVisitorReviewStats($id: String, $itemId: String, $businessType: String = \"place\") {\n  visitorReviewStats(input: {businessId: $id, itemId: $itemId, businessType: $businessType}) {\n    id\n    name\n    apolloCacheId\n    review {\n      avgRating\n      totalCount\n      scores {\n        count\n        score\n        __typename\n      }\n      starDistribution {\n        count\n        score\n        __typename\n      }\n      imageReviewCount\n      authorCount\n      maxSingleReviewScoreCount\n      maxScoreWithMaxCount\n      __typename\n    }\n    analysis {\n      themes {\n        code\n        label\n        count\n        __typename\n      }\n      menus {\n        label\n        count\n        __typename\n      }\n      votedKeyword {\n        totalCount\n        reviewCount\n        userCount\n        details {\n          category\n          code\n          iconUrl\n          iconCode\n          displayName\n          count\n          previousRank\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    visitorReviewsTotal\n    ratingReviewsTotal\n    __typename\n  }\n}\n"
            },
            {
                "operationName": "getVisitorReviewStats",
                "variables": {
                    "businessType": "restaurant",
                    "id": f"{place_id}",
                },
                "query": "query getVisitorReviewStats($id: String, $itemId: String, $businessType: String = \"place\") {\n  visitorReviewStats(input: {businessId: $id, itemId: $itemId, businessType: $businessType}) {\n    id\n    name\n    apolloCacheId\n    review {\n      avgRating\n      totalCount\n      scores {\n        count\n        score\n        __typename\n      }\n      starDistribution {\n        count\n        score\n        __typename\n      }\n      imageReviewCount\n      authorCount\n      maxSingleReviewScoreCount\n      maxScoreWithMaxCount\n      __typename\n    }\n    analysis {\n      themes {\n        code\n        label\n        count\n        __typename\n      }\n      menus {\n        label\n        count\n        __typename\n      }\n      votedKeyword {\n        totalCount\n        reviewCount\n        userCount\n        details {\n          category\n          code\n          iconUrl\n          iconCode\n          displayName\n          count\n          previousRank\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    visitorReviewsTotal\n    ratingReviewsTotal\n    __typename\n  }\n}\n"
            },
            {
                "operationName": "getUgcReviewList",
                "variables": {
                    "businessId": f"{place_id}",
                },
                "query": "query getUgcReviewList($businessId: String) {\n  restaurant(id: $businessId, isNx: false, deviceType: \"mobile\") {\n    fsasReviews {\n      ...FsasReviews\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment FsasReviews on FsasReviewsResult {\n  total\n  maxItemCount\n  items {\n    name\n    type\n    typeName\n    url\n    home\n    id\n    title\n    rank\n    contents\n    bySmartEditor3\n    hasNaverReservation\n    thumbnailUrl\n    thumbnailUrlList\n    thumbnailCount\n    date\n    isOfficial\n    isRepresentative\n    profileImageUrl\n    isVideoThumbnail\n    reviewId\n    authorName\n    createdString\n    __typename\n  }\n  __typename\n}\n"
            },
            {
                "operationName": "getVisitorReviewPhotosInVisitorReviewTab",
                "variables": {
                    "businessId": f"{place_id}",
                    "businessType": "restaurant",
                    "page": 1,
                    "display": 20
                },
                "query": "query getVisitorReviewPhotosInVisitorReviewTab($businessId: String!, $businessType: String, $page: Int, $display: Int, $theme: String, $item: String) {\n  visitorReviews(input: {businessId: $businessId, businessType: $businessType, page: $page, display: $display, theme: $theme, item: $item, isPhotoUsed: true}) {\n    items {\n      id\n      rating\n      author {\n        id\n        nickname\n        from\n        imageUrl\n        objectId\n        url\n        __typename\n      }\n      body\n      thumbnail\n      media {\n        type\n        thumbnail\n        __typename\n      }\n      tags\n      status\n      visited\n      originType\n      item {\n        name\n        code\n        options\n        __typename\n      }\n      businessName\n      isFollowing\n      visitCount\n      votedKeywords {\n        code\n        iconUrl\n        iconCode\n        displayName\n        __typename\n      }\n      __typename\n    }\n    starDistribution {\n      score\n      count\n      __typename\n    }\n    hideProductSelectBox\n    total\n    __typename\n  }\n}\n"
            },
            {
                "operationName": "useBusiness",
                "variables": {
                    "id": f"{place_id}",
                    "isNx": False
                },
                "query": "query useBusiness($id: String, $isNx: Boolean) {\n  restaurant(id: $id, isNx: $isNx, deviceType: \"mobile\") {\n    kinQna {\n      answerCount\n      answerList {\n        detailUrl\n        writeTime\n        contents\n        questionTitle\n        thumbnailUrl\n        dirId\n        __typename\n      }\n      profileUrl\n      __typename\n    }\n    __typename\n  }\n}\n"
            }
        ]
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": f"{language}",
            "Content-Type": "application/json",
            "referer": f"https://pcmap.place.naver.com/restaurant/{place_id}/home"
        }
        result = s.post('https://pcmap-api.place.naver.com/graphql', headers=headers,
                        data=json.dumps(data, ensure_ascii=False)).text
        json_result = json.loads(result)
        return json_result


def parsing_review(json_reviews):
    all_reviews = []
    review_id_set = set()

    review_stats = {}

    for review in json_reviews:
        data_obj = review["data"]

        if "visitorReviewStats" in data_obj:
            if data_obj["visitorReviewStats"] is not None:
                review_obj = data_obj["visitorReviewStats"]["review"]
                review_stats["naver_average_rating"] = review_obj["avgRating"]
                review_stats["naver_visit_review_count"] = review_obj["totalCount"]

        if "visitorReviews" not in data_obj.keys():
            continue

        items = data_obj["visitorReviews"]["items"]

        for item in items:
            review_data = {}
            review_id = item["id"]

            if review_id in review_id_set:
                continue

            review_id_set.add(review_id)
            review_data["review_id"] = review_id
            review_data["rating"] = item["rating"]
            user_data = item["author"]

            review_data["user_id"] = user_data["id"]
            review_data["user_nickname"] = user_data["nickname"]
            review_data["user_from"] = user_data["from"]
            review_data["user_image_url"] = user_data["imageUrl"]
            review_data["user_object_id"] = user_data["objectId"]
            review_data["user_url"] = user_data["url"]

            review_data["review_body"] = item["body"]
            review_image_data = item["media"]

            review_data["review_image"] = None
            review_image_list = []
            for media_index in range(len(review_image_data)):
                review_image_list.append(review_image_data[media_index]["thumbnail"])
                review_data["review_image"] = json.dumps(review_image_list, ensure_ascii=False)

            visited_date = item["visited"][0:-2]

            try:
                review_data["visit_date"] = datetime.strptime(visited_date, "%y.%m.%d")
            except ValueError:

                kst = pytz.timezone('Asia/Seoul')  # Create a timezone object for KST
                korea_current_datetime = datetime.now(tz=kst)  # Get the current date and time in KST
                korea_current_year = korea_current_datetime.year  # Get the current year

                review_data["visit_date"] = datetime.strptime(visited_date, "%m.%d").replace(year=korea_current_year)

            review_data["visit_type"] = item["originType"]
            review_data["visit_count"] = item["visitCount"]

            all_reviews.append(review_data)
    return review_stats, all_reviews


if __name__ == '__main__':
    search_keyword = '서울 강남구 역삼동 짜짜루'
    # search_keyword = '서울 강남구 논현동 씨유 논현역드림점'
    # search_keyword = '서울 강남구 역삼동 스무디킹 강남역점'

    place_search_data = get_search_list(search_keyword)
    print("place_search_data:", place_search_data)

    place_id = get_first_place_id(place_search_data)
    print("place_id:", place_id)

    if place_id is not None:
        place_info = get_store_info(place_id)
        print("place_info:", place_info)

        parsing_place = parsing_store_info(place_info)
        print("parsing_place:", parsing_place)

        review_data = get_review(place_id)
        print("review_data:", review_data)

        review_stats, parsing_reviews = parsing_review(review_data)
        print("review_stats:", review_stats)
        print("parsing_reviews:", parsing_reviews)
