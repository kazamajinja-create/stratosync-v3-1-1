import os
import shutil

def move_files_to_folder(base_path, mapping):
    for folder, patterns in mapping.items():
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        for pattern in patterns:
            for file in os.listdir(base_path):
                if pattern in file and os.path.isfile(os.path.join(base_path, file)):
                    shutil.move(os.path.join(base_path, file), os.path.join(folder_path, file))
                    print(f"Moved {file} to {folder}/")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_map = {
        "core": ["zent_engine", "zent_quantum", "cluster_engin"],
        "modes": ["Mode", "mode", "V4.3_", "V4.2_"],
        "guardian": ["Guardian99", "SENJYU_PARTNE"],
        "nft": ["NFT_", "SENJYU_NFT"],
        "patches": ["patch_", "fix", "update"],
        "ui": ["my_page", "dashboard", "UI", "spec"],
    }
    move_files_to_folder(base_dir, folder_map)
