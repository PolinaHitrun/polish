import os
import re
import time
from bs4 import BeautifulSoup
import requests

base_url = "https://www.gutenberg.org"
search_url = "https://www.gutenberg.org/ebooks/search/?query=l.pl"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

output_dir = "raw_txt/gutenberg_polish_books"
os.makedirs(output_dir, exist_ok=True)


def sanitize_filename(name):
  """Удаляет символы, которые нельзя использовать в именах файлов."""
  return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def get_books_from_page(url):
  response = requests.get(url, headers=headers)
  if response.status_code != 200:
    print(f"Ошибка доступа к странице: {url}")
    return [], None

  soup = BeautifulSoup(response.text, "html.parser")
  books = []

  # Ищем карточки книг в результатах поиска
  for li in soup.find_all("li", class_="booklink"):
    a_tag = li.find("a", href=True)
    if a_tag and a_tag["href"].startswith("/ebooks/"):
      href = a_tag["href"]
      parts = href.strip("/").split("/")
      if len(parts) >= 2 and parts[1].isdigit():
        book_id = parts[1]

        # Извлекаем название книги из элемента)
        title_span = li.find("span", class_="title")
        if title_span:
          book_title = title_span.get_text(strip=True)
        else:
          book_title = a_tag.get_text(strip=True) or f"book_{book_id}"

        books.append({"id": book_id, "title": book_title})

  # Ищем ссылку на следующую страницу выдачи
  next_page_link = None
  next_a = soup.find("a", class_="next")
  if next_a and next_a.get("href"):
    next_page_link = base_url + next_a["href"]

  return books, next_page_link


def download_book(book):
  book_id = book["id"]
  book_title = book["title"]

  txt_url = f"https://www.gutenberg.org/ebooks/{book_id}.txt.utf-8"
  response = requests.get(txt_url, headers=headers)

  if response.status_code == 200:
    safe_title = sanitize_filename(book_title)
    # Обрезаем слишком длинные названия, чтобы не было ошибок ОС
    if len(safe_title) > 150:
      safe_title = safe_title[:150].strip()

    file_name = f"{safe_title}.txt"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
      f.write(response.text)
    print(f"Скачано: {file_name}")
  else:
    print(
        f"Не удалось скачать текст для книги ID {book_id} (статус"
        f" {response.status_code})"
    )


def main():
  current_url = search_url
  all_books = {}

  print("Сбор информации о книгах с сайта Project Gutenberg...")
  while current_url:
    print(f"Обрабатывается страница: {current_url}")
    books, current_url = get_books_from_page(current_url)

    for book in books:
      all_books[book["id"]] = book

    time.sleep(2)

  print(f"Всего найдено уникальных книг: {len(all_books)}")
  print("Начинаю скачивание текстовых файлов...")

  for book_id, book in all_books.items():
    download_book(book)
    time.sleep(1)


if __name__ == "__main__":
  main()