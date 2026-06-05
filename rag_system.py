from langchain_community.document_loaders import PyPDFLoader  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from groq import Groq
import streamlit as st


class documentAssistant:

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.splitter   = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.vectorstore = None
        self.doc_loaded  = False

    def load_pdf(self, pdf_path, filename):
        print(f'Loading {filename}....')
        loader = PyPDFLoader(pdf_path)
        pages  = loader.load()

        for page in pages:
            page.metadata['filename'] = filename

        chunks = self.splitter.split_documents(pages)
        print(f'Created {len(chunks)} chunks')

        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory='db',
        )

        
        self.doc_loaded = True
        print('Document ready!')

    def ask(self, question):
        if not self.doc_loaded:
            return "Please load a document first."

        results   = self.vectorstore.similarity_search(question, k=3)
        context   = ""
        citations = []

        for doc in results:
            page = doc.metadata.get('page', 0) + 1
            context += f'[page {page}]: {doc.page_content}\n'
            citations.append(f'page {page}')

        prompt = f"""Answer using ONLY the document content below.
If the answer is not found, say "Not in document."
Always cite the page number.

Document:
{context}

Question: {question}
Answer:"""

    
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
               {
                   "role": "user",
                   "content": prompt
                   }
                ],
           temperature=0.3
        )


        answer = response.choices[0].message.content
        sources = ', '.join(set(citations))
        return f'{answer}\n\nSources: {sources}'
