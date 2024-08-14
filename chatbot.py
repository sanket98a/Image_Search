from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from app import MultiModel
import os
from langchain_community.vectorstores import FAISS
import time
Window.size=(350,550)



obj=MultiModel()
embeddings=obj.model

if os.path.exists("animals.vdb"):
    # db=FAISS.load_local(folder_path="animals.vdb",embeddings=None)
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
    results = db.similarity_search_by_vector(embedding=search_vector,k=3)

    # Iterate over the returned search results
    image_list=[]
    for res in results:
        # Extract the image path from the result metadata
        image_path = res.metadata['image_path']
        image_list.append(image_path)
        print("Image_Path ::",image_path)
    return image_list

class Command(MDLabel):
    text = StringProperty()
    size_hint_x=NumericProperty()
    halign = StringProperty()
    font_name="Poppins"
    font_size=17

class Response(MDLabel):
    text = StringProperty()
    size_hint_x=NumericProperty()
    halign = StringProperty()
    font_name="Poppins"
    font_size=17

class ResponseImage(Image):
    sources = StringProperty()



class ChatBot(MDApp):

    def change_screen(self,name):
        screen_manager.current=name

    def build(self):
        global screen_manager
        screen_manager=ScreenManager()
        screen_manager.add_widget(Builder.load_file("Main.kv"))
        screen_manager.add_widget(Builder.load_file("Chats.kv"))
        return screen_manager

    def bot_name(self):
        if screen_manager.get_screen("main").bot_name.text != "":
                screen_manager.get_screen("chats").bot_name.text=screen_manager.get_screen("main").bot_name.text
                screen_manager.current="chats"

    def response(self,*args):
        response=""
        if values == "Hello" or values=="hello":
            bot_name1=screen_manager.get_screen("chats").bot_name.text
            response=f"Hello, I Am Your Personal Assistant {bot_name1}" 

        elif values == "How are you?" or values=="how are you?":
             response="I'm doing well. Thanks!"
        
        else:
            start_time=time.time()
            img_list=search(values)
            end_time=time.time()
            inf_time=end_time-start_time
            print("Recommed Image ::",img_list[0])
            screen_manager.get_screen('chats').chat_list.add_widget(ResponseImage(source=img_list[0]))
            screen_manager.get_screen('chats').chat_list.add_widget(ResponseImage(source=img_list[1]))
            screen_manager.get_screen('chats').chat_list.add_widget(ResponseImage(source=img_list[2]))
            screen_manager.get_screen("chats").chat_list.add_widget(Response(text=f" Response Time ::{round(inf_time,3)} sec",size_hint_x=.75))
        # elif values == "Images1":
        #     screen_manager.get_screen('chats').chat_list.add_widget(ResponseImage(source="1.jpg"))
        # else:
        #     response="Sorry, Could you say that again?"

        screen_manager.get_screen("chats").chat_list.add_widget(Response(text=response,size_hint_x=.75))



    def send(self):
        global size,halign,values
        if screen_manager.get_screen("chats").text_input !="":
            values=screen_manager.get_screen("chats").text_input.text
            if len(values) < 6:
                size= .22
                halign= "center"

            elif len(values) < 11:
                size= .32
                halign= "center"

            elif len(values) < 16:
                size= .45
                halign= "center"

            elif len(values) < 21:
                size= .58
                halign= "center"

            elif len(values) < 26:
                size= .71
                halign= "center"
            else:
                size= .71
                halign= "left"

            screen_manager.get_screen("chats").chat_list.add_widget(Command(text=values,size_hint_x=size,halign=halign))
            Clock.schedule_once(self.response,2)
            screen_manager.get_screen("chats").text_input.text=""

if __name__ == "__main__":
    LabelBase.register(name="Poppins",fn_regular="Poppins-Regular.ttf")
    ChatBot().run()