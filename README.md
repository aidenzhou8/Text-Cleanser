# Text Cleansing Toolkit

This toolkit provides two Python scripts for processing arbitrary text files with undesirable HTML content and metadata.

## Scripts

### `separate_articles.py`
Takes large text files with multiple articles or content blocks, extracts individual articles, and saves these as separate files.

### `clean_text.py`
Cleans individual text files by deleting HTML tags, metadata, and validating sentence quality.

## Features

- **HTML Cleaning**: Removes HTML tags, scripts, styles, and decodes HTML entities
- **Metadata Removal**: Strips PHP/JSON serialized data, URLs, email addresses, and WordPress metadata
- **Sentence Validation**: Uses NLP to validate sentence structure and English language detection
- **Large File Support**: Processes files in chunks to handle large datasets efficiently

## Usage Guide

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install spacy==3.7.2 langdetect==1.0.9 beautifulsoup4==4.12.2 tqdm==4.66.1
   ```
3. Download the spaCy English language model:
   ```
   python -m spacy download en_core_web_sm
   ```

## Tips and Tricks

To extract and clean multiple articles from a single large file:

```bash
python separate_articles.py path/to/your/input_file.txt
```

Advanced options:
```bash
python separate_articles.py path/to/your/input_file.txt --output_dir output_folder --chunk_size 2097152
```
- `--chunk_size`: Chunk size for processing large files in bytes (default: 1MB)

To deeply clean a single text file:

```bash
python clean_text.py path/to/your/article.txt
```

With fixed output location:
```bash
python clean_text.py path/to/your/article.txt --output_file path/to/output/cleaned_article.txt
```
