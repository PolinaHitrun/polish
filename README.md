# Polish Text Corpora and Embeddings Pipeline

Репозиторий содержит пайплайн сбора, предобработки польского корпуса текстов, а также построения векторных представлений слов (SVD и CBoW).

## Данные и модели (Ссылки на скачивание)

Из-за ограничений GitHub на размер файлов датасеты и веса моделей размещены по ссылкам ниже:

**[Ссылка](https://disk.360.yandex.ru/d/VHx3KmYLgPQrJA) на всю папку**

* [Необработанный корпус](https://disk.360.yandex.ru/client/disk/%D0%9F%D0%BE%D0%BB%D1%8C%D1%81%D0%BA%D0%B8%D0%B9%20%D1%8F%D0%B7%D1%8B%D0%BA/raw_txt)
Тексты художественной литературы с исходными названиями файлов до очистки и лемматизации.
* Обработанные корпуса. Очищенные и лемматизированные
  * [Пофайловый](https://disk.360.yandex.ru/client/disk/%D0%9F%D0%BE%D0%BB%D1%8C%D1%81%D0%BA%D0%B8%D0%B9%20%D1%8F%D0%B7%D1%8B%D0%BA/preprocessed)
  * [Объединённый](https://docviewer.360.yandex.ru/view/1130000064843132/?*=K4IPjyysbK5qisu3Cbmpp3L5p8J7InVybCI6InlhLWRpc2s6Ly8vZGlzay%2FQn9C%2B0LvRjNGB0LrQuNC5INGP0LfRi9C6L3BvbGlzaF9jb3JwdXMudHh0IiwidGl0bGUiOiJwb2xpc2hfY29ycHVzLnR4dCIsIm5vaWZyYW1lIjpmYWxzZSwidWlkIjoiMTEzMDAwMDA2NDg0MzEzMiIsInRzIjoxNzkwMjUyNjU4NDU1LCJ5dSI6Ijk1NzE5MzM1NzE2ODg2MTk2NjAifQ%3D%3D)
* Эмбеддинги
  * [Для SVD](https://disk.360.yandex.ru/client/disk/%D0%9F%D0%BE%D0%BB%D1%8C%D1%81%D0%BA%D0%B8%D0%B9%20%D1%8F%D0%B7%D1%8B%D0%BA/svd_data) в формате NumPy (`.npy`)
  * [Для CBOW](https://docviewer.360.yandex.ru/view/1130000064843132/?*=3dojSXL9p1dL%2Fiee2vVYI1oDA997InVybCI6InlhLWRpc2s6Ly8vZGlzay%2FQn9C%2B0LvRjNGB0LrQuNC5INGP0LfRi9C6L3BvbGlzaF9jYm93X2RpY3Rpb25hcnkudHh0IiwidGl0bGUiOiJwb2xpc2hfY2Jvd19kaWN0aW9uYXJ5LnR4dCIsIm5vaWZyYW1lIjpmYWxzZSwidWlkIjoiMTEzMDAwMDA2NDg0MzEzMiIsInRzIjoxNzkwMjUyNjM4NDY0LCJ5dSI6Ijk1NzE5MzM1NzE2ODg2MTk2NjAifQ%3D%3D) в текстовом словаре (`.txt`)

## Пайплайн обработки

### Предобработка и лемматизация:

`preprocess.py` — алгоритм очистки от пунктуации, лемматизации и другой предобработки.

`making_corpus.py` — генерация единого корпуса для моделей.

### Обучение моделей:

`get_tfidf.py` — построение матриц совместной встречаемости TF-IDF и SVD-разложение.

`get_word2vec.py` — обучение CBoW эмбеддингов.