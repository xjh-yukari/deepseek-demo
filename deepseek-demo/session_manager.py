from memory_store import clear_memory
from memory_retriever import clear_vector_cache


def start_new_session():
    clear_vector_cache()
    clear_memory()
