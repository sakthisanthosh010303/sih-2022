# Author: Sakthi Santhosh
# Created on: 25/08/2022
#
# Smart India Hackathon
def run(_) -> int:
    from datetime import datetime
    from os import path, SEEK_CUR, SEEK_END
    from picamera import PiCamera, PiCameraError
    from serial import Serial, SerialException

    date, time = datetime.now().strftime("%d-%m-%Y %H:%M:%S").split()
    last_data = []
    last_flag = False

    if not path.exists("./assets/locations/%s.txt"%(date)):
        open("./assets/locations/%s.txt"%(date), 'w').close()

    # Fetch last data point.
    with open("./assets/locations/%s.txt"%(date), "rb") as file_handle:
        try:
            file_handle.seek(-2, SEEK_END)
            while file_handle.read(1) != b'\n':
                file_handle.seek(-2, SEEK_CUR)
            last_data = file_handle.read().decode().strip().split()
        except:
            pass
        print("Last data:", last_data)

    if last_data:
        last_flag = True
        last_datetime = ' '.join(last_data[:2])
        last_latitude, last_longitude = float(last_data[2]), float(last_data[3])

    # Initialize serial port.
    try:
        serial_handle = Serial(port="/dev/ttyS0", baudrate=9600)
    except SerialException:
        print("Fatal: Failed to open port.")
        return 1

    # Initialize camera.
    try:
        camera_handle = PiCamera(resolution=(640, 360))
    except PiCameraError:
        print("Fatal: Failed to initialize camera.")
        return 1

    # Get location.
    location_flag = False
    retries = 30
    while retries > 0:
        line = serial_handle.readline().decode()
        if line[:6] == "$GPGGA":
            break
        retries -= 1
    line = line.split(',')

    if line[2] != '':
        latitude = float(line[2][:2]) + float(line[2][2:]) / 60
        longitude = float(line[4][:3]) + float(line[4][3:]) / 60
        location_flag = True

    serial_handle.close()

    IO_USERNAME, IO_KEY = open("./assets/credentials/adafruit.txt").read().strip().split()

    LOCATION_FEED = "smart-india-hackathon.location"
    IMAGE_FEED = "smart-india-hackathon.image"
    SPEED_FEED = "smart-india-hackathon.speed"

    HEADERS = {
        "X-AIO-Key": IO_KEY,
        "Content-Type": "Application/JSON"
    }
    BASE_URL = "https://io.adafruit.com/api/v2/%s/feeds/%s/data"

    # Capture image.
    from base64 import b64encode
    from io import BytesIO
    from json import dumps
    from PIL import Image, ImageDraw
    from requests import post

    IMAGE_LOC = "./assets/images/" + "%s %s.jpeg"%(date, time)

    stream_handle = BytesIO()

    camera_handle.capture(stream_handle, format="jpeg")
    camera_handle.close()

    # Location
    if location_flag:
        WRITE_TEXT = date + ' ' + time + ' ' + latitude + ' ' + longitude

        # Calculate distance and time.
        if last_flag:
            from geopy import distance

            last_datetime = last_data[0] + ' ' + last_data[1]
            distance_delta = distance.geodesic(
                (last_latitude, last_longitude),
                (latitude, longitude)
            ).km
            time_delta = (datetime.strptime(
                date + ' ' + time,
                "%d-%m-%Y %H:%M:%S"
            ) - datetime.strptime(
                last_datetime,
                "%d-%m-%Y %H:%M:%S"
            )).total_seconds() / 60

            print("\nDistance:", distance_delta)
            print("Time:", time_delta)

            data = {
                "value": str(distance_delta / time_delta)
            }

            # Upload speed to Adafruit IO.
            request_handle = post(
                url=BASE_URL%(IO_USERNAME, SPEED_FEED),
                headers=HEADERS,
                data = dumps(data)
            )

            print("\nReceived:", request_handle.text)
            print("Response:", request_handle.status_code)

            request_handle.close()

        # Log location locally.
        with open("./assets/locations/%s.txt"%(date), 'a') as file_handle:
            file_handle.write(WRITE_TEXT + '\n')

        # Add location tag to images.
        image_handle = Image.open(stream_handle)
        draw_handle = ImageDraw.Draw(image_handle)

        draw_handle.text(
            (10, 10),
            WRITE_TEXT,
            fill=(255, 255, 255)
        )

        # Upload location to Adafruit IO.
        data = {
            "value": "0.0",
            "lat": latitude,
            "lon": longitude
        }
        request_handle = post(
             url=BASE_URL%(IO_USERNAME, LOCATION_FEED),
             headers=HEADERS,
             data=dumps(data)
        )

        print("\nReceived:", request_handle.text)
        print("Response:", request_handle.status_code)

    image_handle.save(IMAGE_LOC, optimize=True, quality=50)

    # Upload image to Adafruit IO.
    data = {
        "value": b64encode(open(IMAGE_LOC, "rb").read()).decode()
    }
    request_handle = post(
        url=BASE_URL%(IO_USERNAME, IMAGE_FEED),
        headers=HEADERS,
        data=dumps(data)
    )

    print("\nResponse:", request_handle.status_code)

    # Upload image to Google Drive.
    BASE_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    ACCESS_TOKEN = open("./assets/credentials/drive.txt", 'r').read().strip()
    HEADERS = {"Authorization": "Bearer " + ACCESS_TOKEN}

    METADATA = {
        "name": date + ' ' + time,
        "parents": ["13jEg05lZe1qF-x94Yhv5h3QfqayXZ63c"] # Get folder ID from URL.
    }
    DATA = {
        "data": ("metadata", dumps(METADATA), "application/json; charset=UTF-8"),
        "file": ("image/png", open(IMAGE_LOC, "rb"))
    }

    request_handle = post(
        url=BASE_URL,
        headers=HEADERS,
        files=DATA
    )

    print("\nReceived:", request_handle.text, end='')
    print("Response:", request_handle.status_code)

    request_handle.close()
    return 0
