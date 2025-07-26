import os
import sys
import torch
import optuna
from datetime import datetime
from ultralytics import YOLO

if torch.cuda.is_available():
    print("Current GPU:", torch.cuda.get_device_name(torch.cuda.current_device()))
    device = torch.device("cuda")
else:
    sys.exit("Exiting script: No GPU available. 😢")  

dataset_path = "data.yaml"
save_dir = "runs"

# Load the study from the .db file
study = optuna.load_study(
    study_name='yolo_optimization',  
    storage='sqlite:///yolo_optuna_11n.db'  
)

# Get all trials from the study
trials = study.trials

# Filter out trials with None values
valid_trials = [trial for trial in trials if trial.value is not None]

# Sort trials by the objective value
sorted_trials = sorted(valid_trials, key=lambda x: x.value, reverse=True)

def train_with_trial(trial_index):
    # Ensure the trial index is within the range of sorted_trials
    if trial_index < 0 or trial_index >= len(sorted_trials):
        raise ValueError("Invalid trial index. Please provide a valid index.")

    # Retrieve the trial using the trial index
    trial = sorted_trials[trial_index]
    
    # Generate a unique run name using the trial index
    run_name = f"trial_{trial_index+1}"

    model_name = "yolo11n.pt"
    model = YOLO(model_name)
    
    training_params = {
        'data': dataset_path,
        'imgsz': 640,
        'epochs': 1,
        'patience': 25,
        'cos_lr': trial.params.get('cos_lr', True),
        
        # Use trial parameters
        'lr0': trial.params['lr0'],
        'lrf': trial.params['lrf'],
        'momentum': trial.params['momentum'],
        'optimizer': trial.params['optimizer'],
        'batch': trial.params['batch_size'],
        'weight_decay': trial.params['weight_decay'],
        'dropout': trial.params['dropout'],
        'freeze': trial.params['freeze'],
        'warmup_epochs': trial.params['warmup_epochs'],
        'warmup_momentum': trial.params['warmup_momentum'],
        'box': trial.params['box'],
        'cls': trial.params['cls'],
        'hsv_h': trial.params['hsv_h'],
        'hsv_s': trial.params['hsv_s'],
        'hsv_v': trial.params['hsv_v'],
        'degrees': trial.params['degrees'],
        'translate': trial.params['translate'],
        'scale': trial.params['scale'],
        'shear': trial.params['shear'],
        'perspective': trial.params['perspective'],
        'flipud': trial.params['flipud'],
        'fliplr': trial.params['fliplr'],
        'mosaic': trial.params['mosaic'],
        'mixup': trial.params['mixup'],
        'cutmix': trial.params['cutmix'],

        'save': True,
        'project': save_dir,
        'name': f'{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{model_name.split(".")[0]}_{run_name}'
    }

    results = model.train(**training_params)

def main():
    try:
        # Ask the user for the number of best trials to run
        num_trials = int(input("Enter the number of best trials to run: "))
        
        # Ensure the number of trials is within the valid range
        if num_trials < 1 or num_trials > len(sorted_trials):
            raise ValueError("Invalid number of trials. Please enter a number between 1 and the total number of valid trials.")

        # Run training for the specified number of best trials
        for trial_index in range(num_trials):
            print(f"Running training for trial {trial_index + 1}...")
            train_with_trial(trial_index)
            print(f"Training completed for trial {trial_index + 1}.\n")

    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()