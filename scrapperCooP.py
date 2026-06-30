import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# ==========================================
# Config & Global Scope
# ==========================================
start_poem_id = 4500
end_poem_id = 16040
output_filename = "all_poems_database.json"

MAX_WORKERS = 6  

all_data = []
data_lock = Lock()  # Prevents race conditions during multi-threading
counter = 0

# Load existing data if backup file exists
if os.path.exists(output_filename):
    try:
        with open(output_filename, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        print(f"[*] Found existing backup with {len(all_data)} poems. Continuing...")
    except:
        all_data = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_word(text):
    """Removes Arabic elongation (Kashida) and normalizes spaces."""
    if not text:
        return ""
    cleaned = re.sub(r'ـ+', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def restructure_poem_properly(poem_div):
    """Extracts, cleans, and formats poem verses properly."""
    if not poem_div:
        return ""
    structured_lines = []
    raw_lines = poem_div.get_text(separator="\n").splitlines()
    
    for line in raw_lines:
        line_str = line.strip()
        if not line_str or re.search(r'(?i)\btesting\b', line_str):
            continue
            
        # Splits double-hemistich verses if separated by '='
        if '=' in line_str:
            parts = line_str.split('=')
            shatr_1 = clean_word(parts[0])
            shatr_2 = clean_word(parts[1]) if len(parts) > 1 else ""
            if shatr_1 or shatr_2:
                structured_lines.append(f"{shatr_1}        {shatr_2}")
        else:
            cleaned_line = clean_word(line_str)
            if cleaned_line:
                structured_lines.append(cleaned_line)
                
    return "\n".join(structured_lines)

def scrape_single_poem(poem_id):
    """Scrapes metadata and text for a single poem ID."""
    global counter
    poem_url = f"https://shoaraa.com/p{poem_id}"
    
    print(f"[-] Thread checking page: p{poem_id}")
    
    try:
        # Avoid aggressive scraping with a small random delay
        time.sleep(random.uniform(0.1, 0.4))
        res = requests.get(poem_url, headers=headers, timeout=10)
        
        if res.status_code != 200:
            return
            
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'lxml')
        
        # Extract poem text
        poem_div = soup.find('div', class_='poemtext')
        if not poem_div:
            return
            
        full_poem_clean = restructure_poem_properly(poem_div)
        if not full_poem_clean:
            return
            
        # Extract Title and Poet Name
        f_tags = soup.find_all('f', class_='lotusbold')
        if len(f_tags) >= 2:
            poem_title = clean_word(f_tags[0].text)
            poet_name = clean_word(f_tags[1].text)
        else:
            poem_title = "Unknown"
            poet_name = "Unknown"
            
        source_info = "Not specified"
        hijri_date = "Not specified"
        
        # Extract date and source context from side/alert boxes
        alert_divs = soup.find_all('div', class_=lambda x: x and 'mainbg2' in x)
        for adv in alert_divs:
            adv_text = adv.text.strip()
            if any(k in adv_text for k in ["محرم", "هـ", "رمضان", "الحرام", "صفر", "ربيع"]):
                hijri_date = clean_word(adv_text)
            elif adv_text and source_info == "Not specified":
                source_info = clean_word(adv_text)

        era = "Not specified"
        country = "Not specified"
        era_id = "Not specified"
        
        # Extract historical era and country from breadcrumbs
        bread_div = soup.find('div', class_='breadmenu')
        if bread_div:
            bread_links = bread_div.find_all('a')
            for b_link in bread_links:
                b_text = b_link.text.strip()
                b_href = b_link.get('href', '')
                if "قرن" in b_text or "عصر" in b_text:
                    era = b_text
                    s_match = re.search(r's(\d+)', b_href)
                    if s_match:
                        era_id = s_match.group(1)
                elif "شعراء" in b_text:
                    country = b_text.replace("شعراء ", "")

        poet_id = "Not specified"
        theme = "Not specified"
        poem_sub_theme = "General"
        
        # Extract IDs and categories from internal links
        all_links = soup.find_all('a')
        for link in all_links:
            link_text = link.text.strip()
            href = link.get('href', '')
            if 's' in href:
                s_match = re.search(r's(\d+)', href)
                current_s_id = s_match.group(1) if s_match else ""
                if link_text == poet_name:
                    poet_id = current_s_id
                elif link_text in ["أحزان", "أفراح", "أناشيد ووجدانيات", "أناشيد"]:
                    poem_sub_theme = link_text
                elif "قصائد" in link_text:
                    theme = link_text

        poetry_type = "Not specified"
        added_date = "Not specified"
        added_time = "Not specified"
        num_verses = "Not specified"
        
        # Extract specific tech specs from the info panel
        collapse_div = soup.find('div', id='collapseExample')
        if collapse_div:
            sub_divs = collapse_div.find_all('div', class_=lambda x: x and 'col-sm' in x)
            for i, sdiv in enumerate(sub_divs):
                sdiv_text = sdiv.text.strip()
                if "نوع القصيدة" in sdiv_text and i + 1 < len(sub_divs):
                    poetry_type = clean_word(sub_divs[i+1].text)
                elif "تاريخ الإضافة" in sdiv_text and i + 1 < len(sub_divs):
                    added_date = clean_word(sub_divs[i+1].text)
                elif "وقـت الإضـافـة" in sdiv_text or "وقت الإضافة" in sdiv_text and i + 1 < len(sub_divs):
                    added_time = clean_word(sub_divs[i+1].text)
                elif "عــــدد الأبـيـات" in sdiv_text or "عدد الأبيات" in sdiv_text and i + 1 < len(sub_divs):
                    num_verses = clean_word(sub_divs[i+1].text)

        # Structure the final payload object
        poem_object = {
            'poem_id': poem_id,
            'poet_id': poet_id,
            'era_id': era_id,
            'title': poem_title,
            'poet_name': poet_name,
            'full_poem_text': full_poem_clean,
            'poetry_type': poetry_type,
            'poem_sub_theme': poem_sub_theme,
            'number_of_verses': num_verses,
            'era': era,
            'country': country,
            'theme': theme,
            'source_context': source_info,
            'hijri_date': hijri_date,
            'added_date_gregorian': added_date,
            'added_time': added_time,
            'source_url': poem_url
        }

        # Safe lock execution to append data and handle auto-saving
        with data_lock:
            all_data.append(poem_object)
            counter += 1
            print(f"   [SUCCESS] Caught Poem #{counter}: {poem_title} (p{poem_id})")
            
            # Save progress incrementally every 20 successful items
            if counter % 20 == 0:
                with open(output_filename, "w", encoding="utf-8") as json_file:
                    json.dump(all_data, json_file, ensure_ascii=False, indent=4)
                print(f"======> AUTO-SAVE TRIGGERED! {len(all_data)} poems secured on disk! <======")

    except Exception:
        return

if __name__ == "__main__":
    print(f"Launching Multi-Threaded Scraper with {MAX_WORKERS} threads...")
    poem_ids_to_scrape = range(start_poem_id, end_poem_id + 1)

    # Initialize thread pool execution
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(scrape_single_poem, poem_ids_to_scrape)

    # Final persistent save to disk after pool closes
    print("\nExecuting final database save...")
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)
    print(f" MISSION ACCOMPLISHED! All active threads completed successfully.")