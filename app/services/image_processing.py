import cv2
import numpy as np
import os

def detect_microplastics(image_path):
    """
    Detects microplastics in an image, extracts their features, and annotates the image.

    Args:
        image_path (str): The path to the image file.

    Returns:
        tuple: A tuple containing:
            - list: A list of dictionaries, where each dictionary represents a
                    detection and contains 'x', 'y', 'size', 'shape', and 'color'.
            - str: The path to the output image with detections drawn on it.
    """
    if not os.path.exists(image_path):
        print(f"Image not found at {image_path}")
        return [], None

    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print(f"Could not read image from {image_path}")
        return [], None

    output_image = image.copy()

    # Convert image to HSV color space for better color thresholding
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define a range for bright colors (like in the sample image)
    # This might need adjustment for different lighting conditions
    lower_bright = np.array([0, 0, 150])
    upper_bright = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_bright, upper_bright)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    for contour in contours:
        # Filter out small contours that are likely noise
        if cv2.contourArea(contour) < 10:
            continue

        # --- Feature Extraction ---

        # 1. Location (centroid)
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # 2. Size (area)
        size = cv2.contourArea(contour)

        # 3. Shape classification
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * (size / (perimeter * perimeter))
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h

        shape = "fragment"
        if circularity > 0.8:
            shape = "bead"
        elif aspect_ratio > 3 or aspect_ratio < 0.3:
            shape = "fiber"

        # 4. Color
        mask_i = np.zeros(image.shape[:2], dtype="uint8")
        cv2.drawContours(mask_i, [contour], -1, 255, -1)
        mean_color_bgr = cv2.mean(image, mask=mask_i)
        # Convert BGR to a hex string for easier display
        mean_color_hex = '#%02x%02x%02x' % (int(mean_color_bgr[2]), int(mean_color_bgr[1]), int(mean_color_bgr[0]))


        detections.append({
            'x': cx,
            'y': cy,
            'size': size,
            'shape': shape,
            'color': mean_color_hex
        })

        # --- Annotation ---
        cv2.drawContours(output_image, [contour], -1, (0, 255, 0), 2)
        cv2.putText(output_image, shape, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


    # Save the output image
    directory, filename = os.path.split(image_path)
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_processed{ext}"
    output_path = os.path.join(directory, output_filename)
    cv2.imwrite(output_path, output_image)

    return detections, output_path
