import io
from gensim.models import Word2Vec


def load_corpus(fname):
    """Читает корпус построчно (новая строка = новый документ)"""
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    documents = []
    for line in fin:
        documents.append(line.split())
    return documents

def save_dictionary(fname, dictionary, args):
    """Сохраняет словарь: первая строка 'длина размерность', далее 'слово вектор'."""
    length, dimension = args
    fin = io.open(fname, 'w', encoding='utf-8')
    fin.write('%d %d\n' % (length, dimension))
    for word in dictionary:
        fin.write('%s %s\n' % (word, ' '.join(map(str, dictionary[word]))))

def load_dictionary(fname):
    """Загружает словарь из текстового файла."""
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    length, dimension = map(int, fin.readline().split())
    dictionary = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        dictionary[tokens[0]] = map(float, tokens[1:])
    return dictionary

def get_vocab(fname):
    """Собирает множество уникальных слов без загрузки всего текста в память."""
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    vocab = set()
    for line in fin:
        for word in line.split():
            vocab.add(word)
    return vocab


def train_simple(corpus_path, output_dict_path, vector_size=8):
    print("Загрузка корпуса...")
    documents = load_corpus(corpus_path)
    
    print("Обучение модели Word2Vec...")
    model = Word2Vec(sentences=documents, vector_size=vector_size, min_count=1)
    
    print("Извлечение словаря...")
    dictionary = {key : model.wv[key] for key in model.wv.key_to_index}
    
    print("Сохранение словаря...")
    save_dictionary(output_dict_path, dictionary, (len(dictionary), vector_size))
    print("Готово!")


def train_memory_safe(corpus_path, output_dict_path, vector_size=8, chunk_size=1000):
    print("Сбор уникального словаря (vocab)...")
    vocab = get_vocab(corpus_path)
    
    print("Инициализация базовой модели...")
    model = Word2Vec(vector_size=vector_size, min_count=1)
    model.build_vocab(vocab)
    model.save('saved_model')
    
    print("Потоковое обучение батчами...")
    with io.open(corpus_path, 'r', encoding='utf-8', newline='\n', errors='ignore') as file:
        eof = False
        while not eof:
            limit = chunk_size
            documents = []
            for line in file:
                documents.append(line.split())
                limit -= 1
                if limit == 0:
                    break
            else:
                eof = True
                
            # Загружаем, обновляем и сохраняем модель для текущего батча
            model = Word2Vec.load('saved_model')
            model.build_vocab(documents, update=True)
            model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
            model.save('saved_model')
            
    print("Извлечение и сохранение итогового словаря...")
    dictionary = {key : model.wv[key] for key in model.wv.key_to_index}
    save_dictionary(output_dict_path, dictionary, (len(dictionary), vector_size))
    print("Готово!")

if __name__ == "__main__":
    train_simple('polish_corpus.txt', 'polish_cbow_dictionary.txt', vector_size=100)
    # train_memory_safe('polish_corpus.txt', 'polish_lit_dictionary.txt', vector_size=100)