import os
import re
import spacy
from langdetect import detect, LangDetectException
from bs4 import BeautifulSoup
import html
import argparse
from tqdm import tqdm

# First download English NLP model using
# python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')

def is_valid_sentence(sentence):
    
    # Skip very short sentences
    if len(sentence) < 30:
        return False
    if len(sentence.split()) < 5:
        return False
    
    # Check if English
    try:
        lang = detect(sentence)
        if lang != 'en':
            return False
    except LangDetectException:
        return False

    # Check for basic sentence structure
    doc = nlp(sentence)
    has_subject = any(tok.dep_ == "nsubj" for tok in doc)
    has_verb = any(tok.pos_ == "VERB" for tok in doc)

    return has_subject and has_verb

def clean_html(text):

    # Use BeautifulSoup to remove HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove all script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # Get text
    text = soup.get_text()
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove serialized PHP/JSON-like metadata strings
    text = re.sub(r'O:\d+:"[^"]+":\d+:{.*?}', '', text, flags=re.DOTALL)
    text = re.sub(r'a:\d+:{.*?}', '', text, flags=re.DOTALL)
    text = re.sub(r's:\d+:"[^"]+";', '', text)
    text = re.sub(r'i:\d+;', '', text)
    text = re.sub(r'b:\d+;', '', text)
    text = re.sub(r'd:\d+;', '', text)
    text = re.sub(r'N;', '', text)
    
    # Remove any remaining HTML-like tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)
    
    # Remove WordPress metadata at the end of articles
    text = re.sub(r'post \d+ .*? _yoast_wpseo_primary_category \d+ _', '', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_article(input_file, output_file=None):

    print(f"Cleaning article: {input_file}")
    
    # Read the article
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        article_text = f.read()
    
    # Clean HTML and other metadata
    cleaned_text = clean_html(article_text)
    
    # Split into sentences
    sentences = [sent.text.strip() for sent in nlp(cleaned_text).sents]
    
    # Filter for valid sentences
    good_sentences = [sent for sent in sentences if is_valid_sentence(sent)]
    
    # Join the good sentences
    final_text = ' '.join(good_sentences)
    
    # Create final_articles directory if it doesn't exist
    os.makedirs('final_articles', exist_ok=True)
    
    # Determine output file path
    if output_file is None:
        base_name = os.path.basename(input_file)
        base_name = os.path.splitext(base_name)[0]
        output_file = os.path.join('final_articles', f"{base_name}_cleaned.txt")
    
    # Save the cleaned article
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"Cleaned article saved to: {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Clean a single article file by removing HTML tags and metadata.')
    parser.add_argument('input_file', help='Path to the input article file')
    parser.add_argument('--output_file', help='Path to save the cleaned article (optional)')
    
    args = parser.parse_args()
    
    clean_article(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
