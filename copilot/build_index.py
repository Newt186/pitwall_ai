
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
    return "\n\n".join(all_text)
load_f = load_texts()
print(load_f)

    

