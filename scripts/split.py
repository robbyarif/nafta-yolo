import random
import shutil
from pathlib import Path


def split_dataset(source_dir, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42):
    """Splits a dataset into train, val, and test sets."""
    random.seed(seed)

    source_dir = Path(source_dir)
    images_dir = source_dir / "images"
    labels_dir = source_dir / "labels"
    split_path = Path(f"{source_dir}_split")
    split_path.mkdir(parents=True, exist_ok=True)

    all_images = list(images_dir.glob("*"))
    random.shuffle(all_images)

    total_images = len(all_images)
    train_end = int(total_images * train_ratio)
    val_end = train_end + int(total_images * val_ratio)

    splits = {
        "train": all_images[:train_end],
        "val": all_images[train_end:val_end],
        "test": all_images[val_end:],
    }

    for split_name, image_files in splits.items():
        split_out_dir = split_path / split_name
        split_out_dir.mkdir(parents=True, exist_ok=True)

        for img_path in image_files:
            label_path = labels_dir / img_path.name.replace(img_path.suffix, ".txt")
            shutil.copy(img_path, split_out_dir / img_path.name)
            if label_path.exists():
                shutil.copy(label_path, split_out_dir / label_path.name)

    print("Dataset split completed successfully!")