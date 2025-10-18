from scripts.split import split_dataset
from pathlib import Path
from ultralytics import YOLO

def main():
    # source_directory = Path("datasets/Benz")  # Path to the dataset directory
    # split_dataset(source_directory, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42)
    source_directory = Path("datasets/Benz_split")  # Path to the dataset directory

    # Load a model
    # model = YOLO("yolo11n-seg.pt")  # load a pretrained model (recommended for training)

    # Train the model
    # results = model.train(data="nafta-benz-seg.yaml", epochs=100, imgsz=640)

    # Inference
    model = YOLO("runs/segment/train6/weights/best.pt")  # load a trained model
    results = model.predict(source_directory / "test", conf=0.25, save=True, save_txt=True, project="Benz_result", name="image_predictions")


if __name__ == "__main__":
    main()