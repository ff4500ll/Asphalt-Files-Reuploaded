import cv2
from ultralytics import YOLO
import os

# Load the YOLO model
model = YOLO('Shake.pt')

# Print model classes
print("Model classes:")
print(model.names)
print()

# Test images
test_images = ['shake 1.png']

for image_name in test_images:
    print("\n" + "=" * 60)
    print(f"Testing: {image_name}")
    print("=" * 60)
    
    # Check if image exists
    if not os.path.exists(image_name):
        print(f"ERROR: {image_name} not found in current directory!")
        continue

    print(f"Loading {image_name}...")
    img = cv2.imread(image_name)

    if img is None:
        print(f"ERROR: Failed to load {image_name}!")
        continue

    print(f"Image loaded: {img.shape[1]}x{img.shape[0]} pixels")

    # Run detection
    print("Running YOLO detection...")
    results = model.predict(img, conf=0.25, verbose=True)

    # Get the first result
    result = results[0]

    # Draw bounding boxes on the image
    annotated_img = result.plot()

    # Save the result
    output_path = f'output_{os.path.splitext(image_name)[0]}.png'
    cv2.imwrite(output_path, annotated_img)

    print(f"\n✓ Detection complete!")
    print(f"✓ Output saved to: {output_path}")

    # Print detection details
    if len(result.boxes) > 0:
        print(f"\nDetected {len(result.boxes)} object(s):")
        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls[0])
            class_name = result.names[cls_id]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            print(f"  {i+1}. {class_name} (confidence: {confidence:.2f})")
            print(f"     Box: [{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]")
            
            if class_name.lower() == "icon":
                icon_center_x = int((x1 + x2) / 2)
                print(f"     Icon center X: {icon_center_x}")
            elif class_name.lower() == "bar":
                bar_left = int(x1)
                bar_right = int(x2)
                print(f"     Bar left: {bar_left}, right: {bar_right}")
    else:
        print("\nNo objects detected!")

    print(f"\nOpen {output_path} to see the results.")

print("\n" + "=" * 60)
print("All tests complete!")
print("=" * 60)
