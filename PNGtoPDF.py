from PIL import Image, ImageDraw, ImageFont
import os

def images_to_pdf(image_directory, output_pdf_name):
    # Supported image formats
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    # 1. Gather and sort all image files alphabetically
    image_files = [
        f for f in os.listdir(image_directory) 
        if f.lower().endswith(valid_extensions)
    ]
    image_files.sort()
    
    if not image_files:
        print("No valid images found in the specified directory.")
        return

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # 2. Open images, label them, and convert to RGB
    opened_images = []
    for img_file in image_files:
        img_path = os.path.join(image_directory, img_file)
        try:
            img = Image.open(img_path)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            draw = ImageDraw.Draw(img)

            # ---- LABEL TEXT ----
            label = img_file

            # Position (top-left)
            x, y = 20, 20

            # Optional: background box for readability
            bbox = draw.textbbox((x, y), label, font=font)
            padding = 10
            box = [
                bbox[0] - padding,
                bbox[1] - padding,
                bbox[2] + padding,
                bbox[3] + padding
            ]

            draw.rectangle(box, fill=(0, 0, 0))
            draw.text((x, y), label, fill=(255, 255, 255), font=font)

            opened_images.append(img)

        except Exception as e:
            print(f"Skipping corrupt or unreadable image {img_file}: {e}")

    # 3. Compile and save into a single PDF
    if opened_images:
        first_image = opened_images[0]
        subsequent_images = opened_images[1:]
        
        first_image.save(
            output_pdf_name,
            "PDF",
            save_all=True,
            append_images=subsequent_images
        )
        print(f"Successfully created labeled PDF: {output_pdf_name}")
    else:
        print("No images were successfully processed.")

# Example Usage
if __name__ == "__main__":
    target_folder = "AutoAreaSCALED"
    output_filename = "organized_photos.pdf"
    
    images_to_pdf(target_folder, output_filename)