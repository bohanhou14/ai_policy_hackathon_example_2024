import requests
import re
from io import BytesIO
from tqdm import tqdm
from pypdf import PdfReader
from bs4 import BeautifulSoup
from datetime import datetime
from data_utils import write_jsonl
import json
import argparse

def date_parser(date_string):
    cleaned_date_str = date_string[2:-1]
    parsed_date = datetime.strptime(cleaned_date_str, '%Y%m%d%H%M%S')
    return parsed_date

def extract_url(markdown_string):
    # Use a regex to find the URL inside parentheses
    match = re.search(r'\((https?://[^\)]+)\)', markdown_string)
    if match:
        return match.group(1)
    else:
        return None
    
def extract_abstract_to_intro(text):
    # Convert the text to lowercase to handle case variations of "abstract" and "introduction"
    lower_text = text.lower()

    # Find the abstract section using "abstract"
    abstract_start = lower_text.split("abstract", 1)[-1]  # Get the part after "abstract"

    # Use a regex pattern to match different forms of "introduction"
    intro_pattern = re.compile(r'\b\d{0,2}\.?\s*i\s*n\s*t\s*r\s*o\s*d\s*u\s*c\s*t\s*i\s*o\s*n\b')

    # Search for the introduction pattern
    match = intro_pattern.search(abstract_start)

    if match:
        # Get the part before "introduction" section
        content = abstract_start[:match.start()]
        return content.strip()
    else:
        return None  # Return None if no "introduction" section is found

def get_papers(output_path):
    r = requests.get('https://raw.githubusercontent.com/hyp1231/awesome-llm-powered-agent/main/README.md')
    lines = r.text.split("\n")
    links = []
    for line in lines:
        if line.find("http") != -1:
            links.append(extract_url(line))

    values = []
    for link in tqdm(links, desc="Crawling papers"):
        if link.find("arxiv") != -1:
            if link.find("pdf") != -1:
                paper = requests.get(link)
                pdf_data = BytesIO(paper.content)

                # Instantiate PdfReader using the raw content
                try:
                    reader = PdfReader(pdf_data)
                    page = reader.pages[0]
                    # extracting text from page
                    text = page.extract_text()
                    lowered_text = text.lower()
                    text = extract_abstract_to_intro(lowered_text)
                    value = {
                        "date" : reader.metadata.creation_date.date(),
                        "abstract": text
                    }
                    values.append(value)
                    # f.write(f'[{reader.metadata.creation_date.date()}] {text}')
                    # f.write("\n")
                    # f.write("\n")
                except Exception as error:
                    # handle the exception
                    print("An exception occurred:", error, link) 
            else:
                paper = requests.get(link)
                soup = BeautifulSoup(paper.text, 'html.parser')
                abstract = soup.find("meta", property="og:description")
                meta_tag = soup.find('meta', attrs={'name': 'citation_date'})
                value = {
                        "date" : datetime.strptime(meta_tag["content"], "%Y/%m/%d").date(),
                        "abstract": abstract["content"]
                    }
                values.append(value)
                # f.write(f'[{datetime.strptime(meta_tag["content"], "%Y/%m/%d").date()}] {abstract["content"]}')
                # f.write("\n")
                # f.write("\n")

    write_jsonl(output_path, values)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Grab papers from awesome-llm-powered-agent')
    parser.add_argument('--output', type=str, default="data/data.jsonl", help='output file')
    args = parser.parse_args()
    get_papers(args.output)