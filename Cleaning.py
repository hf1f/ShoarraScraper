import json
import os

input_filename = "all_poems_database.json"
cleaned_poems_filename = "all_poems_database_cleaned.json"
poets_output_filename = "poets_database.json"

try:
    # 1. Load raw database
    if not os.path.exists(input_filename):
        raise FileNotFoundError(f"File '{input_filename}' not found.")
        
    with open(input_filename, "r", encoding="utf-8") as f:
        all_poems = json.load(f)
    
    print(f"[*] Total poems loaded: {len(all_poems)}")

    # 2. Remove duplicate poems based on poem_id
    poems_dict = {}
    for poem in all_poems:
        p_id = str(poem.get("poem_id", "")).strip()
        if p_id and p_id not in poems_dict:
            poems_dict[p_id] = poem

    cleaned_poems_list = list(poems_dict.values())
    print(f"[-] Removed {len(all_poems) - len(cleaned_poems_list)} duplicate poems.")

    # Save cleaned poems
    with open(cleaned_poems_filename, "w", encoding="utf-8") as json_file:
        json.dump(cleaned_poems_list, json_file, ensure_ascii=False, indent=4)

    print("-" * 40)

    # 3. Extract strictly unique poets (No Duplicates Guaranteed)
    poets_dict = {}
    for poem in cleaned_poems_list:
        poet_id = str(poem.get("poet_id", "")).strip()
        poet_name = str(poem.get("poet_name", "")).strip()
        
        # Validate data integrity
        if poet_id and poet_name and poet_id not in ["Not specified", ""] and poet_name not in ["Unknown", ""]:
            # Dictionary key constraints prevent any duplicate poet_id from entering
            if poet_id not in poets_dict:
                poets_dict[poet_id] = {
                    "poet_id": poet_id,
                    "poet_name": poet_name,
                    "country": poem.get("country", "غير محدد"),
                    "era": poem.get("era", "غير محدد")
                }

    poets_list = list(poets_dict.values())
    
    # Save unique poets
    with open(poets_output_filename, "w", encoding="utf-8") as json_file:
        json.dump(poets_list, json_file, ensure_ascii=False, indent=4)
        
    print(f"[✔] Successfully extracted {len(poets_list)} unique poets to '{poets_output_filename}'.")

except FileNotFoundError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")