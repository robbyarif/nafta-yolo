# Convert Labelbox JSON labels to YOLO format
# Adapted from https://github.com/ultralytics/JSON2YOLO/blob/main/labelbox_json2yolo.py

import json
import os
from pathlib import Path

import requests
import yaml
from PIL import Image
from tqdm import tqdm
import shutil

def convert(file, zip=True):
    """Converts Labelbox JSON labels to YOLO format and saves them, with optional zipping."""
    names = []  # class names
    file = Path(file)
    with open(file) as f:
        data = json.load(f)  # load JSON

    for img in tqdm(data, desc=f"Converting {file}"):
        im_path = img["Labeled Data"]
        im = Image.open(requests.get(im_path, stream=True).raw if im_path.startswith("http") else im_path)  # open
        width, height = im.size  # image size
        label_path = save_dir / "labels" / Path(img["External ID"]).with_suffix(".txt").name
        image_path = save_dir / "images" / img["External ID"]
        im.save(image_path, quality=95, subsampling=0)

        for label in img["Label"]["objects"]:
            # box
            top, left, h, w = label["bbox"].values()  # top, left, height, width
            xywh = [(left + w / 2) / width, (top + h / 2) / height, w / width, h / height]  # xywh normalized

            # class
            cls = label["value"]  # class name
            if cls not in names:
                names.append(cls)

            line = names.index(cls), *xywh  # YOLO format (class_index, xywh)
            with open(label_path, "a") as f:
                f.write(("%g " * len(line)).rstrip() % line + "\n")

    # # Save dataset.yaml
    # d = {
    #     "path": f"../datasets/{file.stem}  # dataset root dir",
    #     "train": "images/train  # train images (relative to path) 128 images",
    #     "val": "images/val  # val images (relative to path) 128 images",
    #     "test": " # test images (optional)",
    #     "nc": len(names),
    #     "names": names,
    # }  # dictionary

    # with open(save_dir / file.with_suffix(".yaml").name, "w") as f:
    #     yaml.dump(d, f, sort_keys=False)

    # # Zip
    # if zip:
    #     print(f"Zipping as {save_dir}.zip...")
    #     os.system(f"zip -qr {save_dir}.zip {save_dir}")

    print("Conversion completed successfully!")

def parse_labelbox_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    entries = parse_labelbox_json(Path("../datasets/Labels/Annotations.json"))
    i = 0
    images_dir = Path("../datasets/Images/Drone/")
    labels_dir = Path("../datasets/yolo_labels")
    out_images = Path("../datasets/yolo_images")
    log_path = Path("../datasets/labelbox_to_yolo.log")
    written = 0
    file_not_found = []
    for entry in entries:
        img_name = entry["External ID"]
        img_path = images_dir / img_name
        label_path = labels_dir / img_name.replace('.jpg', '.txt').replace('.png', '.txt').replace('.jpeg', '.txt')
        labeled_data = entry["Labeled Data"]
        
        label = entry["Label"]
        if "Oil-Spill" in label:
            print(img_name)
            if not img_path.exists():
                print(f"Image not found: {img_path}")
                file_not_found.append(img_name + ", viewpoint: " + label["viewpoint"])
                continue
                # try:
                #     print(f"Downloading {labeled_data} -> {out_images / img_name}")
                #     resp = requests.get(labeled_data, stream=True, timeout=15)
                #     resp.raise_for_status()
                #     with open(out_images / img_name, "wb") as out_f:
                #         for chunk in resp.iter_content(chunk_size=8192):
                #             if chunk:
                #                 out_f.write(chunk)
                #     print(f"Downloaded {img_name}")
                #     file_not_found.append(img_name + " (downloaded)")
                # except Exception as e:
                #     print(f"Failed to download {url}: {e}")
                #     file_not_found.append(img_name)
                #     continue
            with Image.open(img_path) as im:
                w,h = im.size
                print(f"Image size: {w}x{h}")
            geom = label["Oil-Spill"]
            cls = 0
            lines = []
            for g in geom:
                # print(g)
                line = f"{cls} "
                for points in g["geometry"]:
                    # print(points)
                    line += f"{points['x']/w:.6f} {points['y']/h:.6f} "
                lines.append(line)
            
            with label_path.open('w', encoding='utf-8') as f:
                for L in lines:
                    f.write(L + '\n')
                written += 1
            print(img_path)
            shutil.copy2(img_path, out_images / img_name)
        

    with log_path.open('w', encoding='utf-8') as f:
        f.write(f"Images not found:\n")
        for file in file_not_found:
            f.write(file + '\n')
        f.write(f"Total images not found: {len(file_not_found)}\n")
        f.write(f"Total labels written: {written}\n")

    print(f"Written {written} labels, {len(file_not_found)} images not found.")

        

    # convert("../datasets/Labels/Annotations.json", zip=False)