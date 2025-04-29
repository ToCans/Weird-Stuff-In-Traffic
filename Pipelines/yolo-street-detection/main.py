from lib.imports import *
from lib.misc import *

for image_size in [256]: # might get stuck before starting 2nd batch, if this happens just restart this cell
    train_model(pretrained_model='models/yolo11s-seg.pt', save_name=f"training_{image_size}_autotrain", imgsz=image_size, epochs=100, batch=512, amp=True, usecomet=False)
