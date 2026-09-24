import os
import re
import time
from bs4 import BeautifulSoup
import requests

base_url = "https://wolnelektury.pl"
catalog_url = "https://wolnelektury.pl/katalog/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

output_dir = "raw_txt/wolne_lektury_books"
os.makedirs(output_dir, exist_ok=True)


def sanitize_filename(name):
  return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def main():
  print("Подключаемся к каталогу Wolne Lektury...")
  try:
    response = requests.get(catalog_url, headers=headers, timeout=15)
  except requests.exceptions.RequestException as e:
    print(f"Ошибка подключения к каталогу: {e}")
    return

  if response.status_code != 200:
    print(f"Ошибка доступа к каталогу: {response.status_code}")
    return

  soup = BeautifulSoup(response.text, "html.parser")

  book_links = []
  for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith("/katalog/lektura/") and href != "/katalog/lektura/":
      full_url = base_url + href
      if full_url not in book_links:
        book_links.append(full_url)

  print(f"Найдено страниц произведений: {len(book_links)}")

  for i, book_page_url in enumerate(book_links):
    try:
      book_resp = requests.get(book_page_url, headers=headers, timeout=15)
      if book_resp.status_code != 200:
        continue

      book_soup = BeautifulSoup(book_resp.text, "html.parser")

      title_tag = book_soup.find("h1")
      title = title_tag.get_text(strip=True) if title_tag else f"book_{i}"

      safe_title = sanitize_filename(title)
      if len(safe_title) > 150:
        safe_title = safe_title[:150].strip()

      file_path = os.path.join(output_dir, f"{safe_title}.txt")

      # Если файл уже есть на диске, пропускаем скачивание
      if os.path.exists(file_path):
        print(f"Уже скачано, пропуск: {safe_title}.txt")
        continue

      txt_link = None
      for a in book_soup.find_all("a", href=True):
        if ".txt" in a["href"]:
          txt_link = a["href"]
          break

      if not txt_link:
        print(f"У книги '{title}' нет прямой текстовой версии. Пропуск.")
        continue

      if txt_link.startswith("/"):
        txt_link = base_url + txt_link

      txt_resp = requests.get(txt_link, headers=headers, timeout=15)
      if txt_resp.status_code == 200:
        txt_resp.encoding = "utf-8"
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(txt_resp.text)
        print(f"Скачано: {safe_title}.txt")
      else:
        print(f"Ошибка скачивания текста для '{title}'")

      time.sleep(0.5)
    except requests.exceptions.Timeout:
      print(f"Таймаут при обработке {book_page_url}, пропускаем...")
    except Exception as e:
      print(f"Ошибка при обработке {book_page_url}: {e}")


if __name__ == "__main__":
  main()