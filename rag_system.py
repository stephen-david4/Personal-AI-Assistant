from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq
import streamlit as st


class DocumentAssistant:

    def __init__(self, groq_api_key):
        self.embeddings = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.vectorstore = None
        self.doc_loaded  = False
        self.client      = Groq(api_key=groq_api_key)

    def load_pdf(self, pdf_path, filename):
        print(f"Loading {filename}...")

        loader = PyPDFLoader(pdf_path)
        pages  = loader.load()

        for page in pages:
            page.metadata['filename'] = filename

        chunks = self.splitter.split_documents(pages)
        print(f"Created {len(chunks)} chunks from {filename}")

        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory='./db'
            )
            print("New database created!")
        else:
            self.vectorstore.add_documents(chunks)
            print(f"Added to existing database!")

        self.vectorstore.persist()
        self.doc_loaded = True
        print(f"Document ready!")

    def ask(self, question):
        if not self.doc_loaded:
            return "Please upload a document first."

        results   = self.vectorstore.similarity_search(question, k=3)
        context   = ""
        citations = []

        for doc in results:
            page     = doc.metadata.get('page', 0) + 1
            filename = doc.metadata.get('filename', 'document')
            context += f"[{filename} - Page {page}]: {doc.page_content}\n"
            citations.append(f"{filename} Page {page}")

        prompt = f"""Answer using ONLY the document content below.
If answer not found say: Not found in document.
Always mention filename and page number.

Document:
{context}

Question: {question}

Answer:"""

        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        answer  = response.choices[0].message.content
        sources = ', '.join(set(citations))
        return f"{answer}\n\nSources: {sources}"
