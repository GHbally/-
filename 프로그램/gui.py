import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import gasstation  # gasstation.py 모듈 임포트
import googlemap  # googlemap.py 모듈 임포트
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import spam

# API 키 설정 (여기에 실제 API 키를 입력해야 합니다)
GASSTATION_API_KEY = "F240513145"

# 창 설정
root = tk.Tk()
root.title("주유도사")
root.geometry("800x600")  # 크기를 더 크게 설정하여 지도가 표시될 공간을 확보
root.configure(bg='white')  # 창 배경색을 흰색으로 설정

map_label = None  # 전역 변수로 선언

# 이미지 불러오기
search_icon = Image.open("image/찾기.png").resize((100, 100), Image.LANCZOS)
favorite_icon = Image.open("image/즐겨찾기.png").resize((100, 100), Image.LANCZOS)
chart_icon = Image.open("image/그래프.png").resize((100, 100), Image.LANCZOS)
mail_icon = Image.open("image/메일.png").resize((100, 100), Image.LANCZOS)
main_image = Image.open("image/메인.png").resize((600, 712), Image.LANCZOS)
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
left_frame = tk.Frame(root, width=100, bg='lightgray')
left_frame.pack(side='left', fill='y')

right_frame = tk.Frame(root, bg='lightgray')
right_frame.pack(side='right', expand=True, fill='both')

# 검색 결과 리스트
search_results = []
favorite_stations = []  # 즐겨찾기 리스트
map_label = None  # 전역 변수로 선언
info_frame = None  # 전역 변수로 선언

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
    global map_label, info_frame  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        widget.destroy()  # 모든 위젯을 삭제

    if map_label:
        map_label.destroy()
        map_label = None  # map_label을 None으로 설정

    if info_frame:
        info_frame.destroy()
        info_frame = None  # info_frame을 None으로 설정

    # 검색 결과 프레임 생성
    results_frame = tk.Frame(right_frame)
    results_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

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
        for widget in results_frame.winfo_children():
            if widget not in (top_label, search_entry, search_button):
                widget.destroy()

        gas_station_names = [station["name"] for station in gas_stations]
        listbox = tk.Listbox(results_frame, width=50,height=3, selectmode='single')
        listbox.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='w')

        for name in gas_station_names:
            listbox.insert(tk.END, name)

        def on_listbox_select(event):
            selected_index = listbox.curselection()
            if selected_index:
                selected_station = gas_stations[selected_index[0]]
                on_result_click(selected_station['id'])

        listbox.bind("<<ListboxSelect>>", on_listbox_select)

    update_search_results([])


def show_favorite():
    global map_label, info_frame  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        widget.destroy()  # 모든 위젯을 삭제

    # right_frame의 열 구성 설정
    right_frame.columnconfigure(0, weight=1)
    right_frame.columnconfigure(1, weight=2)
    right_frame.rowconfigure(0, weight=1)

    # 즐겨찾기 리스트 프레임 생성
    favorite_frame = tk.Frame(right_frame)
    favorite_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # 즐겨찾기 리스트 박스 생성
    favorite_listbox = tk.Listbox(favorite_frame, width=30, height=20)
    favorite_listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # 선택된 주유소 정보 프레임 생성
    info_frame = tk.Frame(right_frame, bg='white')
    info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def update_info(event):
        selected_index = favorite_listbox.curselection()
        if selected_index:
            selected_station = favorite_stations[selected_index[0]]
            show_station_info1(selected_station)

    favorite_listbox.bind("<<ListboxSelect>>", update_info)

    for station in favorite_stations:
        favorite_listbox.insert(tk.END, station["name"])
def show_station_info1(station_info):
    global map_label, info_frame  # 전역 변수로 선언

    # info_frame을 업데이트 하기 전에 기존 위젯을 삭제
    for widget in info_frame.winfo_children():
        widget.destroy()

    top_label = tk.Label(info_frame, text="주유소 정보", font=("Helvetica", 20), bg='lightgray')
    top_label.grid(row=0, column=0, columnspan=2, pady=10)

    if any(station["id"] == station_info["id"] for station in favorite_stations):
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
        ("휘발유 가격", station_info.get("휘발유_price", "N/A")),
        ("경유 가격", station_info.get("경유_price", "N/A")),
        ("기준 일자", station_info["trade_date"]),
        ("기준 시간", station_info["trade_time"])
    ]

    for i, (label_text, info_text) in enumerate(info_labels):
        if label_text not in ("GIS X 좌표", "GIS Y 좌표"):  # GIS X, Y 좌표 부분 제외
            label = tk.Label(info_frame, text=label_text, bg='lightgray')
            label.grid(row=i + 1, column=0, padx=10, pady=5, sticky='w')

            info_label = tk.Label(info_frame, text=info_text, bg='lightgray')
            info_label.grid(row=i + 1, column=1, padx=10, pady=5, sticky='w')



def show_chart():
    from matplotlib import rcParams
    rcParams["font.family"] = "Malgun Gothic"
    rcParams["axes.unicode_minus"] = False
    global map_label, info_frame  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        widget.destroy()  # 모든 위젯을 삭제

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
        date = list(spam.date(date_str))

        DateText = '' +date[0]+'년'+date[1]+'월'+date[2]+'일 전국 일일 평균 주유소 가격'

    # 화면 위쪽에 평균가 정보 표시
    top_frame = tk.Frame(right_frame, bg='white')
    top_frame.pack(side='top', fill='x', padx=10, pady=10)

    if date_str:
        current_price_label = tk.Label(top_frame, text=DateText, font=("Helvetica", 14), bg='white')
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

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5),gridspec_kw={'wspace': 0.3})


    # 7일간 전국 휘발유 평균 가격 그래프
    gasoline_history = gasstation.get_price_history_gasoline(api_key=GASSTATION_API_KEY)
    diesel_history = gasstation.get_price_history_disel(api_key=GASSTATION_API_KEY)
    #print(gasoline_history)
    #print(diesel_history)
    gasoline_prices = [entry['price'] for entry in gasoline_history]
    diesel_prices = [entry['price'] for entry in diesel_history]

    # 막대 그래프의 위치
    days = ['D+6', 'D+5', 'D+4', 'D+3', 'D+2', 'D+1','D-DAY']

    # 휘발유 평균 가격 그래프
    gasoline_prices = [float(entry['price']) for entry in gasoline_history]
    diesel_prices = [float(entry['price']) for entry in diesel_history]

    x_positions = range(len(days))  # 기본 x 위치
    adjusted_x_positions = [x -0.20 for x in x_positions]  # 각 x 위치를 오른쪽으로 약간 이동

    custom_ticks = [1500, 1600, 1700, 1750]  # 휘발유 가격 범위
    custom_labels = ['1500', '1600', '1700', '1750']

    custom_ticks1 = [1400, 1450, 1500, 1550, 1600]  # 경유 가격 범위
    custom_labels1 = ['1400', '1450', '1500', '1550', '1600']

    # Y축 설정
    ax1.set_yticks(custom_ticks)
    ax1.set_yticklabels(custom_labels)
    ax1.set_ylim(1500, 1750)

    ax2.set_yticks(custom_ticks1)
    ax2.set_yticklabels(custom_labels1)
    ax2.set_ylim(1400, 1600)

    # 휘발유 평균 가격 그래프
    ax1.bar(adjusted_x_positions, gasoline_prices, tick_label=days, label='휘발유 평균 가격')
    ax1.set_title('7일간 전국 휘발유 평균 가격')
    ax1.set_ylabel('가격 (원)')
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(days, rotation=0, ha='center')
    ax1.legend()

    # 경유 평균 가격 그래프
    ax2.bar(adjusted_x_positions, diesel_prices, tick_label=days, label='경유 평균 가격', color='orange')
    ax2.set_title('7일간 전국 경유 평균 가격')
    ax2.set_ylabel('가격 (원)')
    ax2.set_xticks(x_positions)
    ax2.set_xticklabels(days, rotation=0, ha='center')
    ax2.legend()


    fig.autofmt_xdate()

    canvas = FigureCanvasTkAgg(fig, master=top_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
def show_mail():
    global map_label, info_frame  # 전역 변수로 선언
    for widget in right_frame.winfo_children():
        widget.destroy()  # 모든 위젯을 삭제

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
    global map_label, info_frame  # 전역 변수로 선언

    if info_frame:
        info_frame.destroy()
    info_frame = tk.Frame(right_frame, bg='lightgray')
    info_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")  # 기존의 검색 결과 프레임 아래에 배치

    top_label = tk.Label(info_frame, text="주유소 정보", font=("Helvetica", 20), bg='lightgray')
    top_label.grid(row=0, column=0, columnspan=2, pady=10)


    if any(station["id"] == station_info["id"] for station in favorite_stations):
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
        ("휘발유 가격", station_info.get("휘발유_price", "N/A")),
        ("경유 가격", station_info.get("경유_price", "N/A")),
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