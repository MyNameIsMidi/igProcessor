from PIL import Image, ImageFilter, ImageDraw
import os

def process_images(folder_path, canvas_size=(1080, 1080), blur_amount=10):
    # Create a 'processed' subfolder if it doesn't exist
    processed_folder_path = os.path.join(folder_path, 'processed')
    if not os.path.exists(processed_folder_path):
        os.makedirs(processed_folder_path)
    
    # Ensure the folder path is valid
    if not os.path.isdir(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    # Process each image in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            process_image(image_path, canvas_size, blur_amount)

def process_image(image_path, canvas_size, blur_amount):
    with Image.open(image_path) as img:
        # Determine the orientation and set canvas size for landscape images
        if img.width > img.height:
            canvas_size = (1350, 1080)

        # Create a canvas
        canvas = Image.new('RGB', canvas_size, (255, 255, 255))

        # Resize image for background (object-fit: fill)
        img_bg = resize_image(img, canvas_size, fit_canvas=True)
        img_bg_blurred = img_bg.filter(ImageFilter.GaussianBlur(blur_amount))

        # Paste the blurred background
        canvas.paste(img_bg_blurred, (0, 0))

        # Resize image for foreground (object-fit: contain)
        img_fg = resize_image(img, canvas_size)

        # Calculate position to paste the foreground image (centered)
        fg_x = (canvas_size[0] - img_fg.width) // 2
        fg_y = (canvas_size[1] - img_fg.height) // 2

        # Paste the foreground image
        canvas.paste(img_fg, (fg_x, fg_y), mask=create_mask(img_fg))

        # Determine the file format based on the file extension
        file_format = 'JPEG' if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg') else 'PNG'

        # Modify the save path to include the 'processed' subfolder
        base, filename = os.path.split(image_path)
        save_path = os.path.join(base, 'processed', os.path.splitext(filename)[0] + '.processed.' + file_format.lower())

        if file_format == 'JPEG':
            canvas.save(save_path, format=file_format, quality=95)
        else:
            canvas.save(save_path, format=file_format)
        print(f"Processed image saved to: {save_path}")

def resize_image(image, canvas_size, fit_canvas=False):
    img_ratio = image.width / image.height
    canvas_ratio = canvas_size[0] / canvas_size[1]

    if fit_canvas:
        # Resize image to fill the canvas (background, object-fit: fill)
        if img_ratio > canvas_ratio:
            new_height = canvas_size[1]
            new_width = int(new_height * img_ratio)
        else:
            new_width = canvas_size[0]
            new_height = int(new_width / img_ratio)
    else:
        # Resize image to fit within the canvas (foreground, object-fit: contain)
        if img_ratio > canvas_ratio:
            new_width = canvas_size[0]
            new_height = int(new_width / img_ratio)
        else:
            new_height = canvas_size[1]
            new_width = int(new_height * img_ratio)

    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def create_mask(image):
    # Create a mask to blend the images
    mask = Image.new("L", image.size, 255)
    return mask

def main():
    # Prompt for inputs
    folder_path = input("Enter the path to the image folder: ")

    print("Select canvas size:")
    print("1. 1080x1080")
    print("2. 1350x1080")
    canvas_choice = input("Select size (1 or 2): ")
    canvas_size = (1080, 1080) if canvas_choice == "1" else (1350, 1080)

    blur_amount = int(input("Enter the blur amount (e.g., 10): "))
    
    process_images(folder_path, canvas_size, blur_amount)

if __name__ == "__main__":
    main()