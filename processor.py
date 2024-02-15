from PIL import Image, ImageFilter, ImageEnhance
import os

def process_images(folder_path, canvas_size=(1080, 1080), blur_amount=10, darken_factor=1):
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
            process_image(image_path, canvas_size, blur_amount, darken_factor)

def process_image(image_path, canvas_size, blur_amount, darken_factor):
    with Image.open(image_path) as img:
        # Check if we should keep the original size
        if canvas_size[0] == -1:
            effective_canvas_size = (img.width, img.height)
        else:
            effective_canvas_size = canvas_size

        # Create a canvas
        canvas = Image.new('RGB', effective_canvas_size, (255, 255, 255))

        # Resize image for background (object-fit: fill)
        img_bg = resize_image(img, effective_canvas_size, fit_canvas=True)
        img_bg_blurred = img_bg.filter(ImageFilter.GaussianBlur(blur_amount))

        # Apply darkening to the blurred background
        img_bg_blurred_darkened = darken_image(img_bg_blurred, darken_factor)

        # Paste the darkened and blurred background
        canvas.paste(img_bg_blurred_darkened, (0, 0))

        # Resize image for foreground (object-fit: contain)
        img_fg = resize_image(img, effective_canvas_size)

        # Calculate position to paste the foreground image (centered)
        fg_x = (effective_canvas_size[0] - img_fg.width) // 2
        fg_y = (effective_canvas_size[1] - img_fg.height) // 2

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

def darken_image(image, factor):
    """Darkens the given image by the specified factor."""
    if factor < 0 or factor > 1:
        raise ValueError("Factor must be between 0 and 1.")

    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

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
    # Prompt for folder path
    folder_path = input("Enter the path to the image folder: ")
    
    # Validate folder path
    if not os.path.isdir(folder_path):
        print(f"The folder '{folder_path}' does not exist or is not a directory.")
        return

    # Prompt for canvas size
    print("Select canvas size:")
    print("1. 1080x1080")
    print("2. 1350x1080")
    print("3. Enter a custom resolution")
    print("4. Original size (No change)")
    canvas_choice = input("Select size (1 - 4): ")
    
    # Validate canvas size selection and handle custom input
    if canvas_choice == "1":
        canvas_size = (1080, 1080)
    elif canvas_choice == "2":
        canvas_size = (1350, 1080)
    elif canvas_choice == "3":
        # Prompt for custom dimensions
        try:
            custom_width = int(input("Enter custom width: "))
            custom_height = int(input("Enter custom height: "))
            if custom_width <= 0 or custom_height <= 0:
                raise ValueError
            canvas_size = (custom_width, custom_height)
        except ValueError:
            print("Invalid custom resolution. Please enter positive integers for width and height.")
            return
    elif canvas_choice == "4":
        canvas_size = (-1, -1)
    else:
        print("Invalid selection for canvas size. Please select 1, 2, 3 or 4.")
        return


    # Prompt for blur amount
    try:
        blur_amount = int(input("Enter the blur amount (e.g., 10): "))
        if blur_amount < 0:
            raise ValueError
    except ValueError:
        print("Invalid blur amount. Please enter a valid, non-negative integer.")
        return


    # Prompt for darkening factor
    try:
        darken_input = input("Enter a darkening factor (0 for black, 1 for original brightness): ")
        darken_factor = float(darken_input)
        if darken_factor < 0 or darken_factor > 1:
            raise ValueError
    except ValueError:
        print("Darkening factor must be a number between 0 and 1.")
        return

    
    process_images(folder_path, canvas_size, blur_amount, darken_factor)

if __name__ == "__main__":
    main()