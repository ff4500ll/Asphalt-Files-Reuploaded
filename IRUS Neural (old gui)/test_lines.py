import os
import numpy as np
from PIL import Image
import cv2

# Create Processed folder if it doesn't exist
os.makedirs('Processed', exist_ok=True)

# Process images 1.png through 4.png
for i in range(1, 5):
    input_file = f"{i}.png"
    step0_file = f"Processed/step0_{i}_blurred.png"
    step1_file = f"Processed/step1_{i}_canny_multichannel.png"
    
    try:
        # Open image
        img = Image.open(input_file)
        img_array = np.array(img)
        
        # Step 0: Apply Gaussian blur
        blurred = cv2.GaussianBlur(img_array, (5, 5), 0)
        Image.fromarray(blurred).save(step0_file)
        print(f"Step 0: {input_file} -> {step0_file}")
        
        # Multi-channel Canny (apply to each RGB channel and combine)
        if len(blurred.shape) == 3:
            canny_r = cv2.Canny(blurred[:,:,0], 5, 30)
            canny_g = cv2.Canny(blurred[:,:,1], 5, 30)
            canny_b = cv2.Canny(blurred[:,:,2], 5, 30)
            canny_multichannel = cv2.bitwise_or(canny_r, cv2.bitwise_or(canny_g, canny_b))
        else:
            # If grayscale, just use regular Canny
            canny_multichannel = cv2.Canny(blurred, 5, 30)
        
        Image.fromarray(canny_multichannel).save(step1_file)
        print(f"Step 1: {step0_file} -> {step1_file}")
        
        # Step 2: Keep only columns that have more white than black
        step2_file = f"Processed/step2_{i}_filtered_columns.png"
        
        height, width = canny_multichannel.shape
        
        # Create output image (start with black)
        filtered_image = np.zeros_like(canny_multichannel)
        
        # Check each column
        for col in range(width):
            column_pixels = canny_multichannel[:, col]
            white_count = np.sum(column_pixels > 0)
            
            # Keep column if at least 50% white
            if white_count >= height * 0.5:
                filtered_image[:, col] = column_pixels
        
        Image.fromarray(filtered_image).save(step2_file)
        print(f"Step 2: {step1_file} -> {step2_file}")
        
        # Step 3: Combine nearby columns (within 5 pixels) into single lines
        step3_file = f"Processed/step3_{i}_combined_lines.png"
        
        # Find columns that have white pixels
        columns_with_white = []
        for col in range(width):
            if np.any(filtered_image[:, col] > 0):
                columns_with_white.append(col)
        
        # Create output image (start with black)
        combined_image = np.zeros_like(filtered_image)
        
        # Group nearby columns (within 5 pixels)
        if len(columns_with_white) > 0:
            used = set()
            for col in columns_with_white:
                if col in used:
                    continue
                
                # Find all columns within 5 pixels
                group = [col]
                for other_col in columns_with_white:
                    if other_col != col and abs(other_col - col) <= 5 and other_col not in used:
                        group.append(other_col)
                
                # Mark all in group as used
                for g in group:
                    used.add(g)
                
                # Calculate center column for this group
                center_col = int(np.mean(group))
                
                # Combine all columns in group to center column (OR operation)
                combined_column = np.zeros(height, dtype=np.uint8)
                for g in group:
                    combined_column = np.bitwise_or(combined_column, filtered_image[:, g])
                
                # Place combined column at center position
                combined_image[:, center_col] = combined_column
        
        Image.fromarray(combined_image).save(step3_file)
        print(f"Step 3: {step2_file} -> {step3_file}")
        
        # Final output: Get X coordinates of leftmost and rightmost lines
        final_columns = []
        for col in range(width):
            if np.any(combined_image[:, col] > 0):
                final_columns.append(col)
        
        if len(final_columns) >= 2:
            leftmost_x = min(final_columns)
            rightmost_x = max(final_columns)
            print(f"Final: Leftmost line X = {leftmost_x}, Rightmost line X = {rightmost_x}")
        elif len(final_columns) == 1:
            print(f"Final: Only one line found at X = {final_columns[0]}")
        else:
            print(f"Final: No lines detected")
        
    except FileNotFoundError:
        print(f"Warning: {input_file} not found, skipping...")
    except Exception as e:
        print(f"Error processing {input_file}: {e}")

print("\nProcessing complete!")
