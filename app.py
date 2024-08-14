import os
import json
import base64
from langchain_community.vectorstores import FAISS
from io import BytesIO
from PIL import Image
import time
from transformers import AutoModel



class MultiModel():
    
    def __init__(self):
        pass
    
    def jinaai_embedding(self):
        # Initialize the model
        model = AutoModel.from_pretrained('jinaai/jina-clip-v1', trust_remote_code=True)
        return model
    
    # This function takes a file path as input and returns a vector representation of the content
    def get_vector_from_file(self,file_path=None,input_text=None):
        model=self.jinaai_embedding()
        # If input_text is provided, add it to the request body with the key "inputText"
        if input_text:
            embedding = model.encode_text(input_text)

        # If input_image_base64 is provided, add it to the request body with the key "inputImage"
        if file_path:
            embedding = model.encode_image(file_path)

        # Returns the generated vector
        return embedding
    
    def check_size_image(self,file_path):
          """
          This function checks if an image exceeds a predefined maximum size and resizes it if necessary.

          Args:
              file_path (str): The path to the image file.

          Returns:
              None
          """

          # Maximum allowed image size (replace with your desired limit)
          max_size = 2048

          # Open the image using Pillow library (assuming it's already imported)
          try:
            image = Image.open(file_path)
          except FileNotFoundError:
              print(f"Error: File not found - {file_path}")
              return

          # Get the image width and height in pixels
          width, height = image.size

          # Check if either width or height exceeds the maximum size
          if width > max_size or height > max_size:
              print(f"Image '{file_path}' exceeds maximum size: width: {width}, height: {height} px")

              # Calculate the difference between current size and maximum size for both dimensions
              dif_width = width - max_size
              dif_height = height - max_size

              # Determine which dimension needs the most significant resize based on difference
              if dif_width > dif_height:
                # Calculate the scaling factor based on the width exceeding the limit most
                scale_factor = 1 - (dif_width / width)
              else:
                # Calculate the scaling factor based on the height exceeding the limit most
                scale_factor = 1 - (dif_height / height)

              # Calculate new width and height based on the scaling factor
              new_width = int(width * scale_factor)
              new_height = int(height * scale_factor)

              print(f"Resized image dimensions: width: {new_width}, height: {new_height} px")

              # Resize the image using the calculated dimensions
              new_image = image.resize((new_width, new_height))

              # Save the resized image over the original file (be cautious about this)
              new_image.save(file_path)

          # No resizing needed, so we don't modify the image file
          return#i
        
    def get_image_vectors_from_directory(self,path_name):
          """
          This function extracts image paths and their corresponding vectors from a directory and its subdirectories.

          Args:
              path_name (str): The path to the directory containing images.

          Returns:
              list: A list of tuples where each tuple contains the image path and its vector representation.
          """

          items = []  # List to store tuples of (image_path, vector)

          # Get a list of filenames in the given directory
          sub_1 = os.listdir(path_name)

          # Loop through each filename in the directory
          for n in sub_1:
            # Check if the filename ends with '.jpg' (assuming JPG images)
            if n.endswith('.jpg'):
              # Construct the full path for the image file
              file_path = os.path.join(path_name, n)

              # Call the check_size_image function to potentially resize the image
              self.check_size_image(file_path)

              # Get the vector representation of the image using get_vector_from_file
              emd_start=time.time()
              vector = self.get_vector_from_file(file_path)
              emd_end=time.time()
              emd_time=emd_end-emd_start
              # Append a tuple containing the image path and vector to the items list
              items.append((file_path,emd_time,vector))
            else:
              # If the file is not a JPG, check for JPGs within subdirectories
              sub_2_path = os.path.join(path_name, n)  # Subdirectory path
              for n_2 in os.listdir(sub_2_path):
                if n_2.endswith('.jpg'):
                  # Construct the full path for the image file within the subdirectory
                  file_path = os.path.join(sub_2_path, n_2)

                  # Call the check_size_image function to potentially resize the image
                  self.check_size_image(file_path)

                  # Get the vector representation of the image using get_vector_from_file
                  emd_start=time.time()
                  vector = self.get_vector_from_file(file_path)
                  emd_end=time.time()
                  emd_time=emd_end-emd_start
                  # Append a tuple containing the image path and vector to the items list
                  items.append((file_path,emd_time, vector))
                else:
                  # Print a message if a file is not a JPG within the subdirectory
                  print(f"Not a JPG file: {n_2}")

          # Return the list of tuples containing image paths and their corresponding vectors
          return items
        
        
    def create_vector_db(self,path_name):
      """
      This function creates a vector database from image files in a directory.

      Args:
          path_name (str): The path to the directory containing images.

      Returns:
          FAISS index object: The created vector database using FAISS.
      """

      # Get a list of (image_path, vector) tuples from the directory
      image_vectors = self.get_image_vectors_from_directory(path_name)

      # Extract text embeddings (assumed to be empty strings) and image paths
      text_embeddings = [("", item[2]) for item in image_vectors]  # Empty string, vector
      metadatas = [{"image_path": item[0]} for item in image_vectors]
      emd_time_list = [item[1] for item in image_vectors]
      print("+++++++++++++++++++++++++++++++++++++++++")
      print("Embedding Time ::",emd_time_list)
      print("+++++++++++++++++++++++++++++++++++++++++")
      # Create a FAISS index using the extracted text embeddings (might be empty)
      # and image paths as metadata
      db = FAISS.from_embeddings(
          text_embeddings=text_embeddings,
          embedding=None,  # Not explicitly setting embedding (might depend on image_vectors)
          metadatas=metadatas
      )

      # Print information about the created database
      print(f"Vector Database: {db.index.ntotal} docs")
      print("+++++++++++++++++++++++++++++++++++++++++")
      # Return the created FAISS index object (database)
      return db