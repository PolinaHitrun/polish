import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds

def make_matrix_W_list_of_words(corpus_path, min_df, max_df=None, token_pattern=None, use_idf=True):
    with open(corpus_path, 'r', encoding='utf-8') as corpus_file:
        if token_pattern:
            vectorizer = TfidfVectorizer(analyzer='word', min_df=min_df, token_pattern=token_pattern, use_idf=use_idf)
        else:
            vectorizer = TfidfVectorizer(analyzer='word', min_df=min_df, use_idf=use_idf)
            
        data_vectorized = vectorizer.fit_transform(corpus_file)
    return data_vectorized, vectorizer.get_feature_names_out()

def apply_svd(W, k, output_folder):
    # Применение функции SVD, где k должно быть меньше любой размерности W
    u, sigma, vt = svds(W, k)

    # Сортировка сингулярных значений по убыванию
    descending_order_of_inds = np.flip(np.argsort(sigma))
    u = u[:, descending_order_of_inds]
    vt = vt[descending_order_of_inds]
    sigma = sigma[descending_order_of_inds]

    # Сохранение матриц на диск
    with open(os.path.join(output_folder, f'{k}_sigma_vt.npy'), 'wb') as f:
        np.save(f, np.dot(np.diag(sigma), vt).T)
    with open(os.path.join(output_folder, f'{k}_sigma.npy'), 'wb') as f:
        np.save(f, sigma)
    with open(os.path.join(output_folder, f'{k}_u.npy'), 'wb') as f:
        np.save(f, u)
    with open(os.path.join(output_folder, f'{k}_vt.npy'), 'wb') as f:
        np.save(f, vt)
        
    return np.dot(np.diag(sigma), vt).T

def create_dictionary(words_list, vv, output_file):
    dictionary = {}
    for word, vector in zip(words_list, vv):
        dictionary[word] = vector
        
    np.save(output_file, dictionary)
    return dictionary

if __name__ == "__main__":
    corpus_file = 'polish_corpus.txt'
    output_dir = 'dictionary_data'
    dict_file = os.path.join(output_dir, 'polish_dictionary.npy')
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Создание матрицы TF-IDF...")
    W_russian, words_list_russian = make_matrix_W_list_of_words(corpus_file, min_df=1)
    k = min(100, min(W_russian.shape) - 1) 
    
    print(f"Применение SVD размерности {k}...")
    vv_russian = apply_svd(W_russian, k, output_dir)
    
    print("Формирование и сохранение словаря...")
    create_dictionary(words_list_russian, vv_russian, dict_file)
    print("Готово")