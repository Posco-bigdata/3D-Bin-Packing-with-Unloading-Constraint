import json
import numpy as np

def create_scenario(scenario_number):
    # 컨테이너 크기 설정
    container_size = [170, 275, 160]
    container_size = np.array(container_size) * 0.8
    container_size = container_size.tolist()  # JSON 직렬화를 위해 리스트로 변환
    print(f"컨테이너 크기: {container_size}")

    # 컨테이너 부피 계산
    container_volume = container_size[0] * container_size[1] * container_size[2]

    # JSON 파일에서 데이터 로드
    with open(f'./main_box_scenario_{scenario_number}.json', 'r') as file:
        data = json.load(file)

    # 총 아이템 부피 계산
    total_item_volume = sum(item['volume'] for item in data.values())

    # 부피 비율 계산
    volume_ratio = total_item_volume / container_volume

    # 시나리오 데이터 생성
    scenario = {
        "container_size": container_size,
        "items": data
    }

    # 시나리오를 JSON 파일로 저장
    filename = f'./box_data/scenario_{scenario_number}.json'
    with open(filename, 'w') as file:
        json.dump(scenario, file, indent=4)

    print(f"시나리오가 {filename}에 저장되었습니다.")
    print(f"컨테이너 부피: {container_volume:.2f}")
    print(f"선택된 아이템 수: {len(data)}")
    print(f"총 아이템 부피: {total_item_volume:.2f}")
    print(f"부피 비율 (아이템 부피 / 컨테이너 부피): {volume_ratio:.2%}")

    return container_size, data

if __name__ == "__main__":
    scenario_number = int(input("시나리오 번호를 입력하세요: "))
    create_scenario(scenario_number)