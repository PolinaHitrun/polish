import os
import re
import pymupdf


def extract_text_from_pdf(pdf_path):
  """Извлекает весь текст из PDF документа."""
  doc = pymupdf.open(pdf_path)
  text = ""
  for page in doc:
    text += page.get_text("text")
  return text


def split_and_save_chapters(text, output_dir, book_name, compiled_pattern):
  """Разбивает текст по скомпилированному паттерну и сохраняет только контент."""
  os.makedirs(output_dir, exist_ok=True)

  parts = re.split(compiled_pattern, text)

  intro = parts[0].strip()
  if len(intro) > 100:
    intro_path = os.path.join(output_dir, f"{book_name}_00_Wstep.txt")
    with open(intro_path, "w", encoding="utf-8") as f:
      f.write(intro)
    print(f"Сохранено: {intro_path}")

  chapter_num = 1
  for i in range(1, len(parts), 2):
    chapter_title = parts[i].strip()

    safe_title = re.sub(r'[\\/*?:"<>|]', "", chapter_title)
    safe_title = re.sub(r"\s+", "_", safe_title)

    # Сохраняем исключительно текст главы, заголовок остается только в названии файла
    chapter_content = parts[i + 1].strip() if i + 1 < len(parts) else ""

    filename = f"{book_name}_{chapter_num:02d}_{safe_title}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
      f.write(chapter_content)

    print(f"Сохранено: {filepath}")
    chapter_num += 1


def main():
  input_dir = "parsing_scripts/pdf_sapkowski"
  output_dir = "raw_txt/parsed_sp"

  pattern_jeziora = re.compile(
      r"^(Rozdział\s+[a-ząćęłńóśźż]+)$", flags=re.MULTILINE | re.IGNORECASE
  )

  pattern_wiedzmin = re.compile(
      r"^([A-ZĄĆĘŁŃÓŚŹŻ][A-ZĄĆĘŁŃÓŚŹŻ\s\d]{3,})$", flags=re.MULTILINE
  )

  for filename in os.listdir(input_dir):
    if not filename.lower().endswith(".pdf"):
      continue

    if filename == "pani-jeziora_RuLit_Net_99480.pdf":
      print(f"\nНачат парсинг книги: {filename}")
      pdf_path = os.path.join(input_dir, filename)
      text = extract_text_from_pdf(pdf_path)
      split_and_save_chapters(
          text, output_dir, "Pani_Jeziora", pattern_jeziora
      )

    elif "wiedzmin" in filename.lower():
      print(f"\nНачат парсинг книги: {filename}")
      pdf_path = os.path.join(input_dir, filename)
      book_name = os.path.splitext(filename)[0]
      text = extract_text_from_pdf(pdf_path)
      split_and_save_chapters(text, output_dir, book_name, pattern_wiedzmin)


if __name__ == "__main__":
  main()