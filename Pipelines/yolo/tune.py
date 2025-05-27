from ultralytics import YOLO
import optuna

# EDIT BEFORE START
dataset_path = "data.yaml" #.yaml file path
save_dir = "runs"
epochs = 3
patience = 10
n_trials = 5

def objective(trial):

    # Optimization parameters
    lr0 = trial.suggest_float('lr0', 1e-5, 1e-2, log=True)  # Initial learning rate
    lrf = trial.suggest_float('lrf', 0.01, 1.0)  # Final learning rate factor
    momentum = trial.suggest_float('momentum', 0.8, 0.98)  # SGD momentum or Adam beta1
    optimizer_name = trial.suggest_categorical('optimizer', ["Adam", 'AdamW', "RMSProp"])  # Optimizer type
    batch_size = trial.suggest_categorical('batch_size', [8, 16, 24, 32])  # Batch size
    cos_lr = trial.suggest_categorical('cos_lr', [True, False])  # Cosine learning rate schedule
    
    # Regularization parameters
    weight_decay = trial.suggest_float('weight_decay', 0.0001, 0.01)  # Weight decay
    dropout = trial.suggest_categorical('dropout', [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])  # Dropout rate
    freeze = trial.suggest_int('freeze', 0, 8)  # Number of layers to freeze

    # Warmup parameters
    warmup_epochs = trial.suggest_float('warmup_epochs', 0.0, 5.0)  # Warmup epochs
    warmup_momentum = trial.suggest_float('warmup_momentum', 0.0, 0.95)  # Warmup momentum

    # Loss function parameters
    box = trial.suggest_float('box', 0.02, 0.2)  # Bounding box loss weight
    cls = trial.suggest_float('cls', 0.2, 4.0)  # Classification loss weight

    # Augmentation parameters
    hsv_h = trial.suggest_float('hsv_h', 0.0, 0.1)  # Hue augmentation
    hsv_s = trial.suggest_float('hsv_s', 0.0, 0.9)  # Saturation augmentation
    hsv_v = trial.suggest_float('hsv_v', 0.0, 0.9)  # Brightness augmentation
    degrees = trial.suggest_float('degrees', 0.0, 45.0)  # Rotation degrees
    translate = trial.suggest_float('translate', 0.0, 0.2)  # Translation
    scale = trial.suggest_float('scale', 0.0, 0.9)  # Scale gain
    shear = trial.suggest_float('shear', 0.0, 10.0)  # Shear degrees
    perspective = trial.suggest_float('perspective', 0.0, 0.001)  # Perspective
    flipud = trial.suggest_float('flipud', 0.0, 0.5)  # Flip up-down probability
    fliplr = trial.suggest_float('fliplr', 0.0, 0.5)  # Flip left-right probability
    mosaic = trial.suggest_float('mosaic', 0.0, 1.0)  # Mosaic probability
    mixup = trial.suggest_float('mixup', 0.0, 0.3)  # Mixup probability
    cutmix = trial.suggest_float('cutmix', 0.0, 1.0)  # Cutmix probability

    # Initialize YOLO model
    model = YOLO('yolo11n.pt')  
    
    # Train with suggested hyperparameters
    results = model.train(
        device=0,
        data=dataset_path,
        epochs=epochs,  
        patience=patience,  
        close_mosaic = 0,

        batch=batch_size,
        lr0=lr0,
        lrf=lrf,  
        weight_decay=weight_decay,
        optimizer=optimizer_name,  # Must NOT be "auto", else it overrides lr & momentum
        cos_lr = cos_lr,
        
        freeze=freeze,
        momentum=momentum,
        dropout=dropout,
        warmup_epochs=warmup_epochs,  
        warmup_momentum=warmup_momentum,  
        box=box,  
        cls=cls,  

        verbose=False,  # Reduce output clutter
        save=False,
        save_period=0,

        # Augmentation parameters
        hsv_h=hsv_h,
        hsv_s=hsv_s,
        hsv_v=hsv_v,
        degrees=degrees,
        translate=translate,
        scale=scale,
        shear=shear,
        perspective=perspective,
        flipud=flipud,
        fliplr=fliplr,
        mosaic=mosaic,
        mixup=mixup,
        #cutmix=cutmix,
    )
    
    # Return the metric to optimize 
    return results.results_dict['metrics/mAP50-95(B)']

# Create study and optimize
study = optuna.create_study(
    direction='maximize',    # We want to maximize mAP50-95
    study_name='yolo_optimization',
    storage='sqlite:///yolo_optuna.db',
    load_if_exists=True,  # continue existing study if found in dir 
)
study.optimize(objective, n_trials=n_trials)

# Print best results
print('Best trial:')
trial = study.best_trial
print(f'  Value: {trial.value}')
print('  Params: ')
for key, value in trial.params.items():
    print(f'    {key}: {value}')
