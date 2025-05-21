# Text-Cleanser
2 Python scripts that use spaCy and Beautiful Soup to divide and cleanse large text files. 

Given a text file that aggregates articles, blog posts, short stories, etc., **separate_articles.py** separates these into individual files (titled Article 1, 2,...) in a user-specified directory. The script also does a basic cleanse of the text file, deleting metadata such as HTML tags, URLs, and PHP/JSON strings. 

But this cleanse is often not thorough enough to delete ALL undesirable metadata. If that's the case, or if you just want to tidy up a single block of text, **cleantext.py** does so effectively, filtering out metadata, invalid sentences, etc.  

These scripts were tested on text files of size 100 MB+, with over 10,000,000 words. 
