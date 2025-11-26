
import os
import argparse
import zipfile
from pathlib import Path
import tempfile
from PIL import Image

def convert_cbz_to_pdf(input_dir, output_dir):
    """
    Converts all .cbz files in the input directory to .pdf files in the output directory.

    Args:
        input_dir (str): The path to the directory containing .cbz files.
        output_dir (str): The path to the directory where .pdf files will be saved.
    """
    # If output directory is not specified, create a 'pdf_output' folder in the current directory
    if not output_dir:
        output_dir = Path.cwd() / "pdf_output"
    
    # Create the output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Input directory: {Path(input_dir).resolve()}")
    print(f"Output directory: {Path(output_dir).resolve()}")

    # Supported image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.cbz'):
            cbz_path = Path(input_dir) / filename
            pdf_filename = Path(filename).stem + '.pdf'
            pdf_path = Path(output_dir) / pdf_filename

            print(f"Processing '{filename}'...")

            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract the CBZ file
                with zipfile.ZipFile(cbz_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                image_files = []
                # Walk through the extracted files and find images
                for root, _, files in os.walk(temp_dir):
                    for f in files:
                        if Path(f).suffix.lower() in image_extensions:
                            image_files.append(Path(root) / f)
                
                # Sort files alphabetically to maintain page order
                image_files.sort()

                if not image_files:
                    print(f"  No images found in '{filename}'. Skipping.")
                    continue

                images = []
                for image_file in image_files:
                    try:
                        img = Image.open(image_file)
                        # Convert to RGB to avoid issues with different image modes (like RGBA or P)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        images.append(img)
                    except Exception as e:
                        print(f"  Warning: Could not open or convert '{image_file.name}'. Skipping this file. Error: {e}")

                if images:
                    # Save the first image and append the rest
                    images[0].save(
                        pdf_path, 
                        "PDF", 
                        resolution=100.0, 
                        save_all=True, 
                        append_images=images[1:]
                    )
                    print(f"  Successfully converted to '{pdf_path.name}'")
                else:
                    print(f"  No valid images could be processed in '{filename}'.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert .cbz files to .pdf files.")
    parser.add_argument("input_dir", help="The directory containing .cbz files to convert.")
    parser.add_argument("-o", "--output_dir", help="The directory to save the converted .pdf files. (Optional)", default=None)

    args = parser.parse_args()

    input_path = Path(args.input_dir)

    if not input_path.is_dir():
        print(f"Error: Input directory '{args.input_dir}' not found.")
    else:
        convert_cbz_to_pdf(args.input_dir, args.output_dir)
