import tkinter as tk
import customtkinter as ctk 
from PIL import Image,ImageTk
from turtle import st, width
from networkx import core_number
from numpy import pad
from Story import  create_new_window
import torch
from torch import autocast, device
import os
import threading 
import warnings
import tkinter.messagebox as messagebox
warnings.filterwarnings('ignore') # ignore warnings  




# from authtoken import auth_token

# from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler  
from diffusers import StableDiffusion3Pipeline 
from transformers import BlipProcessor, BlipForConditionalGeneration
# from transformers import T5EncoderModel, BitsAndBytesConfig #(sd3 model)

# code downloads the model in users/.cache/hugging face folder

# Create the app
app = ctk.CTk()
app.geometry("600x805")
app.title("VisionaryScribe")     
app.set_appearance_mode("dark")    
# app.configure(bg='gray20')


# Pipelines

device = "cuda"

import torch
print(torch.cuda.is_available())
print(torch.cuda.current_device())
print(torch.cuda.get_device_name(torch.cuda.current_device()))
# Stable Diffusion Pipeline 3
# ***************************
model_id = "stabilityai/stable-diffusion-3-medium-diffusers"
blip_model_name = "Salesforce/blip-image-captioning-large"  


pipe = StableDiffusion3Pipeline.from_pretrained( 
    model_id,
    text_encoder_3=None,
    tokenizer_3=None,
    torch_dtype=torch.float16
).to("cuda")

# weight file checker
print(f"Using model weights from: {model_id} app successfully loaded")


# BLIP model for captioning
processor = BlipProcessor.from_pretrained(blip_model_name)
blip_model = BlipForConditionalGeneration.from_pretrained(blip_model_name, torch_dtype=torch.float16).to("cuda")
#ADD ON 
print(f"Using model weights from: {blip_model_name} app successfully loaded")


# default value
guidance_scale=7.0  
image_height = 256
image_width = 256
inference_steps = ctk.StringVar(value="10")

def move_cursor_word_right(event):
    text_var = prompt.get()  # Assuming prompt is linked to a StringVar
    current_text = text_var
    current_position = len(current_text)
    new_position = current_text.find(' ', current_position + 1)
    if new_position == -1:
        new_position = len(current_text)


def move_cursor_word_left(event):
    text_var = prompt.get()  # Assuming prompt is linked to a StringVar
    current_text = text_var
    # Simulate cursor position based on text length (not accurate)
    current_position = len(current_text)
    new_position = current_text.rfind(' ', 0, current_position - 1)
    if new_position == -1:
        new_position = 0


def clear_prompt():
    prompt.delete(0, tk.END)
    prompt.focus_set()
    

def update_guidance_scale(value):
    global guidance_scale
    guidance_scale = float(value)
    guidance_scale_label.configure(text=f"Guidance Scale: {guidance_scale:.2f}")
    # print(f"Guidance Scale updated to: {guidance_scale}")

def optionmenu_callback(choice):
    global image_height, image_width
    print("optionmenu dropdown clicked:", choice)
    if choice == "512*512":
        image_height, image_width = 512, 512
    elif choice == "512*720":
        image_height, image_width = 512, 720
    elif choice == "512*1024":
        image_height, image_width = 512, 1024
    elif choice == "720*512":
        image_height, image_width = 720, 512
    elif choice == "720*720":
        image_height, image_width = 720, 720
    elif choice == "720*1024":
        image_height, image_width = 720, 1024
    elif choice == "1024*512":
        image_height, image_width = 1024, 512
    elif choice == "1024*720":
        image_height, image_width = 1024, 720
    elif choice == "1024*1024":
        image_height, image_width = 1024, 1024
    # Add more options as needed


# Generate button thread generator 
def imagetext_generation_thread():
    def run():
        try:
            generate()
        except Exception as e:
            print(f"Error: {e}")
            # messagebox.showerror("Error", str(e))  # Show error in UI
    
    generate_thread = threading.Thread(target=run)
    generate_thread.start()

def blip_text_generation(image):
    """
    Generates a caption for the given image using the BLIP model.
    
    Args:
        image_path (str): Path to the input image.

    Returns:
        str: Generated caption for the image.
    """
    # if isinstance(image, str):
    #     # Assuming the image is a file path
    #     from PIL import Image
    #     image = Image.open(image)
    # else:
    inputs = processor(images=image, return_tensors="pt").to(device)
    
    # Generate caption with the BLIP model
    output = blip_model.generate(**inputs, max_length=256)
    caption = processor.decode(output[0], skip_special_tokens=True)
    
    return caption

# Modify the generate    

def generate():     

# Generate the image
    with autocast(device):  
        global guidance_scale, image_height, image_width
        try:
            # seed_value = seed_value_entry.get()  # Assuming `seed_value_entry` is your entry widget for the seed
            # if seed_value:
            #     seed = int(seed_value)
            #     torch.manual_seed(seed) 
            image = pipe(
                prompt.get(),
                guidance_scale=guidance_scale,
                # negative_prompt= "",
                num_inference_steps= int(inference_value_entry.get()),
                height=image_height, 
                width= image_width,
                max_sequence_length= 256,
                # seed= int(seed_value_entry.get())  # modify

            )["images"][0]   
            image_path = "generated_image.png"
            image.save(image_path) 
            print(type(image))



            
            resized_img = image.resize((635, 350), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(resized_img)           #converting and storing to tk format
            img_ref.configure(image=img)
            img_ref.resized_img = img #keep a reference to the image



         
         
            global unconditional_caption, conditional_caption, generated_image_path, prompt_entered
        # Store the prompt entry value and image path in global variables
            prompt_entered = prompt.get()
            generated_image_path = image_path


            # unconditional image captioning
  
            unconditional_caption = blip_text_generation(image)
            unconditional_caption_label.configure(state='normal')  # Enable the text box
            # unconditional_caption_label.delete("1.0", "end")  # Clear previous text
            unconditional_caption_label.insert("1.0", unconditional_caption)  # Insert new text
            unconditional_caption_label.configure(state='disabled')  # Disable the text box



            # conditional image captioning
            
            conditional_caption = blip_text_generation(image)
            conditional_caption_label.configure(state='normal')  # Enable the text box
            # conditional_caption_label.delete("1.0", "end")  # Clear previous text
            conditional_caption_label.insert("1.0", conditional_caption)  # Insert new text
            conditional_caption_label.configure(state='disabled')  # Disable the text box
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", str(e))  # Show error in UI



def check_and_create_window():
    try:
        # Check if the required variables are defined
        if 'unconditional_caption' not in globals() or 'conditional_caption' not in globals():
            raise NameError("Required variables are not defined")
      

        # Check if the image file exists
        image_path = generated_image_path
        if not os.path.exists(image_path):
            messagebox.showwarning("Warning", f"File not found: {image_path}")
            return
        
        print(generated_image_path)
        print(prompt_entered)
        
        # Call the function to create the new window
        create_new_window(unconditional_caption, conditional_caption,prompt_entered, generated_image_path).mainloop()
    except NameError as e:
        # Display a warning message if the variables are not defined
        messagebox.showwarning("Warning", "Please generate an image first, then click 'Generate'.")











# App label frame 
labelframe = ctk.CTkFrame(app, corner_radius=15, height=33, width=30) 
labelframe.grid(row=0, column=0, columnspan=2, pady=10)

# App introduction label
text1 = "🌃 Image  Generator 🌇"

label = ctk.CTkLabel(labelframe, text= text1 , text_font=("", 30), text_color='white', width=512, height=40, corner_radius=15)
label.grid(row=0, column=0, pady=10)







#Parent Frame
parent_frame = ctk.CTkFrame(app, corner_radius=15, height=33, width=30) 
parent_frame.grid(row=1, column=0, columnspan=2, pady=5 , padx =40)

# Configure columns to take 80% and 20% of the space respectively
parent_frame.columnconfigure(0, weight=4)
parent_frame.columnconfigure(1, weight=1)

# Prompt box 
prompt = ctk.CTkEntry(parent_frame, width=365, height=35, text_font=("Arial", 16), text_color="black", corner_radius=10, fg_color="white", placeholder_text="Type your prompt here ⌨ ->")
prompt.grid(row=1, column=0, sticky='ew', padx=(10, 5), pady=(10, 5))  # Adjust padding as needed

# Clear button widget 
clear_button = ctk.CTkButton(parent_frame, width=25, height=35, text="❌", command=clear_prompt, text_font=("Arial", 20), text_color="white", corner_radius=15, fg_color="#20a4f3")
clear_button.grid(row=1, column=1, padx=(10, 10), pady=(10, 5), sticky='ew')










# Create a frame to hold all the widgets
control_frame = ctk.CTkFrame(parent_frame, corner_radius=15,height=63, width=30)
control_frame.grid(row=2, column=0, columnspan=2,  padx=10, pady=5)

# label for the guidance_scale_slider
guidance_scale_label = ctk.CTkLabel(control_frame, text=f"Guidance Scale : {guidance_scale:.2f}", text_color='white', text_font=("Arial", 16))
guidance_scale_label.grid(row=0, column=0, padx=(0,30), pady=(0,10), sticky='ew')  # Adjust padding as needed

# Create the slider for adjusting guidance_scale
guidance_scale_slider = ctk.CTkSlider(control_frame, from_=0, to=15, height=15, width=60, command=update_guidance_scale)
guidance_scale_slider.grid(row=0, column=0, padx=(35,60), pady=(35,10), sticky='ew')  # Adjust layout as needed

# Option menu for image size
optionmenu_var = ctk.StringVar(value="256*256")  # default value
optionmenu = ctk.CTkOptionMenu(control_frame, height=30, values=["512*512", "512*720", "512*1024", "720*512", "720*720", "720*1024", "1024*512", "1024*720", "1024*1024"], command=optionmenu_callback, width=160, text_font=("Arial", 19), variable=optionmenu_var, button_color="#20a4f3")    
optionmenu.grid(row=0, column=1, padx=(0,10), pady=(0,10), sticky='we')

        

# Inference Steps Label
inference_steps_label = ctk.CTkLabel(control_frame, text="Inference Steps: ", text_font=("Arial", 16), text_color="white")
inference_steps_label.grid(row=1, column=0, padx=(20,106), pady=(0,5))

# Inference Value input

inference_value_entry = ctk.CTkEntry(control_frame, width=60, height=28, text_font=("Arial", 15), text_color="black", fg_color="white", textvariable = inference_steps)
inference_value_entry.grid(row=1, column=0, padx=(160,20 ), pady=(0,5))

# Create a frame for seed value input
seed_frame = ctk.CTkFrame(control_frame, height=28,width=100)  
seed_frame.grid(row=1, column=1, padx=(0, 10), pady=(5, 5))

# Seed Value Label
seed_label = ctk.CTkLabel(seed_frame, text="Seed :", text_font=("Arial", 15), text_color="white" ,width= 40,corner_radius=15)
seed_label.grid(row=0, column=0 , pady=0)

# Seed Value input
seed_value = ctk.StringVar(value=None)
seed_value_entry = ctk.CTkEntry(seed_frame, width=96, height=25, text_font=("Arial", 16), text_color="black", fg_color="white", placeholder_text="Enter here!", textvariable=seed_value)
seed_value_entry.grid(row=0, column=1, padx=(0, 1), pady=0)









# Create a CTkFrame with a grey background to act as the border
img_border_frame = ctk.CTkFrame(app,  border_color="grey", border_width=2, corner_radius=13)
img_border_frame.grid(row=4, padx=40, pady=5, columnspan=2)

# Adjust the img_ref label to be inside the frame, with slightly smaller dimensions to fit within the border
 
img_ref = ctk.CTkLabel(img_border_frame, height= 300,width=518,text_font=("Arial", 20),text=" Generated Image 😃",  corner_radius=15,)
img_ref.pack(padx=4,pady=4,anchor='center')  # Center the label inside the frame









# Text window opener
text_generation_frame = ctk.CTkFrame(app, corner_radius=15, height=190, width=500)  # Adjusted width
text_generation_frame.grid(row=5, column=0, columnspan=2, pady=5, padx=40)

# Frame for conditional caption with scrollbar
conditional_frame = ctk.CTkFrame(text_generation_frame, corner_radius=15)
conditional_frame.grid(row=0, column=0, padx=(10, 10), pady=(5, 2.5))  # Adjusted padding

conditional_caption_label = ctk.CTkTextbox(conditional_frame, border_color="grey", border_width=2, corner_radius=15, height=60, width=350, text_color='white', text_font=("", 12))
conditional_caption_label.pack(side='left', fill='both', expand=True)
conditional_caption_label.configure(state='disabled')

conditional_scrollbar = ctk.CTkScrollbar(conditional_frame, command=conditional_caption_label.yview, height=10)
conditional_scrollbar.pack(side='right', fill='y')
conditional_caption_label.configure(yscrollcommand=conditional_scrollbar.set)

# Frame for unconditional caption with scrollbar
unconditional_frame = ctk.CTkFrame(text_generation_frame, corner_radius=15)
unconditional_frame.grid(row=1, column=0, padx=(10, 10), pady=(2.5, 5), sticky='ew')  # Adjusted padding

unconditional_caption_label = ctk.CTkTextbox(unconditional_frame, border_color="grey", border_width=2, corner_radius=15, height=60, width=350, text_color='white', text_font=("", 12))
unconditional_caption_label.pack(side='left', fill='both', expand=True)
unconditional_caption_label.configure(state='disabled')

unconditional_scrollbar = ctk.CTkScrollbar(unconditional_frame, command=unconditional_caption_label.yview, height=10)
unconditional_scrollbar.pack(side='right', fill='y')
unconditional_caption_label.configure(yscrollcommand=unconditional_scrollbar.set)

open_window_button = ctk.CTkButton(text_generation_frame, width=100, height=100, text_color="white", fg_color="#20a4f3", text="Text Window", command=lambda: check_and_create_window(), corner_radius=15, text_font=("", 14))
open_window_button.grid(row=0, column=1, rowspan=2, padx=(0, 10), pady=5, sticky='ns')  # Adjusted padding

# Set column weights to ensure proper distribution of space
text_generation_frame.grid_columnconfigure(0, weight=1)
text_generation_frame.grid_columnconfigure(1, weight=0)








# Trigger button
# Button to trigger image generation
trigger = ctk.CTkButton(
    height=60, 
    width=150, 
    text_font=("Arial", 20, "bold"), 
    text_color="white", 
    fg_color="#ff5733",  # Changed to a more vibrant color
    text="Generate", 
    corner_radius=15,  # Increased corner radius for a more rounded look
    command=imagetext_generation_thread
) 
trigger.grid(row=6, columnspan=2, padx=20, pady=10, sticky='nsew')  # Increased padding for better spacing
  






# create_new_window(unconditional_caption,conditional_caption).mainloop()



#bindings 

app.bind("<Return>", lambda event= None: generate()) # set's return key -> generate
# prompt.bind("<FocusIn>", on_entry_click)
# prompt.bind("<FocusOut>", on_focus_out)
app.bind('<Control-Left>', move_cursor_word_left)
app.bind('<Control-Right>', move_cursor_word_right)
app.columnconfigure(0, weight=1)




# Ensure the main loop starts
if __name__ == "__main__":
    print("Starting app.py")
    app.mainloop()  