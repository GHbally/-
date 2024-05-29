# chart 추가 전 기존 GUI

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import gasstation  # gasstation.py 모듈 임포트
import googlemap  # googlemap.py 모듈 임포트

# API 키 설정 (여기에 실제 API 키를 입력해야 합니다)
GASSTATION_API_KEY = "F240513145"

# 창 설정
root = tk.Tk()
root.title("프로그램 GUI")
root.geometry("800x600")  # 크기를 더 크게 설정하여 지도가 표시될 공간을 확보
map_label = None  # 전역 변수로 선언

# 이미지 불러오기
search_icon = Image.open("image/찾기.png").resize((100, 100), Image.LANCZOS)
favorite_icon = Image.open("image/즐겨찾기.png").resize((100, 100), Image.LANCZOS)
chart_icon = Image.open("image/그래프.png").resize((100, 100), Image.LANCZOS)
mail_icon = Image.open("image/메일.png").resize((100, 100), Image.LANCZOS)

search_photo = ImageTk.PhotoImage(search_icon)
favorite_photo = ImageTk.PhotoImage(favorite_icon)
chart_photo = ImageTk.PhotoImage(chart_icon)
mail_photo = ImageTk.PhotoImage(mail_icon)

# 프레임 설정
left_frame = tk.Frame(root, width=100, bg='white')
left_frame.pack(side='left', fill='y')

right_frame = tk.Frame(root, bg='white')
right_frame.pack(side='right', expand=True, fill='both')

# 검색 결과 리스트
search_results = []

# 검색 결과를 클릭했을 때의 동작
def on_result_click(id):
    global map_label  # 전역 변수로 선언
    station_info = gasstation.get_gas_station_info(api_key=GASSTATION_API_KEY, station_id=id)
    show_station_info(station_info)
    print(station_info["gis_x"], station_info["gis_y"])
    lat, lon = gasstation.katec_to_wgs84(float(station_info["gis_x"]), float(station_info["gis_y"]))
    print(lat, lon)

    if map_label is None:
        map_label = tk.Label(right_frame)
        map_label.grid(row=2, column=1, columnspan=1, sticky="nsew")
    googlemap.update_map(map_label, lat, lon)

# 검색 버튼 눌렀을 때의 동작
def show_search():
    global map_label  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        if widget != map_label:  # map_label을 삭제하지 않도록 예외 처리
            widget.destroy()

    # 검색 결과 프레임 생성
    results_frame = tk.Frame(right_frame)
    results_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

    top_label = tk.Label(results_frame, text="검색 (지역 검색)", font=("Helvetica", 14))
    top_label.grid(row=0, column=0, columnspan=2, pady=10)

    search_entry = tk.Entry(results_frame, width=50)
    search_entry.grid(row=1, column=0, padx=10, pady=10)

    def perform_search():
        query = search_entry.get()
        if query:
            # Geopy를 사용하여 지역명을 위도, 경도로 변환
            coords = gasstation.geocoding(query)
            if coords:
                lat, lon = coords['lat'], coords['lng']
                print(f"Geocoded Coordinates: Latitude={lat}, Longitude={lon}")
                gas_stations = gasstation.get_gas_stations(GASSTATION_API_KEY, lat, lon)
                if gas_stations:
                    update_search_results(gas_stations)
                    search_results = gas_stations
                    print("fsafsa",search_results)
                else:
                    messagebox.showerror("오류", "주유소 정보를 가져오는 데 실패했습니다.")
            else:
                messagebox.showerror("오류", "지역명을 찾을 수 없습니다.")

    search_button = tk.Button(results_frame, text="검색", command=perform_search)
    search_button.grid(row=1, column=1, padx=10, pady=10)

    def update_search_results(gas_stations):
        gas_station_names = [station["name"] for station in gas_stations]
        combo = ttk.Combobox(results_frame, values=gas_station_names, state="readonly")
        combo.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='w')

        def on_combo_select(event):
            selected_index = combo.current()
            if selected_index >= 0:
                selected_station = gas_stations[selected_index]
                on_result_click(selected_station['id'])

        combo.bind("<<ComboboxSelected>>", on_combo_select)

    update_search_results([])

def show_favorite():
    global map_label  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        if widget != map_label:  # map_label을 삭제하지 않도록 예외 처리
            widget.destroy()
    if map_label:
        map_label.destroy()
        map_label = None  # map_label을 None으로 설정
    label = tk.Label(right_frame, text="즐겨찾기 화면")
    label.pack()

def show_chart():
    global map_label  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        if widget != map_label:  # map_label을 삭제하지 않도록 예외 처리
            widget.destroy()
    if map_label:
        map_label.destroy()
        map_label = None  # map_label을 None으로 설정
    label = tk.Label(right_frame, text="차트 화면")
    label.pack()

def show_mail():
    global map_label  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        if widget != map_label:  # map_label을 삭제하지 않도록 예외 처리
            widget.destroy()
    if map_label:
        map_label.destroy()
        map_label = None  # map_label을 None으로 설정
    label = tk.Label(right_frame, text="메일 화면")
    label.pack()

def show_station_info(station_info):
    global map_label  # 전역 변수로 선언

    info_frame = tk.Frame(right_frame, bg='white')
    info_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")  # 기존의 검색 결과 프레임 아래에 배치

    top_label = tk.Label(info_frame, text="주유소 상세 정보", font=("Helvetica", 14))
    top_label.grid(row=0, column=0, columnspan=2, pady=10)

    info_labels = [
        ("상호", station_info["name"]),
        ("도로명주소", station_info.get("address", "N/A")),  # 수정된 부분
        ("전화번호", station_info["tel"]),
        ("휘발유 가격", station_info["oil_price"]),
        ("제품 코드", station_info["product_code"]),
        ("기준 일자", station_info["trade_date"]),
        ("기준 시간", station_info["trade_time"])
    ]

    for i, (label_text, info_text) in enumerate(info_labels):
        if label_text not in ("GIS X 좌표", "GIS Y 좌표"):  # GIS X, Y 좌표 부분 제외
            label = tk.Label(info_frame, text=label_text)
            label.grid(row=i + 1, column=0, padx=10, pady=5, sticky='w')

            info_label = tk.Label(info_frame, text=info_text)
            info_label.grid(row=i + 1, column=1, padx=10, pady=5, sticky='w')

    # 지도 표시용 레이블 (상세 정보 오른쪽에 배치)
    if map_label is None:
        map_label = tk.Label(right_frame)
        map_label.grid(row=2, column=1, columnspan=1, sticky="nsew")

# 지도 표시용 레이블 (상세 정보 오른쪽에 배치)
map_label = tk.Label(right_frame)
map_label.grid(row=2, column=1, columnspan=1, sticky="nsew")

# 버튼 추가
search_button = tk.Button(left_frame, image=search_photo, command=show_search)
search_button.pack(pady=20)

favorite_button = tk.Button(left_frame, image=favorite_photo, command=show_favorite)
favorite_button.pack(pady=20)

chart_button = tk.Button(left_frame, image=chart_photo, command=show_chart)
chart_button.pack(pady=20)

mail_button = tk.Button(left_frame, image=mail_photo, command=show_mail)
mail_button.pack(pady=20)

# 기본 화면 설정
show_search()

root.mainloop()
