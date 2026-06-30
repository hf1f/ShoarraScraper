import json

input_filename = "all_poems_database.json"
output_filename = "poets_database.json"

try:
    # Load the main crawled database
    with open(input_filename, "r", encoding="utf-8") as f:
        all_poems = json.load(f)
    
    poets_dict = {}

    # Extract poets and avoid duplicates using a dictionary
    for poem in all_poems:
        poet_id = poem.get("poet_id")
        poet_name = poem.get("poet_name")
        
        # Validate data before extracting
        if poet_id and poet_name and poet_id != "غير محدد" and poet_name != "غير معروف":
            if poet_id not in poets_dict:
                poets_dict[poet_id] = {
                    "poet_id": poet_id,
                    "poet_name": poet_name,
                    "country": poem.get("country", "غير محدد"),
                    "era": poem.get("era", "غير محدد")
                }

    # Convert dictionary to list and save to a new file
    poets_list = list(poets_dict.values())
    
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(poets_list, json_file, ensure_ascii=False, indent=4)
        
    print(f"Done! Extracted {len(poets_list)} unique poets into '{output_filename}'.")

except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")