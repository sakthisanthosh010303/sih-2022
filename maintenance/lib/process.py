# Author: Sakthi Santhosh
# Created on: 28/08/2022
#
# Smart India Hackathon
def run(channel, state) -> int:
    try:
        IO_USERNAME, IO_KEY = open("./assets/credentials.txt", 'r').read().strip().split()
    except FileNotFoundError:
        print("Fatal: Credential file not found.")
        return 1

    from json import dumps
    from requests import post

    feed = "smart-india-hackathon."
    if channel == 8:
        feed += "indicator-1"
    elif channel == 10:
        feed += "indicator-2"
    elif channel == 12:
        feed += "indicator-3"
    elif channel == 16:
        feed += "indicator-4"

    # Upload data to Adafruit IO.
    HEADERS = {
        "X-AIO-Key": IO_KEY,
        "Content-Type": "Application/JSON"
    }
    BASE_URL = "https://io.adafruit.com/api/v2/%s/feeds/%s/data"%(IO_USERNAME, feed)
    DATA = {"value": 0 if state else 1}

    request_handle = post(
        url=BASE_URL,
        headers=HEADERS,
        data=dumps(DATA)
    )

    print("Sent:", DATA)
    print("Received:", request_handle.text)
    print("Response:", request_handle.status_code)

    request_handle.close()
    return 0
