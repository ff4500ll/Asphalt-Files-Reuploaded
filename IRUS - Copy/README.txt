================================================================================
                    FISHING DETECTION - PROJECT DOCUMENTATION
================================================================================

PROJECT OVERVIEW:
-----------------
This project uses YOLO (You Only Look Once) object detection to identify:
  1. Target Line
  2. Fish Bar

The system captures screenshots, trains a model, and runs live detection on a
specified screen area (fish_box) defined in Config.txt.


================================================================================
                              FILE STRUCTURE
================================================================================

Root Directory:
├── p.py                    - GUI for configuring hotkeys and fish_box area
├── a.py                    - Screenshot capture tool (takes 100 screenshots)
├── b.py                    - Live detection (runs trained model in real-time)
├── train.py                - Model training script
├── organize_dataset.py     - Organizes dataset into proper YOLO format
├── Config.txt              - Configuration file (hotkeys, fish_box coordinates)
├── fishing_model.pt        - Trained YOLO model (created after training)
└── README.txt              - This file

Images Directory Structure:
Images/
├── Flimsy Rod/             - Raw screenshots (100 images from a.py)
│   ├── Bar_1.png
│   ├── Bar_2.png
│   └── ...
│
└── Processed/              - Annotated datasets
    ├── 100 Flimsy Rod/     - First dataset (100 images annotated)
    │   ├── data.yaml
    │   ├── images/
    │   │   ├── train/      (80% of images)
    │   │   └── val/        (20% of images)
    │   └── labels/
    │       ├── train/      (80% of labels)
    │       └── val/        (20% of labels)
    │
    └── [Future Datasets]/  - Add new datasets here with different names
        ├── 200 Better Rod/
        ├── 150 Gold Rod/
        └── etc...


================================================================================
                            COMPLETE WORKFLOW
================================================================================

STEP 1: CONFIGURE SETTINGS
---------------------------
Run: python p.py

- Set hotkeys (F4=Start, F5=Stop, F6=Modify Area, F7=Exit)
- Press F6 to define the fish_box area on screen
- Drag the blue box to select the fishing area
- Press Enter or F6 again to save
- This saves to Config.txt


STEP 2: CAPTURE SCREENSHOTS
----------------------------
Run: python a.py

- Press F1 to start capturing screenshots
- Takes 100 screenshots (1 every 500ms) of the fish_box area
- Press F2 to pause, F1 to resume
- Press F3 for emergency shutdown
- Images saved to: Images/Flimsy Rod/Bar_1.png to Bar_100.png


STEP 3: ANNOTATE IN CVAT
-------------------------
1. Go to https://www.cvat.ai/ (or your CVAT instance)
2. Create a new project with 2 labels:
   - Target Line
   - Fish Bar
3. Upload all 100 images from Images/Flimsy Rod/
4. Annotate each image by drawing bounding boxes around:
   - The target line (where you need to stop)
   - The fish bar (the moving indicator)
5. Export as: "Ultralytics YOLO Detection Track 1.0"
6. Save export to: Images/Processed/[Dataset Name]/
   Example: Images/Processed/100 Flimsy Rod/


STEP 4: ORGANIZE DATASET
-------------------------
Run: python organize_dataset.py

This script:
- Finds images in Images/Flimsy Rod/
- Finds labels in Images/Processed/100 Flimsy Rod/labels/train/
- Creates proper YOLO structure (train/val split 80/20)
- Generates data.yaml configuration file

After running, your dataset structure will be:
Images/Processed/100 Flimsy Rod/
├── data.yaml
├── images/
│   ├── train/  (80 images)
│   └── val/    (20 images)
└── labels/
    ├── train/  (80 label files)
    └── val/    (20 label files)


STEP 5: TRAIN THE MODEL
------------------------
Run: python train.py

Recommended settings:
- Epochs: 100 (will stop early if model converges)
- Batch size: 8 (CPU) or 16-32 (GPU)
- Image size: 640
- Device: cpu (or 0 for GPU if CUDA available)

Training will:
- Use YOLOv8 nano model (fast and efficient)
- Train for up to 100 epochs with early stopping
- Save best model as: fishing_model.pt
- Save training results to: runs/fishing_detection/

Expected training time:
- CPU: 30-90 minutes
- GPU (RTX 4070 Super): 5-15 minutes


STEP 6: RUN LIVE DETECTION
---------------------------
Run: python b.py

This will:
- Load fishing_model.pt
- Capture fish_box area from Config.txt in real-time
- Show live feed with detected objects:
  * Target Line - Green bounding box
  * Fish Bar - Red bounding box
- Display confidence scores and FPS

Controls:
- Press ESC or Q to exit


================================================================================
                        ADDING MORE TRAINING DATA
================================================================================

To add more data and retrain with a larger/different dataset:

METHOD 1: NEW SEPARATE DATASET
-------------------------------
1. Clear Images/Flimsy Rod/ (or move old images elsewhere)
2. Run a.py to capture new screenshots
3. Annotate in CVAT
4. Export to: Images/Processed/[NEW DATASET NAME]/
   Example: Images/Processed/200 Better Rod/
5. Update organize_dataset.py to point to new dataset folder
6. Run organize_dataset.py
7. Run train.py to train new model


METHOD 2: COMBINE MULTIPLE DATASETS
------------------------------------
To combine multiple datasets for better training:

1. Manually merge datasets:
   - Copy all images from multiple processed datasets into one
   - Copy all labels from multiple processed datasets into one

2. Or modify organize_dataset.py to read from multiple sources

3. Example structure for combined dataset:
   Images/Processed/Combined_300_Images/
   ├── images/
   │   ├── train/  (from multiple datasets)
   │   └── val/
   └── labels/
       ├── train/
       └── val/


METHOD 3: INCREMENTAL TRAINING (TRANSFER LEARNING)
---------------------------------------------------
1. Take new screenshots with a.py
2. Annotate in CVAT
3. Organize into new dataset folder
4. In train.py, modify to load existing fishing_model.pt instead of yolov8n.pt
5. Train for fewer epochs (20-50) to fine-tune on new data


================================================================================
                          TROUBLESHOOTING
================================================================================

ISSUE: "No CUDA GPU detected" when I have a GPU
-------------------------------------------------
Solution: Install CUDA-enabled PyTorch
  pip uninstall torch torchvision torchaudio
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

Note: Requires Python 3.12 or lower (PyTorch doesn't support 3.14 yet)


ISSUE: "'train' and 'val' are required in all data YAMLs"
----------------------------------------------------------
Solution: Run organize_dataset.py to create proper YOLO structure


ISSUE: Training is very slow
-----------------------------
Solution:
- Reduce batch size to 4 or 8
- Reduce image size to 416
- Reduce epochs to 50
- Use GPU instead of CPU


ISSUE: Model detects nothing / low accuracy
--------------------------------------------
Solution:
- Collect more training data (200-500+ images)
- Ensure annotations are accurate in CVAT
- Train for more epochs
- Check that fish_box area is consistent between training and detection


ISSUE: Live detection window is laggy
--------------------------------------
Solution:
- Close other programs
- Reduce detection confidence threshold in b.py
- Use smaller YOLO model (yolov8n is already smallest)


================================================================================
                          HOTKEY REFERENCE
================================================================================

p.py (Configuration GUI):
- F6 (default) - Toggle area selection mode
- F7 (default) - Exit application and save config

a.py (Screenshot Capture):
- F1 - Start/Resume capturing
- F2 - Pause capturing
- F3 - Emergency shutdown

b.py (Live Detection):
- ESC or Q - Exit live detection


================================================================================
                        CONFIGURATION FILES
================================================================================

Config.txt:
-----------
JSON format containing:
{
    "Start": "F4",
    "Stop": "F5",
    "Modify Area": "F6",
    "Exit": "F7",
    "fish_box": {
        "x1": 100,    // Top-left X coordinate
        "y1": 100,    // Top-left Y coordinate
        "x2": 300,    // Bottom-right X coordinate
        "y2": 300     // Bottom-right Y coordinate
    },
    "always_on_top": false
}

data.yaml (generated by organize_dataset.py):
----------------------------------------------
path: [full path to dataset]
train: images/train
val: images/val

names:
  0: Target Line
  1: Fish Bar

nc: 2


================================================================================
                         FUTURE IMPROVEMENTS
================================================================================

Potential enhancements:
- Auto-fishing bot (press key when target line reaches fish bar)
- Multiple fish_box support for multi-monitor setups
- Real-time training data collection during fishing
- Model ensemble (combine multiple models)
- Add more classes (different fish types, special events)
- Web interface for remote monitoring
- Statistics tracking (catch rate, timing analysis)


================================================================================
                            REQUIREMENTS
================================================================================

Python Packages:
- ultralytics  (YOLO model)
- opencv-python  (Computer vision)
- pillow  (Image processing)
- keyboard  (Hotkey detection)
- torch  (PyTorch - deep learning)
- torchvision  (PyTorch vision utilities)
- tkinter  (GUI - usually included with Python)
- numpy  (Numerical operations)

Install all:
pip install ultralytics opencv-python pillow keyboard torch torchvision


================================================================================
                            VERSION HISTORY
================================================================================

v1.0 - Initial Release
- Basic screenshot capture
- YOLO training pipeline
- Live detection
- Configurable fish_box area
- Hotkey support


================================================================================
                              CONTACT
================================================================================

For issues or questions, refer to:
- YOLO Documentation: https://docs.ultralytics.com/
- CVAT Documentation: https://opencv.github.io/cvat/
- PyTorch Documentation: https://pytorch.org/docs/


================================================================================
                            END OF DOCUMENTATION
================================================================================
