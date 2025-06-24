import os
import sys
import torch
from datetime import datetime
from ultralytics import YOLO

if torch.cuda.is_available():
    print("Current GPU:", torch.cuda.get_device_name(torch.cuda.current_device()))
    device = torch.device("cuda")
else:
    print("No GPU available.")
    sys.exit("Exiting script: No GPU available. 😢")  

dataset_path = "data.yaml"
save_dir = "runs"

def train_new():
    model_name = "yolo11n.pt"
    run_name = input("Please enter the run name: ")
    model = YOLO(model_name)
    
    training_params = {
        'data': dataset_path,
        'imgsz': 640, #1024
        'epochs': 150,
        'batch': 16,
        'patience': 15,
        'cos_lr': True,
        'augment': True,
        'save': True,
        'project': save_dir,
        'name':  f'{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{model_name.split(".")[0]}_{run_name}'
    }

    results = model.train(**training_params)

def train_resume():
    while True:
        run_name = input("Please enter the run name to resume, it can be found in the runs folder: ")
        weights_path = os.path.join(save_dir, run_name, "weights", "last.pt")

        if os.path.exists(weights_path):
            break
        else:
            print(f"Run name '{run_name}' not found. Please try again.")

    model = YOLO(weights_path)

    resume_params = {
        'resume': True,
        'warmup_epochs': 0,
        'data': dataset_path,
        'project': save_dir,
        'name': run_name
    }

    model.train(**resume_params)

def main():
    while True:
        print("\nChoose an option:")
        print("1. Train a new model")
        print("2. Resume training a model")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            train_new()
        elif choice == '2':
            train_resume()
        elif choice == '3':
            print("Blowing up the server and deleting all the files...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
