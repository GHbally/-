import requests
import xml.etree.ElementTree as ET
from geopy.geocoders import Nominatim
from pyproj import Proj, Transformer

def katec_to_wgs84(x, y):
    # KATEC 설정
    KATEC = Proj(
        proj='tmerc',
        lat_0=38,
        lon_0=128,
        k=0.9999,
        x_0=400000,
        y_0=600000,
        ellps='bessel',
        towgs84='-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43'
    )

    # WGS84 설정
    WGS84 = Proj(proj='latlong', datum='WGS84', ellps='WGS84')

    # Transformer 생성
    transformer = Transformer.from_proj(KATEC, WGS84, always_xy=True)

    # 좌표 변환
    lon, lat = transformer.transform(x, y)
    return lat, lon


def wgs84_to_katec(lat, lon):
    # WGS84 설정
    WGS84 = Proj(proj='latlong', datum='WGS84', ellps='WGS84')

    # KATEC 설정
    KATEC = Proj(
        proj='tmerc',
        lat_0=38,
        lon_0=128,
        k=0.9999,
        x_0=400000,
        y_0=600000,
        ellps='bessel',
        towgs84='-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43'
    )

    # Transformer 생성
    transformer = Transformer.from_proj(WGS84, KATEC, always_xy=True)

    # 좌표 변환
    x, y = transformer.transform(lon, lat)
    return x, y

def get_gas_stations(api_key, x, y, radius=5000):
    # WGS84 좌표계를 KATEC 좌표계로 변환
    gis_x, gis_y = wgs84_to_katec(x, y)
    print("Converted KATEC coordinates:", gis_x, gis_y)

    url = "http://www.opinet.co.kr/api/aroundAll.do"
    params = {
        "code": api_key,
        "x": gis_x,
        "y": gis_y,
        "radius": radius,
        "sort": 1,
        "prodcd": "B027",
        "out": "xml"
    }
    response = requests.get(url, params=params)

    # 응답 내용을 출력하여 디버그
    print(f"Request URL: {response.url}")
    print(f"Response Content: {response.content.decode('utf-8')}")

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return []

    gas_stations = []
    for item in root.findall('.//OIL'):
        station = {
            "id":item.findtext('UNI_ID'),
            "name": item.findtext('OS_NM'),
            "price": item.findtext('PRICE'),
            "distance": item.findtext('DISTANCE'),
            "gis_x": item.findtext('GIS_X_COOR'),
            "gis_y": item.findtext('GIS_Y_COOR')
        }
        gas_stations.append(station)

    print("Parsed Gas Stations:", gas_stations)  # 디버깅 메시지 추가
    return gas_stations


def get_gas_station_info(api_key, station_id):
    url = "http://www.opinet.co.kr/api/detailById.do"
    params = {
        "code": api_key,
        "id": station_id,
        "out": "xml"
    }
    response = requests.get(url, params=params)

    # 응답 내용을 출력하여 디버그
    print(f"Request URL: {response.url}")
    print(f"Response Content: {response.content.decode('utf-8')}")

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return None

    station_info = {}
    for item in root.findall('.//OIL'):
        station_info["name"] = item.findtext('OS_NM')
        station_info["address"] = item.findtext('NEW_ADR')
        station_info["tel"] = item.findtext('TEL')
        station_info["gis_x"] = item.findtext('GIS_X_COOR')
        station_info["gis_y"] = item.findtext('GIS_Y_COOR')
        prices = {"B027": "휘발유", "D047": "경유"}
        for oil_price in item.findall('OIL_PRICE'):
            prodcd = oil_price.findtext('PRODCD')
            price = oil_price.findtext('PRICE')
            if prodcd in prices:
                station_info[prices[prodcd] + "_price"] = price
        station_info["trade_date"] = oil_price.findtext('TRADE_DT')
        station_info["trade_time"] = oil_price.findtext('TRADE_TM')

    print("Gas Station Info:", station_info)  # 디버깅 메시지 추가
    return station_info

def geocoding(address):
    geolocator = Nominatim(user_agent="South Korea", timeout=None)
    geo = geolocator.geocode(address)
    if geo is None:
        return None
    crd = {"lat": geo.latitude, "lng": geo.longitude}
    return crd

def get_avg_prices(api_key, station_id):
    url = "http://www.opinet.co.kr/api/avgAllPrice.do"
    params = {
        "code": api_key,
        "out": "xml"
    }
    response = requests.get(url, params=params)

    # 응답 내용을 출력하여 디버그
    print(f"Request URL: {response.url}")
    print(f"Response Content: {response.content.decode('utf-8')}")

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return None

    gas_avg = []
    for item in root.findall('.//OIL'):
        average = {
        "date": item.findtext('TRADE_DT'),
        "product_name" : item.findtext('PRODNM'),
        "price" : item.findtext('PRICE'),
        "diff" : item.findtext('DIFF'),
        }
        gas_avg.append(average)
    print("Gas AVG Info:", gas_avg)  # 디버깅 메시지 추가
    return gas_avg
def get_price_history_gasoline(api_key):
    url = "http://www.opinet.co.kr/api/avgRecentPrice.do"
    params = {
        "code": api_key,
        "out": "xml",
        "date": "",
        "prodcd": "B027"
    }
    response = requests.get(url, params=params)

    # 응답 내용을 출력하여 디버그
    print(f"Request URL: {response.url}")
    print(f"Response Content: {response.content.decode('utf-8')}")

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return None


    gas_history_gasoline = []
    for item in root.findall('.//OIL'):
        history = {
            "date": item.findtext('DATE'),
            "product_code": item.findtext('PRODCD'),
            "price": item.findtext('PRICE'),
        }
        gas_history_gasoline.append(history)

    print("Gas AVG Info:", gas_history_gasoline)  # 디버깅 메시지 추가
    return gas_history_gasoline

def get_price_history_disel(api_key):
    url = "http://www.opinet.co.kr/api/avgRecentPrice.do"
    params = {
        "code": api_key,
        "out": "xml",
        "date": "",
        "prodcd": "D047"
    }
    response = requests.get(url, params=params)

    # 응답 내용을 출력하여 디버그
    print(f"Request URL: {response.url}")
    print(f"Response Content: {response.content.decode('utf-8')}")

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return None


    gas_history_disel = []
    for item in root.findall('.//OIL'):
        history = {
            "date": item.findtext('DATE'),
            "product_code": item.findtext('PRODCD'),
            "price": item.findtext('PRICE'),
        }
        gas_history_disel.append(history)

    print("Gas AVG Info:", gas_history_disel)  # 디버깅 메시지 추가
    return gas_history_disel