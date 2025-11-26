
import os
import argparse
import zipfile
from pathlib import Path
import tempfile
from PIL import Image

def convert_single_cbz_to_pdf(cbz_path, output_dir):
    """
    Converts a single .cbz file to a .pdf file.

    Args:
        cbz_path (str): The path to the .cbz file.
        output_dir (str): The path to the directory where the .pdf file will be saved.
    """
    cbz_path = Path(cbz_path)
    pdf_filename = cbz_path.stem + '.pdf'
    pdf_path = Path(output_dir) / pdf_filename

    print(f"Processing '{cbz_path.name}'...")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(cbz_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            print(f"  Warning: '{cbz_path.name}' is not a valid zip file. Skipping.")
            return

        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        image_files = []
        for root, _, files in os.walk(temp_dir):
            for f in sorted(files):
                if Path(f).suffix.lower() in image_extensions:
                    image_files.append(Path(root) / f)

        if not image_files:
            print(f"  No images found in '{cbz_path.name}'. Skipping.")
            return

        images = []
        for image_file in image_files:
            try:
                with Image.open(image_file) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img.copy())
            except Exception as e:
                print(f"  Warning: Could not open or convert '{image_file.name}'. Skipping this file. Error: {e}")

        if images:
            images[0].save(
                pdf_path,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=images[1:]
            )
            print(f"  Successfully converted to '{pdf_path.name}'")
        else:
            print(f"  No valid images could be processed in '{cbz_path.name}'.")

def convert_cbz_to_pdfs(input_dir, output_dir):
    """
    Converts all .cbz files in the input directory to individual .pdf files in the output directory.

    Args:
        input_dir (str): The path to the directory containing .cbz files.
        output_dir (str): The path to the directory where .pdf files will be saved.
    """
    if not output_dir:
        output_dir = Path.cwd() / "pdf_output"
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Input directory: {Path(input_dir).resolve()}")
    print(f"Output directory: {Path(output_dir).resolve()}")

    for filename in sorted(os.listdir(input_dir)):
        if filename.lower().endswith('.cbz'):
            cbz_path = Path(input_dir) / filename
            convert_single_cbz_to_pdf(cbz_path, output_dir)


def combine_cbz_to_pdf(input_files, output_file):
    """
    Combines multiple .cbz files into a single .pdf file.

    Args:
        input_files (list): A list of paths to the .cbz files.
        output_file (str): The path to the output .pdf file.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Combining {len(input_files)} .cbz files into '{output_path.name}'...")

    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    all_images = []
    
    files_processed = 0

    for cbz_file in sorted(input_files):
        cbz_path = Path(cbz_file)
        if not cbz_path.is_file() or cbz_path.suffix.lower() != '.cbz':
            print(f"Warning: '{cbz_file}' is not a valid .cbz file. Skipping.")
            continue

        print(f"Processing '{cbz_path.name}' for combination...")
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(cbz_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                image_files = []
                for root, _, files in os.walk(temp_dir):
                    for f in sorted(files):
                        if Path(f).suffix.lower() in image_extensions:
                            image_files.append(Path(root) / f)
                
                for image_file in image_files:
                    try:
                        with Image.open(image_file) as img:
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            all_images.append(img.copy())
                    except Exception as e:
                        print(f"  Warning: Could not open or convert '{image_file.name}'. Skipping. Error: {e}")
            except zipfile.BadZipFile:
                print(f"  Warning: '{cbz_path.name}' is not a valid zip file. Skipping.")
        
        files_processed += 1
        yield files_processed


    if all_images:
        print(f"Saving combined PDF to '{output_path.resolve()}'...")
        all_images[0].save(
            output_path, 
            "PDF", 
            resolution=100.0, 
            save_all=True, 
            append_images=all_images[1:]
        )
        print("  Successfully created combined PDF.")
    else:
        print("No valid images found to create a combined PDF.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert or combine .cbz files to .pdf files.")
    parser.add_argument("input_paths", nargs='+', help="One or more .cbz files to process, or a single directory.")
    parser.add_argument("-o", "--output", help="The output directory for individual PDFs, or the output file name for a combined PDF.", default=None)
    parser.add_argument("--combine", action="store_true", help="Combine multiple .cbz files into a single .pdf file.")

    args = parser.parse_args()

    if args.combine:
        if not args.output:
            parser.error("--output is required when using --combine")
        
        # We need to consume the generator for the combine function to execute
        for _ in combine_cbz_to_pdf(args.input_paths, args.output):
            pass

    else:
        if len(args.input_paths) > 1:
            parser.error("Only a single input directory is allowed when not using --combine.")
        
        input_path = Path(args.input_paths[0])
        if not input_path.is_dir():
            parser.error(f"Input path '{input_path}' is not a directory. To process single files, please use the --combine flag.")
        
        convert_cbz_to_pdfs(input_path, args.output)
