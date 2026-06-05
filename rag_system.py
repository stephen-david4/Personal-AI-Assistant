from langchain_community.document_loaders import PyPDFLoader  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import ollama


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

        self.vectorstore.persist()
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

    
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{'role': 'user', 'content': prompt}],
            options={"temperature": 0.3}
        )

        answer  = response['message']['content']
        sources = ', '.join(set(citations))
        return f'{answer}\n\nSources: {sources}'
