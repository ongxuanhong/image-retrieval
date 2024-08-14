import os

import chromadb
import numpy as np
import streamlit as st
from PIL import Image
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction


class ChromaDBToolkit:

    def __init__(self, collection_name) -> None:
        # Create a Chroma Client
        self.chroma_client = chromadb.PersistentClient(path="./chromadb/persisted")
        self.embedding_function = OpenCLIPEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def get_single_image_embedding(self, image):
        embedding = self.embedding_function._encode_image(image=np.array(image))
        return embedding

    def search(self, image_path, n_results):
        query_image = Image.open(image_path)
        query_embedding = self.get_single_image_embedding(query_image)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,  # how many results to return
        )
        return results


class StreamlitUI:

    def __init__(self, db_client):
        self.db_client = db_client

    def display_sidebar(self):
        st.sidebar.title("Search Images")
        # Image uploader
        uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
        search_button = st.sidebar.button("Search")
        return uploaded_file, search_button

    def display_search_results(self, search_input):
        # Cached function to get filtered images
        @st.cache_data(ttl=3600)
        def get_filtered_images(search_input):
            image_paths = self.db_client.search(image_path=search_input, n_results=100)
            return image_paths

        # Get the filtered images from the cached function
        images = get_filtered_images(search_input)

        # Create a container for the images
        st.subheader("Search image")
        st.image(search_input)
        image_container = st.container()

        # Create columns for the grid
        image_container.subheader("Search Results")
        cols = image_container.columns(4)

        # Loop through the filtered images and display them in the columns
        for i, id_img in enumerate(images["ids"][0]):
            id_img = int(id_img.split("_")[-1])
            img_path = files_path[id_img]
            cols[i % 4].image(img_path, use_column_width=True)


def get_files_path(path):
    files_path = []
    for label in CLASS_NAME:
        label_path = path + "/" + label
        filenames = os.listdir(label_path)
        for filename in filenames:
            filepath = label_path + "/" + filename
            files_path.append(filepath)
    return files_path


if __name__ == "__main__":
    # get file paths
    ROOT = "data"
    CLASS_NAME = sorted(list(os.listdir(f"{ROOT}/train")))

    # init vector db
    data_path = f"{ROOT}/train"
    files_path = get_files_path(path=data_path)
    db_client = ChromaDBToolkit("Cosine_collection")

    # start streamlit ui
    ui = StreamlitUI(db_client)
    uploaded_file, search_button = ui.display_sidebar()
    if uploaded_file or search_button:
        ui.display_search_results(uploaded_file)
