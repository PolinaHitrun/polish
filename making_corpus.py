import glob
import tqdm

def make_corpus(input_path, output_file_path):
    file_list = sorted(glob.glob(input_path + '/*'))
    
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for file in tqdm.tqdm(file_list):
            with open(file, 'r', encoding='utf-8') as input_file:
                output_file.write(input_file.read().replace('\n', ' '))
                output_file.write('\n')

if __name__ == "__main__":
    input_directory = 'preprocessed'
    corpus_file = 'polish_corpus.txt'
    
    print("Сборка корпуса...")
    make_corpus(input_directory, corpus_file)
    print(f"Корпус сохранен в {corpus_file}")