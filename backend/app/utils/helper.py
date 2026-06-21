from pathlib import Path
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)


def load_documents(file_path: str):
    path = Path(file_path)
    suffix = path.suffix.lower()
    loader_map = {
        ".pdf": PyMuPDFLoader,
        ".md": UnstructuredMarkdownLoader,
        ".txt": TextLoader,
    }
    loader_class = loader_map.get(suffix)
    loader = loader_class(str(path))
    return loader.load()


def safe_retrieve(retriever, query: str):
    try:
        return retriever.invoke(query)
    except ValueError as e:
        if "Collection not found" in str(e):
            return []
        raise e
    except Exception as e:
        raise e
