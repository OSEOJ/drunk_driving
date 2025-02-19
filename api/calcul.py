from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 서버에서 그래프를 생성하도록 설정
import matplotlib.pyplot as plt
import os

app = FastAPI()

# 각 주류별 정보: 이름, 용량, 도수, 단위당 알콜 그램
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

def get_user_input():
    print("=== 음주 측정기 ===")
    gender = input("성별 (male/female): ").strip().lower()
    while gender not in ['male', 'female']:
        gender = input("유효하지 않은 입력입니다. 성별 (male/female): ").strip().lower()
    
    weight = float(input("몸무게 (kg): ").strip())
    hours = float(input("음주 후 경과 시간 (시간): ").strip())
    
    consumption = {}
    print("\n각 주류별 섭취 횟수를 입력하세요 (숫자만 입력, 미입력 시 0으로 처리됩니다).")
    for key, info in alcohol_info.items():
        prompt = f"{info['name']} ({info['volume']}, {info['abv']}): "
        count_str = input(prompt).strip()
        count = int(count_str) if count_str.isdigit() else 0
        consumption[key] = count

    return gender, weight, hours, consumption

def calculate_bac(gender, weight, hours, consumption):
    total_alcohol = 0.0
    details_list = []
    for key, count in consumption.items():
        grams = count * alcohol_info[key]['grams']
        total_alcohol += grams
        details_list.append(
            f"{alcohol_info[key]['name']}: {count}회 ({alcohol_info[key]['volume']}, {alcohol_info[key]['abv']}) → {grams:.2f} g"
        )
    
    # 성별에 따른 알콜 분포율: 남성 0.68, 여성 0.55
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
    # 안전 기준에 도달할 때까지의 시간을 계산한 후 추가 1시간 더하여 그래프 시간 설정
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
    
    plt.show()
    
    image_path = "bac_plot.png"
    plt.savefig(image_path)
    plt.close()
    return image_path

    
    # filename = "bac_over_time.png"
    # plt.savefig(filename, bbox_inches="tight")
    # plt.close()
    # return filename

def display_results(total_alcohol, initial_bac, bac, penalty, details_list, hours):
    print("\n=== 입력 내역 ===")
    for item in details_list:
        print(" -", item)
    
    print("\n=== 측정 결과 ===")
    print(f"총 알콜 섭취량: {total_alcohol:.2f} g")
    print(f"마신 직후 BAC: {initial_bac:.3f}%")
    print(f"음주 후 {hours:.1f}시간 경과 시 BAC: {bac:.3f}%")
    print("\n처벌 기준 (예시):")
    print(" - BAC 0.03% 미만: 운전해도 괜찮습니다.")
    print(" - BAC 0.03% 이상 ~ 0.08% 미만: 징역 1년, 벌금 200만원, 면허 취소 6개월")
    print(" - BAC 0.08% 이상 ~ 0.15% 미만: 징역 2년, 벌금 500만원, 면허 취소 1년")
    print(" - BAC 0.15% 이상: 징역 3년, 벌금 1000만원, 면허 취소 2년")
    print(f"\n최종 결과: {penalty}")
    
    
    
@app.get("/graph")
def get_graph():
    image_path = "bac_plot.png"
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/png")
    return {"error": "그래프를 찾을 수 없습니다."}

def main():
    gender, weight, hours, consumption = get_user_input()
    total_alcohol, initial_bac, bac, penalty, details_list = calculate_bac(gender, weight, hours, consumption)
    display_results(total_alcohol, initial_bac, bac, penalty, details_list, hours)
    
    #plot_filename = generate_bac_plot(initial_bac)
    #plt.show()
    
    generate_bac_plot(initial_bac)

if __name__ == "__main__":
    main()