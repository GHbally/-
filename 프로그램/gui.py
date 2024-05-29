import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import gasstation  # gasstation.py 모듈 임포트
import googlemap  # googlemap.py 모듈 임포트
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# API 키 설정 (여기에 실제 API 키를 입력해야 합니다)
GASSTATION_API_KEY = "F240513145"

# 창 설정
root = tk.Tk()
root.title("프로그램 GUI")
root.geometry("800x600")  # 크기를 더 크게 설정하여 지도가 표시될 공간을 확보
root.configure(bg='white')  # 창 배경색을 흰색으로 설정

map_label = None  # 전역 변수로 선언

# 이미지 불러오기
search_icon = Image.open("image/찾기.png").resize((100, 100), Image.LANCZOS)
favorite_icon = Image.open("image/즐겨찾기.png").resize((100, 100), Image.LANCZOS)
chart_icon = Image.open("image/그래프.png").resize((100, 100), Image.LANCZOS)
mail_icon = Image.open("image/메일.png").resize((100, 100), Image.LANCZOS)
main_image = Image.open("image/메인.png").resize((400, 400), Image.LANCZOS)
favorite_on_icon = Image.open("image/즐겨찾기.png").resize((20, 20), Image.LANCZOS)
favorite_off_icon = Image.open("image/즐겨찾기off.png").resize((20, 20), Image.LANCZOS)
search_photo = ImageTk.PhotoImage(search_icon)
favorite_photo = ImageTk.PhotoImage(favorite_icon)
chart_photo = ImageTk.PhotoImage(chart_icon)
mail_photo = ImageTk.PhotoImage(mail_icon)
main_photo = ImageTk.PhotoImage(main_image)
favorite_on_photo = ImageTk.PhotoImage(favorite_on_icon)
favorite_off_photo = ImageTk.PhotoImage(favorite_off_icon)
# 프레임 설정
left_frame = tk.Frame(root, width=100, bg='white')
left_frame.pack(side='left', fill='y')

right_frame = tk.Frame(root, bg='white')
right_frame.pack(side='right', expand=True, fill='both')

# 검색 결과 리스트
search_results = []
favorite_stations = []  # 즐겨찾기 리스트

# 검색 결과를 클릭했을 때의 동작
def on_result_click(id):
    global map_label  # 전역 변수로 선언
    station_info = gasstation.get_gas_station_info(api_key=GASSTATION_API_KEY, station_id=id)
    station_info['id'] = id  # station_info에 'id' 키 추가
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
    print(favorite_stations)


def show_chart():
    global map_label  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        if widget != map_label:  # map_label을 삭제하지 않도록 예외 처리
            widget.destroy()
    if map_label:
        map_label.destroy()
        map_label = None  # map_label을 None으로 설정

    # 평균가 정보 가져오기
    avg_prices = gasstation.get_avg_prices(api_key=GASSTATION_API_KEY, station_id=id)

    # 휘발유와 경유 평균 가격 추출
    gasoline_price = None
    diesel_price = None
    date_str = None

    for avg in avg_prices:
        if avg['product_name'] == '휘발유':
            gasoline_price = avg['price']
            date_str = avg['date']  # 날짜는 동일하므로 한번만 추출
        elif avg['product_name'] == '자동차용경유':
            diesel_price = avg['price']

    if date_str:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]

    # 화면 위쪽에 평균가 정보 표시
    top_frame = tk.Frame(right_frame, bg='white')
    top_frame.pack(side='top', fill='x', padx=10, pady=10)

    if date_str:
        current_price_label = tk.Label(top_frame, text=f"{year}년 {month}월 {day}일 전국 일일 평균 주유소 가격", font=("Helvetica", 14), bg='white')
        current_price_label.pack()

    gasoline_frame = tk.Frame(top_frame, bg='white')
    gasoline_frame.pack(side='top', fill='x', padx=10, pady=5)

    diesel_frame = tk.Frame(top_frame, bg='white')
    diesel_frame.pack(side='top', fill='x', padx=10, pady=5)

    if gasoline_price:
        gasoline_label = tk.Label(gasoline_frame, text=f"휘발유 평균 가격: {gasoline_price}원", font=("Helvetica", 14), bg='white')
        gasoline_label.pack(side='left', padx=10)

    if diesel_price:
        diesel_label = tk.Label(diesel_frame, text=f"경유 평균 가격: {diesel_price}원", font=("Helvetica", 14), bg='white')
        diesel_label.pack(side='left', padx=10)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # # 7일간 전국 휘발유 평균 가격 그래프
    gasoline_history = gasstation.get_price_history_gasoline(api_key=GASSTATION_API_KEY)
    diesel_history = gasstation.get_price_history_disel(api_key=GASSTATION_API_KEY)
    print(gasoline_history)
    print(diesel_history)
    # gasoline_dates = [entry['date'] for entry in gasoline_history]
    # gasoline_prices = [entry['price'] for entry in gasoline_history]
    #
    # diesel_dates = [entry['date'] for entry in diesel_history]
    # diesel_prices = [entry['price'] for entry in diesel_history]
    #
    # # 휘발유 평균 가격 그래프
    # ax1.plot(gasoline_dates, gasoline_prices, label='휘발유 평균 가격')
    # ax1.set_title('7일간 전국 휘발유 평균 가격')
    # ax1.set_xlabel('날짜')
    # ax1.set_ylabel('가격 (원)')
    # ax1.legend()
    #
    # # 경유 평균 가격 그래프
    # ax2.plot(diesel_dates, diesel_prices, label='경유 평균 가격', color='orange')
    # ax2.set_title('7일간 전국 경유 평균 가격')
    # ax2.set_xlabel('날짜')
    # ax2.set_ylabel('가격 (원)')
    # ax2.legend()

    fig.autofmt_xdate()

    canvas = FigureCanvasTkAgg(fig, master=top_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
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

def toggle_favorite(station_info, button):
    station_id = station_info["id"]
    if any(station["id"] == station_id for station in favorite_stations):
        favorite_stations[:] = [station for station in favorite_stations if station["id"] != station_id]
        button.config(image=favorite_off_photo)
        messagebox.showinfo("즐겨찾기", "즐겨찾기에서 제거되었습니다.")
    else:
        favorite_stations.append(station_info)
        button.config(image=favorite_on_photo)
        messagebox.showinfo("즐겨찾기", "즐겨찾기에 추가되었습니다.")

def show_station_info(station_info):
    global map_label  # 전역 변수로 선언

    info_frame = tk.Frame(right_frame, bg='lightgray')
    info_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")  # 기존의 검색 결과 프레임 아래에 배치

    top_label = tk.Label(info_frame, text="주유소 정보", font=("Helvetica", 20), bg='lightgray')
    top_label.grid(row=0, column=0, columnspan=2, pady=10)

    if station_info["id"] in favorite_stations:
        favorite_state_button = tk.Button(info_frame, image=favorite_on_photo,
                                    command=lambda: toggle_favorite(station_info, favorite_state_button))
    else:
        favorite_state_button = tk.Button(info_frame, image=favorite_off_photo,
                                    command=lambda: toggle_favorite(station_info, favorite_state_button))
    favorite_state_button.grid(row=0, column=1, padx=10, pady=10, sticky='ne')

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
            label = tk.Label(info_frame, text=label_text, bg='lightgray')
            label.grid(row=i + 1, column=0, padx=10, pady=5, sticky='w')

            info_label = tk.Label(info_frame, text=info_text, bg='lightgray')
            info_label.grid(row=i + 1, column=1, padx=10, pady=5, sticky='w')

    # 지도 표시용 레이블 (상세 정보 오른쪽에 배치)
    if map_label is None:
        map_label = tk.Label(right_frame)
        map_label.grid(row=2, column=1, columnspan=1, sticky="nsew")

# 지도 표시용 레이블 (상세 정보 오른쪽에 배치)
map_label = tk.Label(right_frame)
map_label.grid(row=2, column=1, columnspan=1, sticky="nsew")

# 기본 메인 화면에 이미지 표시
def show_main_image():
    global map_label
    for widget in right_frame.winfo_children():
        if widget != map_label:  # map_label을 삭제하지 않도록 예외 처리
            widget.destroy()
    if map_label:
        map_label.destroy()
        map_label = None  # map_label을 None으로 설정

    main_image_label = tk.Label(right_frame, image=main_photo)
    main_image_label.pack(expand=True)

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
show_main_image()

root.mainloop()