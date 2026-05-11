from sentence_transformers import SentenceTransformer
import faiss as fs
import os
import numpy as np

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

def build_index(all_chunks):
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    en_code = model.encode(all_chunks)
    #converting into numpy array
    encoded_array = np.array(en_code, dtype=np.float32)
    
    index = fs.IndexFlatL2(encoded_array.shape[1])
    index.add(encoded_array)
    return index

    
if __name__ == "__main__":
    load_f = load_texts()
    print(load_f)
slice_f = split_into_chunks(load_f)
print(slice_f)
build_i = build_index(slice_f)
print(build_i)
    

