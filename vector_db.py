import os
import json
import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from constants import (
    VECTOR_DB_PATH,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIM,
    DATA_DIR,
    FEEDBACK_LOG_PATH,
)

os.makedirs(DATA_DIR, exist_ok=True)


@st.cache_resource
def get_embedding_model():
    """SentenceTransformer modelini yükler ve önbelleğe alır."""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def create_vector_db_from_feedback(
    feedback_log_path=FEEDBACK_LOG_PATH, vector_db_path=VECTOR_DB_PATH
):
    pairs = []
    prompt = None
    with open(feedback_log_path, "r") as f:
        for line in f:
            if "PromptForLikedResponse" in line:
                prompt = line.split(": ", 1)[1].strip()
            elif "Feedback: like" in line and prompt is not None:
                response = line.split(": ", 1)[1].strip()
                pairs.append((prompt, response))
                prompt = None
    if not pairs:
        return False
    prompts = [pair[0] for pair in pairs]
    responses = [pair[1] for pair in pairs]
    embedding_model = get_embedding_model()
    prompt_vectors = np.array(embedding_model.encode(prompts)).astype('float32')
    if prompt_vectors.ndim == 1:
        prompt_vectors = prompt_vectors.reshape(1, -1)
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(prompt_vectors)
    faiss.write_index(index, vector_db_path)
    with open(vector_db_path + ".responses.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False)
    return True


# Yardımcı fonksiyon: Vektörleri DataFrame olarak döndür (görselleştirme için)
def get_vector_dataframe(vector_db_path=VECTOR_DB_PATH):
    import pandas as pd
    if not os.path.exists(vector_db_path):
        return None
    index = faiss.read_index(vector_db_path)
    with open(vector_db_path + ".responses.json", "r", encoding="utf-8") as f:
        responses = json.load(f)
    if index.ntotal == 0:
        return None
    xb = np.zeros((index.ntotal, index.d), dtype='float32')
    index.reconstruct_n(0, index.ntotal, xb)
    df = pd.DataFrame(xb, columns=[f"v{i}" for i in range(xb.shape[1])])
    df["Yanıt"] = [str(r) for r in responses]
    return df

def search_cache(query, threshold=0.95, vector_db_path=VECTOR_DB_PATH):
    if not os.path.exists(vector_db_path):
        return None
    embedding_model = get_embedding_model()
    index = faiss.read_index(vector_db_path)
    with open(vector_db_path + ".responses.json", "r", encoding="utf-8") as f:
        responses = json.load(f)
    query_vector = np.array(embedding_model.encode([query])).astype('float32')
    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)
    distances, indices = index.search(query_vector, k=1)
    if distances[0][0] < (1 - threshold):
        return responses[indices[0][0]]
    return None
