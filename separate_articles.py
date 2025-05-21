import os
import re
import spacy
from langdetect import detect, LangDetectException
from bs4 import BeautifulSoup
import html
import argparse
from tqdm import tqdm

# Load English NLP model
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
    
    # Remove extra spaces again
    text = re.sub(r'\s+', '', text).strip()
    
    return text

def clean_and_split_articles(file_path, chunk_size=1024*1024):

    # Process file in chunks to avoid memory issues
    articles = []
    current_article = []
    buffer = ""
    
    # Usual article markers
    article_markers = [
        r'<item>', r'</item>',
        r'<story>', r'</story>',
        r'<article>', r'</article>',
        r'<title>', r'</title>',
        r'<content:encoded>', r'</content:encoded>',
        r'<wp:post_content>', r'</wp:post_content>',
        r'<description>', r'</description>',
        r'<excerpt:encoded>', r'</excerpt:encoded>'
    ]
    
    # Create a regex pattern for article markers
    marker_pattern = '|'.join(article_markers)
    
    print(f"Processing file: {file_path}")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        # Process the file in chunks
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
                
            # Add chunk to buffer
            buffer += chunk
            
            # Look for article boundaries
            if re.search(marker_pattern, buffer):
                # Split by article markers
                potential_articles = re.split(marker_pattern, buffer)
                
                # Process all but the last potential article (which might be incomplete)
                for i in range(len(potential_articles) - 1):
                    article_text = potential_articles[i].strip()
                    if article_text:
                        # Clean HTML
                        cleaned_text = clean_html(article_text)
                        
                        # Split into sentences
                        sentences = [sent.text.strip() for sent in nlp(cleaned_text).sents]
                        
                        # Filter for valid sentences
                        good_sentences = [sent for sent in sentences if is_valid_sentence(sent)]
                        
                        if len(good_sentences) >= 3:
                            # Assume 3 good sentences minimum to treat it as an article
                            articles.append(' '.join(good_sentences))
                
                # Keep the last potential article in the buffer
                buffer = potential_articles[-1]
    
    # Process any remaining text in the buffer
    if buffer.strip():
        cleaned_text = clean_html(buffer)
        sentences = [sent.text.strip() for sent in nlp(cleaned_text).sents]
        good_sentences = [sent for sent in sentences if is_valid_sentence(sent)]
        
        if len(good_sentences) >= 3:
            articles.append(' '.join(good_sentences))
    
    return articles

def save_articles(articles, output_dir):

    # Save articles to individual files with proper naming
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Saving {len(articles)} articles to '{output_dir}'...")
    for idx, article in enumerate(tqdm(articles), start=1):
        filename = os.path.join(output_dir, f'Article {idx}.txt')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(article)

def main():
    parser = argparse.ArgumentParser(description='Clean and split newspaper articles from a text file.')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('--output_dir', default='cleaned_articles', help='Directory to save the cleaned articles')
    parser.add_argument('--chunk_size', type=int, default=1024*1024, help='Chunk size for processing large files (in bytes)')
    
    args = parser.parse_args()
    
    articles = clean_and_split_articles(args.input_file, args.chunk_size)
    save_articles(articles, args.output_dir)
    
    print(f"Successfully saved {len(articles)} high-quality articles to '{args.output_dir}'.")

if __name__ == "__main__":
    main()
