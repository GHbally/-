import tkinter as tk
import requests
import io
from PIL import Image, ImageTk
from pyproj import Proj, Transformer

# Google Maps API 키
Google_API_Key = "AIzaSyCzFgc9OGnXckq1-JNhSCVGo9zIq1kSWcE"  # 여기에 새 API 키를 입력하세요
zoom = 16

def update_map(map_label, lat, lon):
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom}&size=400x400&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={Google_API_Key}"
    print(f"Requesting map URL: {map_url}")  # 디버깅을 위한 URL 출력

    response = requests.get(map_url)
    if response.status_code == 200:
        try:
            image = Image.open(io.BytesIO(response.content))
            photo = ImageTk.PhotoImage(image)

            map_label.config(image=photo)
            map_label.image = photo
        except Exception as e:
            print(f"Error loading image: {e}")
    else:
        print(f"Failed to fetch map. Status code: {response.status_code}")
        print(f"Response content: {response.content}")
