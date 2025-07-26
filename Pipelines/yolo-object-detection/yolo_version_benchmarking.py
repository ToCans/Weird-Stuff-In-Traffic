import os
import sys
import torch
from datetime import datetime
from ultralytics import YOLO

if torch.cuda.is_available():
    print("Current GPU:", torch.cuda.get_device_name(torch.cuda.current_device()))
    device = torch.device("cuda")
else:
    sys.exit("Exiting script: No GPU available. 😢")  

save_dir = "runs/benchmarks"
yolo_versions = ["12n","11n"]
#yolo_versions = ["12n","11n","v10n", "v9t", "v8n"]

def update_yaml_file(iteration_number):
    dataset_path = f"iteration_2_{iteration_number}/train/images"
    val_path = f"iteration_2_{iteration_number}/val/images"
    test_path = f"iteration_2_{iteration_number}/test/images"
    
    yaml_content = f"""
train: {dataset_path}
val: {val_path}
test: {test_path}

nc: 1
names: ['Anomaly']
"""
    with open("data_iterate.yaml", "w") as file:
        file.write(yaml_content)

def train(yolo_version, iteration_number):
    # Construct the model name using the version
    model_name = f"yolo{yolo_version}.pt"
    model = YOLO(model_name)
    
    training_params = {
        'data': "data_iterate.yaml",
        'imgsz': 640,
        'epochs': 1,
        'patience': 25,
        'cos_lr': True,
        'batch': 16,
        'save': True,
        'project': save_dir,
        'name': f'{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{model_name.split(".")[0]}_iter{iteration_number}'
    }

    results = model.train(**training_params)

def main(max_iterations):
    for iteration_number in range(1, max_iterations + 1):
        print(f"Updating dataset path for iteration: {iteration_number}")
        update_yaml_file(iteration_number)
        
        for version in yolo_versions:
            print(f"Training YOLO model version: {version} on iteration {iteration_number}")
            train(version, iteration_number)

    print("Benchmarking Complete! 🥳")

if __name__ == "__main__":
    max_iterations = int(input("Enter the number of iterations: "))
    main(max_iterations)
