from app import MultiModel
import os
from langchain_community.vectorstores import FAISS
import time


obj=MultiModel()
embeddings=obj.model

if os.path.exists("animals.vdb"):
    db=FAISS.load_local("animals.vdb",embeddings)
else:
    db=obj.create_vector_db("Images")
    # Define the filename for the vector database
    db_file = "animals.vdb"

    # Save the created vector database (FAISS index object) to a local file
    db.save_local(db_file)

    # Print a confirmation message indicating the filename where the database is saved
    print(f"Vector database was saved in {db_file}")

def search(query):
    # Get a multimodal vector representation of the query text using get_multimodal_vector
    search_vector = obj.get_vector_from_file(input_text=query)

    # Perform a similarity search in the vector database using the query vector
    results = db.similarity_search_by_vector(search_vector,k=3)

    # Iterate over the returned search results
    print("-----------------------------------------------")
    image_list=[]
    for res in results:
        print(res)
        # Extract the image path from the result metadata
        image_path = res.metadata['image_path']
        image_list.append(image_path)
        print("Image_Path ::",image_path)
    return image_list



if __name__ == '__main__':
    while True:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        query=input("Input text ::")
        if query:
            start_time=time.time()
            img_list=search(query)
            end_time=time.time()
            inf_time=end_time-start_time
            print("-----------------------------------------------")
            print(f" Response Time ::{round(inf_time,3)} sec")
        else:
            break