from calendar import c
import re
from turtle import end_fill, update
import customtkinter as ctk
from customtkinter import *
import google.generativeai as genai
from PIL import Image
import os
import threading
from tkinter import Text, Button
from sympy import content, expand, rad
from torch import fill
import json
import datetime

# from tests.test_metrics import ImageTextMetrics
# from tests.feedback_aggregator import FeedbackAggregator




def setup_feedback_section(root,unconditional_caption, conditional_caption,prompt_entered, generated_image_path,button_values):
    end_frame = ctk.CTkFrame(root, corner_radius=15, height=100) 
    end_frame.pack(pady=5, padx=50)


    # Create the feedback label and entry box
    feedback_label = ctk.CTkLabel(end_frame, text="Feedback:",width=15, text_font=("default_theme", 16))
    feedback_label.pack(pady=5,  side='left', padx=(5,0),anchor ='w')
    
    feedback_entry = ctk.CTkTextbox(end_frame, height=50, width=300)
    feedback_entry.pack(pady=(5), side='left', padx=(5,5),anchor ='w')


    # Rating scale
    rating_label = ctk.CTkLabel(end_frame, text="Rate:", text_font=("default_theme", 16), width=10)
    rating_label.pack(pady=5, side='left', padx=(5,0), anchor='w')
    
    rate_value={1 : "Very Bad", 2 : "Bad", 3: "Neutral", 4:"Good", 5:"Excellent" }
    rating_value = ctk.StringVar(value="3")  # Default rating

    def update_rating_value(event):
        selected = rating_scale.get() 
        rating_value.set(selected.split(":")[0])

    rating_scale = ctk.CTkComboBox(end_frame, values=[f"{key}: {value}" for key, value in rate_value.items()],variable=rating_value,width=7)
    rating_scale.pack(pady=(5), side='left', padx=(5,5), anchor='w')

    
    # Define the function to handle feedback submission
    def submit_feedback():
        feedback_text = feedback_entry.textbox.get("1.0", "end").strip()
        feedback_data = {
            "prompt": prompt_entered,
            "image_path": generated_image_path,
            "conditional_caption": conditional_caption,
            "unconditional_caption": unconditional_caption,
            "text_generation_parameters": button_values,
            "generated_text": generated_text,
            "feedback": feedback_text,
            "rating": int(rating_value.get()),
            "timestamp": datetime.datetime.now().isoformat()
            # generation time can be added later on 
        }
    
    
        store_feedback(feedback_data)
        feedback_entry.textbox.delete("1.0", "end")  # Clear the text box after submitting

    # Add the submit button for feedback
    feedback_button = ctk.CTkButton(end_frame, height= 50 , text="->", command=submit_feedback)
    feedback_button.pack( side='left', padx=(5,5),anchor ='w')  # Space below button




def store_feedback(feedback_data, filename="feedback.json"):
    """Appends feedback data to a JSON file in array format."""
    try:
        # Try to read existing feedback data
        try:
            with open(filename, "r") as f:
                feedback_list = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            feedback_list = []  # Initialize an empty list if the file doesn't exist or is empty
        
        # Append the new feedback data
        feedback_list.append(feedback_data)
        
        # Write the updated list back to the file
        with open(filename, "w") as f:
            json.dump(feedback_list, f, indent=4)  # Use indent for better readability
        
    except Exception as e:
        print(f"Error storing feedback: {e}")

def calculate_average_score(file_path="feedback.json"):
    """Calculates the average rating from stored feedback data."""
    try:
        with open(file_path, "r") as f:
            feedback_data = [json.loads(line) for line in f if line.strip()]
        if not feedback_data:
            return 0  # No feedback available
        
        total_score = sum(entry["rating"] for entry in feedback_data if "rating" in entry)
        average_score = total_score / len(feedback_data)
        return round(average_score, 2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error calculating average score: {e}")
        return 0






# Generate the text
def generate_text(conditional_caption, unconditional_caption,button_values): #result testing variable
    # print(conditional_caption)
    # print (unconditional_caption)

    prompt = 'understand the image provided and use it as much as possible and based on the conditions given generate the text for it. Two statements unconditional and conditional are provided which somewhat are a description of the image use it as reference if your understanding and the statements match and use whatever is there. In case inputs are unclear try put things together on your own.\n\n'+ 'Statements :\n\nConditional : '+conditional_caption+'\nUnconditional : '+ unconditional_caption +'\n\n\nConditions are as follows :\n'+'1. What to do ?' + ' Answer : ' + button_values[0]  + '\n' + '2. Generated text should be in ' + button_values[1] + ' figure of speech.\n'+'3. ' + button_values[2] + ' writing style should be followed for generated text.\n' + '4. The text should be of length ' + button_values[3] + ' words.\n'+'5. The language of text should be ' + button_values[4] + '.\n\n'
    print(prompt)

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    img = Image.open('generated_image.png')

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([prompt, img])

    if response:
        print(response.text)
        global generated_text
        generated_text = response.text
        result.configure(state='normal') # Enable the text box
        result.textbox.delete("1.0", "end") # Clear the text box                                               # work on history tab 
        result.insert("0.0", response.text) # Insert the generated text
        result.configure(state='disabled') # Disable the text box
    else:
        raise ValueError("No response text received from the Gemini model.")

def generate_text_thread(unconditional_caption, conditional_caption,button_values):
    try:
        generate_text(unconditional_caption, conditional_caption,button_values)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Hide the loading indicator
        result.after(0, lambda: loading_label.place_forget())

# # Start the text generation in a separate thread
def start_thread(unconditional_caption, conditional_caption,button_values):
    def run():
        generate_text_thread(unconditional_caption, conditional_caption,button_values)
    
    global thread
    thread = threading.Thread(target=run)
    thread.start()




# Function to create the new window
def create_new_window(unconditional_caption, conditional_caption,prompt_entered, generated_image_path ):
    global result, loading_label  # Declare as global to modify within functions

    new_window = ctk.CTk()
    new_window.title("Text Display")
    new_window.geometry("700x890")
    ctk.set_appearance_mode("dark")  # Set dark mode 

    

    def update_button_values():
        button_values.clear()
        x = content_value_store.get()
        y = speech_value_store.get()
        z = format_dropdown.get()
        a = word_value.get()
        b = language_dropdown.get()
        button_values.append(x)
        button_values.append(y)
        button_values.append(z)
        button_values.append(a)
        button_values.append(b)
        print(button_values)


    # label frame 
    labelframe = ctk.CTkFrame(new_window, corner_radius=15, height=33, width=30) 
    labelframe.pack(pady=10)

    # new window label 
    label = ctk.CTkLabel(labelframe, text="📰 Text Generator 📰", text_font=("", 20), text_color='white', width=512, height=40, corner_radius=15)
    label.pack(pady=10)

    #Text Generation options :


    # option area frame 
    optionmenu_frame = ctk.CTkFrame(new_window, corner_radius=15, height=100) 
    optionmenu_frame.pack(pady=5, padx=50)


    # option label
    optionmenu_label = ctk.CTkLabel(optionmenu_frame, text="📝 What to do ? ", text_font=("", 15), text_color='white', height=40, corner_radius=15)
    optionmenu_label.pack(side='top',padx=10)

    # content selection frame
    content_selection = ctk.CTkFrame(optionmenu_frame, corner_radius=15, height=40, width=30) 
    content_selection.pack( pady = 5 , padx =(10,10), side='top')

    # radio button value store 
    content_value_store = ctk.StringVar(value="None") # default value

    radiobutton1 = ctk.CTkRadioButton(content_selection, text='Describe Image', variable=content_value_store, value="Describe Image",command=update_button_values)
    radiobutton1.pack(side='left', padx=[20, 10], pady=10)

    radiobutton2 = ctk.CTkRadioButton(content_selection, text='Product Description', variable=content_value_store, value="Product Description",command=update_button_values)
    radiobutton2.pack(side='left', padx=10, pady=10)

    radiobutton3 = ctk.CTkRadioButton(content_selection, text='Story Generation', variable=content_value_store, value="Story Generation",command=update_button_values)
    radiobutton3.pack(side='left', padx=10, pady=10)

    radiobutton4 = ctk.CTkRadioButton(content_selection, text='Idea Generation', variable=content_value_store, value="Idea Generation",command=update_button_values)
    radiobutton4.pack( padx=10, pady=10)

    


   
    joining_frame = ctk.CTkFrame(optionmenu_frame, corner_radius=15, height=40, width=30)
    joining_frame.pack(pady=5, side='top', padx=(10,10),anchor ='w')

    # figure of speech selection frame 
    fig_speech_frame = ctk.CTkFrame(joining_frame, corner_radius=15, height=40, width=150) 
    fig_speech_frame.pack(pady=10, side='left', padx=(5,5),anchor ='w')

    # speech selection label 
    fig_speech_label = ctk.CTkLabel(fig_speech_frame, text="Figure of Speech Selection", text_font=("", 12), text_color='white', height=15, corner_radius=15)
    fig_speech_label.pack()

    # radio button value store 
    speech_value_store = ctk.StringVar(value="None") # default value

    radio1 = ctk.CTkRadioButton(fig_speech_frame, text='1st Person', variable=speech_value_store, value="1st Person", command=update_button_values)
    radio1.pack(side='left', padx=[20, 10], pady=10)

    radio2 = ctk.CTkRadioButton(fig_speech_frame, text='2nd Person', variable=speech_value_store, value="2nd Person",command=update_button_values)
    radio2.pack(side='left', padx=10, pady=10)

    radio3 = ctk.CTkRadioButton(fig_speech_frame, text='3rd Person', variable=speech_value_store, value="3rd Person",command=update_button_values)
    radio3.pack(side='left', padx=10, pady=10)





    # Format type selection :
    format_type_frame = ctk.CTkFrame(joining_frame, corner_radius=15, height=40, width=150) 
    format_type_frame.pack(pady=10, side='left', padx=(5,5),anchor ='w')

    # speech selection label 
    format_type__label = ctk.CTkLabel(format_type_frame, text="Content Format Selection", text_font=("", 11), text_color='white', height=13, corner_radius=15)
    format_type__label.pack()

    format_dropdown = ctk.CTkComboBox(
        format_type_frame,
        values=["Paragraph","Summary","Essay","Poem","Music", "Email", "Message","Catchy Phrase" ],
        width=200,
        height=40,
    )
    format_dropdown.pack(pady=5, padx=10)
    
    language_dropdown = ctk.CTkComboBox(
        format_type_frame,
        values=["English", "bengali", "chinese", "german", "Gujarati", "Hindi", "italian", "japanese", "Kannada", "Marathi","Malayalam", "russian", "spanish", "Tamil", "Telugu", "arabic"],
        width=200,
        height=40, 
    )
    language_dropdown.pack(pady=5, padx=10)
    








    # word length selection :
    word_frame = ctk.CTkFrame(optionmenu_frame, corner_radius=15, height=40, width=30)
    word_frame.pack(pady=5, side='top', padx =10,expand=True,fill='x')

    # word selection label 
    word_frame_label = ctk.CTkLabel(word_frame, text="Select the Desired length", text_font=("", 12), text_color='white', height=15, corner_radius=15)
    word_frame_label.pack(pady=(3,0))

    # radio button value store 
    word_value = ctk.StringVar(value="None") # default value

    radio1 = ctk.CTkRadioButton(word_frame, text='7-15', variable=word_value, value="7 - 15", command=update_button_values)
    radio1.pack(side='left', padx=[20, 10], pady=10,expand=True,fill='x')

    radio2 = ctk.CTkRadioButton(word_frame, text='40-50', variable=word_value, value="40 - 50", command=update_button_values)
    radio2.pack(side='left', padx=[20, 10], pady=10,expand=True,fill='x')

    radio3 = ctk.CTkRadioButton(word_frame, text='80-100', variable=word_value, value="80 - 100",command=update_button_values)
    radio3.pack(side='left', padx=10, pady=10,expand=True,fill='x')

    radio4 = ctk.CTkRadioButton(word_frame, text='150-200', variable=word_value, value="150 - 200",command=update_button_values)
    radio4.pack(side='left', padx=10, pady=10,expand=True,fill='x')

    radio5 = ctk.CTkRadioButton(word_frame, text='300-400', variable=word_value, value="300 - 400",command=update_button_values)
    radio5.pack(side='left', padx=10, pady=10,expand=True,fill='x')

    radio6 = ctk.CTkRadioButton(word_frame, text='500+', variable=word_value, value="about 500 or more than it",command=update_button_values)
    radio6.pack(side='left', padx=10, pady=10,expand=True,fill='x')



    button_values = []
    update_button_values()


    generate_text_button = ctk. CTkButton(optionmenu_frame, text="Generate",command=lambda: start_thread(conditional_caption, unconditional_caption,button_values), text_color="white", fg_color="#ff5733" ,height=40,)
    generate_text_button.pack(padx=100, fill="x", pady=5)






 



# add click to unselect 

# gix text generation window  using a square instead (side of unconditional and conditional)

        # Check if the required variables are defined
        # if 'unconditional_caption' not in globals() or 'conditional_caption' not in globals():
        #     raise NameError("Required variables are not defined")


 


# resnet, pytessearct , easy ocr ,opencv can be used for more refined image captioning 




    # text display area
    result = ctk.CTkTextbox(new_window, border_color="grey", border_width=2, corner_radius=15, text_color='white', height=370, text_font=("", 17))
    result.pack(pady=5, fill='x', padx=50)
    result.configure(state='disabled') # Disable the text box


    # Loading indicator
    loading_label = ctk.CTkLabel(result, text="Generated text will display here", text_font=("", 20), text_color='white')
    loading_label.place(relx=0.5, rely=0.5, anchor='center')


    
    setup_feedback_section(new_window,unconditional_caption, conditional_caption,prompt_entered, generated_image_path,button_values) 


    # Close Button 
    close_button = ctk.CTkButton(new_window, text="Close", command=new_window.destroy, text_font=("Arial", 20), text_color="white", fg_color="#20a4f3")
    close_button.pack(pady=10)


    return new_window




# new_window = create_new_window("unconditional_caption", "conditional_caption","prompt_entered", "generated_image_path")
# new_window.mainloop()

