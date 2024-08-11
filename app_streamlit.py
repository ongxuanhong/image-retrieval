import os
import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
import numpy as np
from PIL import Image


class ChromaDBToolkit:

    def __init__(self, collection_name) -> None:
        # Create a Chroma Client
        self.chroma_client = chromadb.Client()
        self.embedding_function = OpenCLIPEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def get_single_image_embedding(self, image):
        embedding = self.embedding_function._encode_image(image=np.array(image))
        return embedding

    def add_embedding(self, files_path):
        ids = []
        embeddings = []
        for id_filepath, filepath in enumerate(files_path):
            ids.append(f"id_{id_filepath}")
            image = Image.open(filepath)
            embedding = self.get_single_image_embedding(image=image)
            embeddings.append(embedding)
        self.collection.add(embeddings=embeddings, ids=ids)

    def search(self, image_path, n_results):
        query_image = Image.open(image_path)
        query_embedding = self.get_single_image_embedding(query_image)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,  # how many results to return
        )
        return results

    def indexing(self, files_path):
        # Create a collection
        self.add_embedding(files_path=files_path)


class StreamlitUI:

    def __init__(self, db_client):
        self.db_client = db_client

    def display_sidebar(self):
        st.sidebar.title("Search Images")
        search_input = st.sidebar.text_input(
            "What would you like to see? (e.g., begin_123)"
        )
        search_button = st.sidebar.button("Search")
        return search_input, search_button

    def display_search_results(self, search_input):
        st.header("Search Results")

        # Cached function to get filtered images
        @st.cache_data(ttl=3600)
        def get_filtered_images(search_input):
            image_paths = self.db_client.search(image_path=search_input, n_results=5)
            return image_paths

        # Get the filtered images from the cached function
        images = get_filtered_images(search_input)

        # Create a container for the images
        image_container = st.container()

        # Create columns for the grid
        cols = image_container.columns(4)

        # Loop through the filtered images and display them in the columns
        for i, image_url in enumerate(images):
            # Construct the URL for the image in S3
            print(image_url)
            cols[i % 4].image(image_url, use_column_width=True)


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
    db_client.indexing(files_path=files_path)

    # start streamlit ui
    ui = StreamlitUI(db_client)
    search_input, search_button = ui.display_sidebar()
    if search_input or search_button:
        ui.display_search_results(search_input)
