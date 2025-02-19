from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 서버에서 그래프 생성
import matplotlib.pyplot as plt
import pandas as pd
import io
from starlette.responses import StreamingResponse

# --- calcul.py에 있는 코드 시작 ---
# 각 주류별 정보
alcohol_info = {
    'soju': {
        'name': "소주",
        'volume': "360 mL",
        'abv': "20%",
        'grams': 56.8
    },
    'beer': {
        'name': "맥주",
        'volume': "500 mL",
        'abv': "4.5%",
        'grams': 17.75
    },
    'wine': {
        'name': "와인",
        'volume': "150 mL",
        'abv': "12%",
        'grams': 14.2
    },
    'makgeolli': {
        'name': "막걸리",
        'volume': "300 mL",
        'abv': "6%",
        'grams': 14.2
    },
    'whiskey': {
        'name': "양주",
        'volume': "30 mL",
        'abv': "40%",
        'grams': 9.5
    }
}

def calculate_bac(gender, weight, hours, consumption):
    total_alcohol = 0.0
    details_list = []
    for key, count in consumption.items():
        grams = count * alcohol_info[key]['grams']
        total_alcohol += grams
        details_list.append(
            f"{alcohol_info[key]['name']}: {count}회 ({alcohol_info[key]['volume']}, {alcohol_info[key]['abv']}) → {grams:.2f} g"
        )
    r = 0.68 if gender == 'male' else 0.55
    initial_bac = (total_alcohol / (weight * 1000 * r)) * 100  # 마신 직후 BAC (%)
    bac = max(initial_bac - 0.015 * hours, 0)  # 경과 시간 후 BAC (%)
    
    if bac < 0.03:
        penalty = "운전해도 괜찮습니다."
    elif bac < 0.08:
        penalty = "징역 1년, 벌금 200만원, 면허 취소 6개월"
    elif bac < 0.15:
        penalty = "징역 2년, 벌금 500만원, 면허 취소 1년"
    else:
        penalty = "징역 3년, 벌금 1000만원, 면허 취소 2년"
    
    return total_alcohol, initial_bac, bac, penalty, details_list

def generate_bac_plot(initial_bac, safe_threshold=0.03):
    time_to_safe = (initial_bac - safe_threshold) / 0.015 if initial_bac > safe_threshold else 0
    T_end = time_to_safe + 1 if time_to_safe > 0 else 1
    times = np.linspace(0, T_end, 100)
    bac_values = [max(initial_bac - 0.015 * t, 0) for t in times]
    
    plt.figure(figsize=(6, 4))
    plt.plot(times, bac_values, label="BAC")
    plt.axhline(y=safe_threshold, color='green', linestyle='--', label="Safe Limit (0.03%)")
    plt.xlabel("Time (hours)")
    plt.ylabel("Blood Alcohol Concentration (%)")
    plt.title("BAC over Time")
    plt.legend()
    plt.grid(True)
    
    image_path = "bac_plot.png"
    plt.savefig(image_path)
    plt.close()
    return image_path
# --- calcul.py에 있는 코드 끝 ---

app = FastAPI()
# main.py가 있는 디렉토리의 상위 디렉토리를 BASE_DIR로 설정합니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# public/static 폴더의 절대 경로를 지정합니다.
static_dir = os.path.join(BASE_DIR, "public", "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# main.py가 있는 api 폴더의 상위 디렉토리(프로젝트 루트)를 BASE_DIR로 설정합니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(BASE_DIR, "public")

templates = Jinja2Templates(directory=template_dir)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 기존 섹션3 관련 엔드포인트들 (생략)

# ---------------- 새로 추가된 부분 ----------------
@app.post("/custom_calculate")
async def custom_calculate(
    gender: str = Form(...),
    bodyWeight: float = Form(...),
    hours: float = Form(...),
    soju: int = Form(0),
    beer: int = Form(0),
    wine: int = Form(0),
    makgeolli: int = Form(0),
    whiskey: int = Form(0)
):
    try:
        consumption = {
            'soju': soju,
            'beer': beer,
            'wine': wine,
            'makgeolli': makgeolli,
            'whiskey': whiskey
        }
        total_alcohol, initial_bac, bac, penalty, details = calculate_bac(gender, bodyWeight, hours, consumption)
        graph_path = generate_bac_plot(initial_bac)
        result = {
            "total_alcohol": total_alcohol,
            "initial_bac": initial_bac,
            "bac": bac,
            "penalty": penalty,
            "details": details,
            "graph_url": "/graph"
        }
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/graph")
async def get_graph():
    image_path = "bac_plot.png"
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/png")
    return JSONResponse({"error": "그래프를 찾을 수 없습니다."})
# ---------------- 새로 추가된 부분 끝 ----------------

# Section 3: 음주운전 부상자 및 사망자 로즈차트


# main.py 파일이 위치한 api 폴더의 상위 디렉토리(my-fastapi-app)를 BASE_DIR로 설정합니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# data 폴더는 api 폴더와 같은 레벨에 있으므로, BASE_DIR 아래에 data 폴더가 있습니다.
data_file = os.path.join(BASE_DIR, "data", "DUI_death_injure.xls")

print("Data file path:", data_file)  # 경로 확인용

plt.rc("font", family="AppleGothic")  
df = pd.read_excel(data_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.get("/dui_chart")
async def dui_chart(request: Request):
    years = df['연도']
    deaths = df['음주 사망자수']
    injuries = df['음주 부상자수']
    casualty = deaths + injuries  

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(years, casualty, color='grey', label='사상자수', alpha=1)

    ax.axvline(x=2014, color='black', linestyle='--', linewidth=3, label="14' 가중처벌 도입")
    ax.axvline(x=2019, color='black', linestyle='-.', linewidth=3, label="19' 윤창호법 시행")

    ax.set_xlabel('연도')
    ax.set_ylabel('사상자 수')
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    return StreamingResponse(io.BytesIO(img.getvalue()), media_type="image/png")
