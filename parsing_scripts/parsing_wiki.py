import os
import time
import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm

API_URL = "https://pl.wikisource.org/w/api.php"
HEADERS = {
    "User-Agent": "PolishLitCrawler/1.2"
}

def generate_category_members(category_name, max_depth=3, current_depth=0, visited=None):
    if visited is None:
        visited = set()
        
    if not category_name.startswith("Kategoria:"):
        category_name = f"Kategoria:{category_name}"
        
    if category_name in visited:
        return
        
    visited.add(category_name)

    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category_name,
        "cmlimit": "500",
        "maxlag": "5",
        "format": "json"
    }

    while True:
        success = False
        data = {}
        wait_time = 5 
        
        for attempt in range(5):
            try:
                response = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                if "error" in data and data["error"].get("code") == "maxlag":
                    time.sleep(wait_time)
                    wait_time *= 2
                    continue
                
                success = True
                break
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    time.sleep(wait_time)
                    wait_time *= 2
                else:
                    break
            except requests.exceptions.RequestException:
                time.sleep(wait_time)
                wait_time *= 2

        if not success:
            break
            
        if "query" in data and "categorymembers" in data["query"]:
            for member in data["query"]["categorymembers"]:
                if member["ns"] == 0:  
                    yield member["title"]
                elif member["ns"] == 14 and current_depth < max_depth:  
                    yield from generate_category_members(member["title"], max_depth, current_depth + 1, visited)

        if "continue" in data:
            params.update(data["continue"])
        else:
            break

def get_page_text(title):
    params = {
        "action": "parse",
        "prop": "text",
        "page": title,
        "maxlag": "5",
        "format": "json"
    }
    
    wait_time = 5
    for attempt in range(5):
        try:
            response = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                if data["error"].get("code") == "maxlag":
                    time.sleep(wait_time)
                    wait_time *= 2
                    continue
                else:
                    return None
            
            html_content = data.get("parse", {}).get("text", {}).get("*", "")
            if not html_content:
                return None
                
            soup = BeautifulSoup(html_content, "html.parser")
            
            for hidden in soup.find_all(class_=["ws-noexport", "noprint", "mw-editsection", "pagenum"]):
                hidden.decompose()
                
            text = soup.get_text(separator="\n", strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text
                
        except (requests.exceptions.RequestException, ValueError):
            time.sleep(wait_time)
            wait_time *= 2
            
    return None

def main():
    categories = [
        "Kategoria:Józef_Ignacy_Kraszewski",
        "Kategoria:Henryk_Sienkiewicz",
        "Kategoria:Bolesław_Prus",
        "Kategoria:Eliza_Orzeszkowa",
        "Kategoria:Władysław_Reymont",
        "Kategoria:Stefan_Żeromski",
        "Kategoria:Maria_Rodziewiczówna"
    ]
    
    output_dir = "raw_txt/wikisource_books"
    os.makedirs(output_dir, exist_ok=True)
    
    saved_books = 0
    # Укажите здесь, сколько файлов надо скачать
    target_amount = 300 
    processed_titles = set() 
    
    pbar = tqdm(total=target_amount, desc="Скачивание текстов")

    for cat in categories:
        if saved_books >= target_amount:
            break
            
        for title in generate_category_members(cat, max_depth=3):
            if saved_books >= target_amount:
                break
                
            if title in processed_titles:
                continue
            processed_titles.add(title)
            
            # Генерируем имя файла
            safe_title = re.sub(r'[\\/*?:"<>|]', " ", title)
            safe_title = re.sub(r'\s+', '_', safe_title).strip()[:100] 
            filepath = os.path.join(output_dir, f"{safe_title}.txt")
            
            # Если файл уже скачан ранее — пропускаем
            if os.path.exists(filepath):
                continue
                
            # Скачиваем текст
            text = get_page_text(title)
            
            if text and len(text.split()) > 100:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text)
                saved_books += 1
                pbar.update(1)
                    
                time.sleep(0.5)

    pbar.close()
    print(f"\nСкачано {saved_books} текстов")

if __name__ == "__main__":
    main()