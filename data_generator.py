from main_scenario_box import generate_box_scenario
from barcode_reader import process_barcodes
from generate_barcodes import generate_barcodes
import json

def main():
    # Step 1: Generate box scenario
    scenario_number = input("시나리오 번호를 입력하세요: ")
    scenario_file = generate_box_scenario(scenario_number)

    # Step 2: Load the generated scenario
    with open(scenario_file, 'r') as f:
        scenario_data = json.load(f)

    # Step 3: Generate barcodes
    generate_barcodes(scenario_number, scenario_data)

    # Step 4: Wait for user to start barcode reading
    while True:
        user_input = input("바코드 생성이 완료되었습니다. 바코드 읽기를 시작하려면 'start'를 입력하세요: ")
        if user_input.lower() == 'start':
            break
    # Step 5: Process barcodes
    updated_data = process_barcodes(scenario_data)

    # Step 6: Save updated data back to the scenario file
    with open(scenario_file, 'w') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=4)

    print(f"업데이트된 데이터가 {scenario_file}에 저장되었습니다.")

if __name__ == "__main__":
    main()