import os
import re
import spacy
from langdetect import detect, LangDetectException
from tqdm import tqdm


def split_into_sentences(text, nlp):
    "Разделение текста на предложения с использованием spaCy"
    nlp.max_length = max(nlp.max_length, len(text) + 100000)
    doc = nlp(text)
    return list(doc.sents)


def is_polish(text):
    "Проверка, является ли текст польским"
    try:
        return detect(text) == 'pl'
    except LangDetectException:
        return False


def is_punctuation_or_space(token):
    "Проверка, является ли токен знаком препинания или пробелом"
    return token.is_punct or token.is_space


def is_all_caps(token):
    "Проверка, является ли токен словом, написанным капсом"
    if token.is_alpha and token.is_upper and len(token.text) > 1:
        return True
    return False


def process_propn(token):
    "Заменяем имена собственные на специальный токен"
    return "PROPN" if token.pos_ == "PROPN" else None


def process_roman_numeral(token):
    "Выкидываем римские цифры, так как в основном ими записан номер главы"
    pattern = r'^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
    if token.is_alpha and token.is_upper and re.match(pattern, token.text):
        return ""
    return None


def process_num(token):
    "Заменяем числительные на специальный токен"
    return "NUM" if token.pos_ == "NUM" or token.like_num else None


def process_pronoun(token):
    "Заменяем местоимения на специальный токен"
    if token.pos_ == "PRON":
        person = token.morph.get("Person")
        if person:
            return person[0]
    return None


def get_lemma(token):
    return token.lemma_


def process_token(token):
    "Общая функция для обработки токена"
    if is_punctuation_or_space(token) or is_all_caps(token):
        return None

    replacement = (
        process_propn(token) or 
        process_roman_numeral(token) or 
        process_num(token) or 
        process_pronoun(token)
    )
    
    if replacement:
        return replacement

    return get_lemma(token).lower()

def main(input_dir, output_dir):
    try:
        nlp = spacy.load("pl_core_news_sm")
    except OSError:
        print("Ошибка: Скачайте модель через 'python -m spacy download pl_core_news_sm'")
        return

    os.makedirs(output_dir, exist_ok=True)

    filepaths = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".txt"):
                filepaths.append(os.path.join(root, file))

    for filepath in tqdm(filepaths, desc="Предобработка текстов"):
        filename = os.path.basename(filepath)
        out_path = os.path.join(output_dir, filename)
        
        # Пропуск файла, если он уже существует в выходной директории
        if os.path.exists(out_path):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        if not text.strip():
            continue

        sentences = split_into_sentences(text, nlp)
        processed_sentences = []

        for sent in sentences:
            sent_text = sent.text.strip()
            if not sent_text or not is_polish(sent_text):
                continue

            processed_tokens = []
            
            for token in sent:
                processed_word = process_token(token)
                if processed_word:
                    processed_tokens.append(processed_word)

            if processed_tokens:
                processed_sentences.append(" ".join(processed_tokens))

        if processed_sentences:
            total_words = sum(len(sent.split()) for sent in processed_sentences)
            
            if total_words > 100:
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(processed_sentences))
            else:
                print(f"Файл пропущен (слишком мало слов - {total_words}): {filepath}")

if __name__ == "__main__":
    input_directory = "txt"
    output_directory = "preprocessed"
    main(input_directory, output_directory)