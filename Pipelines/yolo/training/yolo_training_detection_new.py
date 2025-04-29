# %% [markdown]
# ## Yolov11 Training Pipeline

# %% [markdown]
# ---

# %% [markdown]
# #### Key Sections
# 
# 1. [Training Setup](#training-setup)
# 2. [Training](#training)
# 3. [Hyperparameter Tuning](#hyperparameter-tuning)

# %% [markdown]
# ---

# %% [markdown]
# ### Training Setup

# %% [markdown]
# ##### Imports

# %%
import os
import gc
import re
import cv2
import random
import shutil
import torch
import warnings
import torchvision
from datetime import datetime
from ultralytics import YOLO
import matplotlib.pyplot as plt

# %% [markdown]
# ##### Package Versions

# %%
print("Torch version:", torch.__version__)
print("Torchvision version:", torchvision.__version__)
print("Is torch available?",torch.cuda.is_available())

# %% [markdown]
# ### Disable Warnings

# %%
warnings.filterwarnings("ignore")

# %% [markdown]
# ### Setting Training Device

# %%
# Defining Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Printing Necessary CUDA Info
if str(device) == "cuda":
    print(f"Using GPU {torch.cuda.get_device_properties(device)}")
    print("# of CUDA devices available:", torch.cuda.device_count())
else:
    print("Using CPU")

# %% [markdown]
# ### Emptying the GPU Cache (if necessary)

# %%
# Cleaning out the device cache
def empty_cache() -> None:
    gc.collect()
    torch.cuda.empty_cache()

# Displaying the free memory
def print_free_memory():
    free, total = torch.cuda.mem_get_info(device)
    print(f"Percent of free memory: {round(free/total *100,2)}")

# Running GPU info related functions
empty_cache()
print_free_memory()

# %% [markdown]
# ### Memory Summary

# %%
# Memory Summary Function
def memory_summary() -> None:
    print(torch.cuda.memory_summary())

# Running memory summary funciton
memory_summary()

# %% [markdown]
# ### Preparing GPU (if necessary)
# 

# %%
# For AMD GPU - 7800xt
device_name = torch.cuda.get_device_name(0)
if "AMD" in device_name or "Radeon" in device_name:
    os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

print(f"GPU {torch.cuda.get_device_properties(device).name} is now setup")

# %% [markdown]
# ##### Local Setting Paths for Data, Base Model, and Output Directory
# 

# %%
# Directory Paths
training_dataset_name = "coco8" # Change this once we have the necessary data
yaml_training_dataset_name = "coco8.yaml" # Change this once we have the necessary data

# Flexible Data Paths (needed for THI server)
current_directory = os.getcwd()
path_to_base_directory = re.search(rf"(.*?){"Weird-Stuff-In-Traffic"}", current_directory).group(1)
training_yaml_data_path = f"Weird-Stuff-In-Traffic/Data/yolo/{training_dataset_name}/{yaml_training_dataset_name}"
complete_training_data_path = path_to_base_directory + training_yaml_data_path

# Model Paths
model_name = "yolo11n.pt"
simple_model_name = model_name.split(".")[0]

# %% [markdown]
# ---

# %% [markdown]
# ### Training

# %% [markdown]
# ##### Training - Loading Model

# %%
# Loading Model
model = YOLO(model_name)

# %% [markdown]
# ##### Training - Training Configuration and Output Paths

# %%
# Model Training Configurations
epochs = 3
image_size = 640
batch_size = 64

# Output Folder Name
output_folder_name = f'{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{simple_model_name}_{training_dataset_name}_{image_size}cuts_{epochs}epoch'

# Model Storage and Results Path
training_results_path = f"Weird-Stuff-In-Traffic/Models/Segmentation-Detection/yolo/"
complete_training_results_path = path_to_base_directory + training_results_path + output_folder_name

# %% [markdown]
# ##### Training - Training Parameters

# %%
# Model Training Parameters
training_params = {
    'data': complete_training_data_path, # Local Dataset
    'imgsz': image_size, #1024
    'epochs': epochs,
    'batch': batch_size,
    'patience': 20,
    'cos_lr': True,
    #'rect': True,
    'augment': True,
    #'hsv_s': 0.45,
    #'hsv_v': 0.3,
    #'auto_augment': 'autoaugment',
    'save': True,
    'project': complete_training_results_path, # Local Save Directory
    'name':  output_folder_name # Output Folder Name
}

# %% [markdown]
# ##### Training - Training Model

# %%
results = model.train(**training_params)

# %% [markdown]
# ##### Training - Printing Key Training Metrics

# %%
# After training, print the most important metrics
print("\n### Training completed. ### \n\n Key metrics:")
print(f"X (all classes): {results.box.map:.4f}")  #??
print(f"mAP50 (all classes): {results.box.map50:.4f}")
print(f"mAP50-95 (all classes)??: {results.box.map75:.4f}")  # This might be mAP50-95??
#print(f"Precision: {results.box.p:.4f}")
#print(f"Recall: {results.box.r:.4f}")

# Print class-specific metrics if available
if hasattr(results, 'names'):
    print("\nClass-specific metrics:")
    for i, class_name in results.names.items():
        print(f"{class_name}:")
        print(f"  Precision: {results.box.p[i]:.4f}")
        print(f"  Recall: {results.box.r[i]:.4f}") 
        #print(f"  mAP50: {results.box.map50[i]:.4f}") # This breaks the code, revisit later
        #print(f"  mAP50-95: {results.box.map[i]:.4f}") # This breaks the code, revisit later

# %% [markdown]
# ---

# %% [markdown]
# ### Hyperparameter Tuning

# %% [markdown]
# ##### Builtin ray tune (Hyperband)

# %%
'''
from ultralytics import YOLO
from ray import tune

model_name = "yolo11n.pt"
model = YOLO(model_name)
hypp_space = {}

result_grid = model.tune(
    device='cuda:0',
    data=dataset_path,
    iterations=3,
    grace_period = 2,
    name="tune_exp_1", 
    #space = hypp_space,
    #resume=True,
    imgsz=1024,
    epochs=2,
    batch=24,
    project=save_dir,
    use_ray=True)
'''


# %% [markdown]
# ##### Builtin YOLO tune (genetic algorithm)

# %%
'''
from ultralytics import YOLO

model_name = "yolo11n.pt"
model = YOLO(model_name)
hypp_space = {}

model.tune(
    device='cuda:0',
    data=dataset_path,
    epochs=30,
    name="tune_exp_1", 
    imgsz=1024,
    batch=24,
    iterations=300,
    optimizer="AdamW",
    plots=True,
    save=False,
    val=False,
)
'''

# %% [markdown]
# ##### Custom Optuna trial (Bayesian optimization)

# %%
'''
import optuna
from ultralytics import YOLO

def objective(trial):
    # Define hyperparameters to optimize
    lr = trial.suggest_float('lr0', 1e-5, 1e-2, log=True)
    weight_decay = trial.suggest_float('weight_decay', 0.0001, 0.01)
    dropout = trial.suggest_float('dropout', 0.0, 0.5)
    batch_size = trial.suggest_categorical('batch_size', [8, 16, 32, 64])
    
    # Initialize YOLO model
    model = YOLO('yolov8n.yaml')  
    
    # Train with suggested hyperparameters
    results = model.train(
        data='coco128.yaml',
        epochs=50,
        batch=batch_size,
        lr0=lr,
        weight_decay=weight_decay,
        dropout=dropout,
        verbose=False  # Reduce output clutter
    )
    
    # Return the metric to optimize 
    return results.results_dict['metrics/mAP50-95(B)']

# Create study and optimize
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)

# Print best results
print('Best trial:')
trial = study.best_trial
print(f'  Value: {trial.value}')
print('  Params: ')
for key, value in trial.params.items():
    print(f'    {key}: {value}')
'''


