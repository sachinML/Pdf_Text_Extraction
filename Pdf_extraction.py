import pdfplumber
import json
import nltk
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

class PdfExtractor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.data = []

    def stopw(self, s):
        texts = []
        for line in s:
            words = line.split()
            filtered_words = [word for word in words if word.lower() not in stop_words]
            filtered_text = ' '.join(filtered_words)
            texts.append(filtered_text)

        return texts

    def chunks(self, t, n):
        chunked_text = []
        for i in range(0, len(t), n):
            chunked_text.append("<NL>".join(t[i:i + n]))

        return chunked_text

    def extract_data(self):
        with pdfplumber.open(self.input_path) as pdf_file:
            for page_num in range(len(pdf_file.pages)):
                try:
                    page = pdf_file.pages[page_num]
                    text = page.extract_text()
                    tables = page.extract_tables()
                    page = {'page no.': page_num + 1, 'content': []}
                    for table_num, table in enumerate(tables):
                        page['content'].append(table)
                    if page['content']:
                        page['content'].append(text)
                        page['content'] = ''.join([elem for elem in page['content'] if isinstance(elem, str)])
                    else:
                        page['content'] = text
                    modified_text = page['content'].split('\n')
                    
                    # removing stopwords
                    stopwords_removed_text = self.stopw(modified_text)
                    
                    # making chunks with n lines
                    final_text = self.chunks(stopwords_removed_text, n)

                    page['content'] = final_text

                    self.data.append(page)

                except Exception as e:
                    print("Error extracting data from page:", e)

    def write_to_json(self):
        with open(self.output_path, "w", encoding="utf8") as output_file:
            json.dump(self.data, output_file, indent=4)

input_path = ''
output_path = ''

pdf_extractor = PdfExtractor(input_path, output_path)
pdf_extractor.extract_data()
pdf_extractor.write_to_json()
