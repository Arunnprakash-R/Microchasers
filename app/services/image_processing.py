import cv2
import numpy as np
import os

def detect_microplastics(image_path):
    """
    Placeholder function to detect microplastics in an image.
    This function uses a simple circle detection method as a placeholder.
    A real implementation would require a more sophisticated machine learning model.

    Args:
        image_path (str): The path to the image file.

    Returns:
        tuple: A tuple containing:
            - list: A list of dictionaries, where each dictionary represents a
                    detection and contains 'x', 'y', and 'confidence'.
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
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Add a blur to reduce noise
    gray = cv2.medianBlur(gray, 5)

    # Use Hough Circle Transform to detect circles as a placeholder for particles
    # Adjust param2 (accumulator threshold) to be less strict
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=10,
                               param1=50, param2=10, minRadius=5, maxRadius=40)

    detections = []
    if circles is not None:
        print(f"Found {len(circles[0])} circles.")
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Draw the circle in the output image
            cv2.circle(output_image, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output_image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            # Add detection to the list
            detections.append({
                'x': int(x),
                'y': int(y),
                'confidence': float(np.random.uniform(0.7, 0.99)) # Assign a random confidence
            })

    # Save the output image
    directory, filename = os.path.split(image_path)
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_processed{ext}"
    output_path = os.path.join(directory, output_filename)
    cv2.imwrite(output_path, output_image)

    return detections, output_path
