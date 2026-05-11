
import os

def load_texts():
    all_text = []

    folder_path = "data/raw"

    for file_name in os.listdir(folder_path):
                if file_name.endswith(".txt"):
                        file_path = os.path.join("data/raw/", file_name)
                        with open(file_path, 'r', encoding = 'utf-8') as f: 
                            file = f.read()
                            print(file)
                            all_text.append(file)
    return "\n\n ".join(all_text)

def split_into_chunks(text):
    
    
    all_chunks =[]
    total_length = len(text)
    chunks_size = 400
    overlap = 50
    start = 0

    while start < total_length:
        sliced_text = text[start : start +  chunks_size] 
        all_chunks.append(sliced_text)
        gap = chunks_size - overlap 
        start = start + gap
    return all_chunks 
    

load_f = load_texts()
print(load_f)
slice_f = split_into_chunks(load_f)
print(slice_f)

    

