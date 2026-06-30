import os
import re
from typing import List, Dict, Tuple
from pathlib import Path
from PyPDF2 import PdfReader
from nltk.tokenize import sent_tokenize
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import KnowledgeBaseConfig


class DocumentLoader:
    def __init__(self, pdf_dir: str = None):
        self.pdf_dir = pdf_dir or KnowledgeBaseConfig.PDF_DIR
        self.chunks: List[Dict] = []

    def load_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text.strip()

    def load_all_pdfs(self) -> List[str]:
        texts = []
        for filename in os.listdir(self.pdf_dir):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(self.pdf_dir, filename)
                text = self.load_pdf(file_path)
                if text:
                    texts.append(text)
        return texts

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'-\n', '', text)
        text = text.strip()
        return text

    def split_by_section(self, text: str) -> List[str]:
        sections = re.split(r'(第[一二三四五六七八九十]+章|第\d+章|^\d+\.\d+\s+.+?$)', text, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]
        return sections

    def split_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        text = self.clean_text(text)
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length <= chunk_size:
                current_chunk += sentence + " "
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                overlap = ""
                if len(chunks) > 0 and chunk_overlap > 0:
                    overlap = " ".join(chunks[-1].split()[-chunk_overlap // 10:])
                current_chunk = overlap + sentence + " "
                current_length = len(current_chunk)

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def process_pdf_file(self, file_path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
        text = self.load_pdf(file_path)
        text = self.clean_text(text)
        chunks = self.split_text(text, chunk_size, chunk_overlap)
        
        results = []
        for idx, chunk in enumerate(chunks):
            results.append({
                "file_name": os.path.basename(file_path),
                "chunk_id": f"{os.path.basename(file_path)}_{idx}",
                "content": chunk,
                "chunk_index": idx,
                "total_chunks": len(chunks)
            })
        return results

    def process_all_pdfs(self, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
        all_chunks = []
        for filename in os.listdir(self.pdf_dir):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(self.pdf_dir, filename)
                chunks = self.process_pdf_file(file_path, chunk_size, chunk_overlap)
                all_chunks.extend(chunks)
        self.chunks = all_chunks
        return all_chunks

    def get_chunks(self) -> List[Dict]:
        return self.chunks
