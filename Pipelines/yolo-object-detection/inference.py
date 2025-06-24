import matplotlib.pyplot as plt
from ultralytics import YOLO

def main():
    model = YOLO("best.pt")

    img_dir = "inference/input/images"
    save_dir = "inference/results"
    experiment = "test_" # Can be a unique identifier from the backend

    model.predict(source=img_dir,
                            device = 0, # cuda = 0, else "cpu"
                
                            imgsz= 640,
                            conf=0.4, # higher conf = lower false positives
                            iou= 0.7,
                            half = False, # half precision = faster inference, minimal accuracy loss
                            batch = 5, # batch size to process images, only works with csv or directories
                            max_det=2,
                            
                
                            show = False, # show results
                            show_labels = False, # also applies to saved results
                            show_conf = False, # also applies to saved results, only works if show_labels = True
                            show_boxes = True, # draws bboxes on detections
                
                            save=True, # saves output images with bboxes
                            save_txt=True, # saves annotations in a labels folder in the experiment dir
                            save_conf=True, # maybe needed for scoring NOTE, if true, conf will be saved as the last value in the line
                        
                            project=save_dir,
                            name=experiment,
                )

    """
    Add logic to compare results against ground truth in input\labels
    """


    print(f"Results saved to {save_dir}/{experiment}")


if __name__ == "__main__":
    main()