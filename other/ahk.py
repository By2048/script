import os

folder_path = "E:\Sync\Ahk"

all_ahk_file = []
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.ahk'):
            file_path = os.path.join(root, file)
            all_ahk_file.append(file_path)

for file_path in all_ahk_file:
    print(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as file_test:
            pass
    except UnicodeDecodeError:
        continue

    with open(file_path, "r", encoding="utf-8") as file_read:
        file_data = file_read.readlines()
        with open(file_path, "w", encoding="utf-8-sig") as file_write:
            file_write.writelines(file_data)
