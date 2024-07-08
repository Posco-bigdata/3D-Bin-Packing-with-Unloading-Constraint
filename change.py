import json

# Open the JSON file and load its content into a Python object
with open("./scenario/rearranged_items_scenario_777_original.json", "r") as json_file:
    json_data = json.load(json_file)

# Assuming json_data is a list of dictionaries and you want to sort it by 'item_id'
json_data.sort(key=lambda x: x['id'])

# Assuming the rest of the processing happens here
# After updating the json_data dictionary as needed

# Save the updated data back to the same JSON file
with open("rearranged_items_scenario_777_original.json", 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

# Optionally, print a message indicating the file has been updated
print(f"Data saved to rearranged_items_scenario_777_original.json")