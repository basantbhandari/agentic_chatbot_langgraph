from langchain_community.document_loaders import PyMuPDFLoader, TextLoader


def load_documents(file_path):
    if file_path.endswith(".pdf"):
        loader = PyMuPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    return loader.load()

