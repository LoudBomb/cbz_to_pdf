# CBZ to PDF Converter

This script converts `.cbz` (comic book archive) files into `.pdf` files. It can convert each `.cbz` file into a separate `.pdf` or combine multiple `.cbz` files into a single `.pdf` file.

## Features

-   Convert all `.cbz` files in a directory to individual `.pdf` files.
-   Combine multiple `.cbz` files into a single `.pdf` file.
-   Specify input and output directories/files.
-   Command-line driven with no interactive prompts.

## Prerequisites

-   Python 3.x
-   Pillow library (PIL)

You can install the required library using pip:

```bash
pip install Pillow
```

## Usage

The script has two main modes of operation: converting a directory of `.cbz` files to individual `.pdf` files, and combining multiple `.cbz` files into a single `.pdf` file.

### Converting a Directory of CBZ Files

To convert all `.cbz` files in a directory to individual `.pdf` files, provide the directory path as the `input_paths` argument.

```bash
python cbz_to_pdf.py <directory_path>
```

By default, the output files will be saved in a `pdf_output` folder in the current directory. You can specify a different output directory with the `-o` or `--output` flag.

```bash
python cbz_to_pdf.py <directory_path> -o <output_directory_path>
```

**Example:**

```bash
# Convert all .cbz files in the current directory
python cbz_to_pdf.py .

# Convert all .cbz files in the 'my_comics' directory and save them in 'my_pdfs'
python cbz_to_pdf.py my_comics -o my_pdfs
```

### Combining Multiple CBZ Files

To combine multiple `.cbz` files into a single `.pdf` file, use the `--combine` flag. You must also provide the list of input `.cbz` files and specify the output file name using the `-o` or `--output` flag.

```bash
python cbz_to_pdf.py <file1.cbz> <file2.cbz> ... --combine -o <output.pdf>
```

**Example:**

```bash
# Combine two .cbz files into a single .pdf
python cbz_to_pdf.py "Chapter 1.cbz" "Chapter 2.cbz" --combine -o "Combined Chapters.pdf"
```