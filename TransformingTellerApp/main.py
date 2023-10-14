'''
Rachael Savage
CSC285-Python II
Professor Tony Hinton
9/16/23
Python: 3.11.5
Pygame:2.5.1
Markovify:0.9.4

'''
import tkinter as tk #built-in GUI
from tkinter import PhotoImage #to use images
import markovify #generate text
import pygame #for sounds
import os #file path

# import parameters from the speech module
from speech import text_to_speech, api_key, voice_id
#built-in lib used to generate a unique identifier for temporary audio files that are created during the text-to-speech process
import uuid

# Initialize pygame to play sounds
pygame.init()

#custom event to end music playback
VOICE_READING_DONE = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(VOICE_READING_DONE)

# Create a dictionary to store image-sound pairs for each theme
theme_data = {
    "Fantasy": [("media/fantasy.png", "media/fantasy.mp3")],
    "Horror": [("media/horror.png", "media/horror.mp3")],
    "Mystery": [("media/mystery.png", "media/mystery.mp3")],
    "Romance": [("media/romance.png", "media/romance.mp3")],
    "Sci-fi": [("media/sci-fi.png", "media/sci-fi.mp3")],
    # Add more genres here
}

# specify the folder that contain stories text files 
story_folder = "Story"

# Create Markovify models to loop through the themes
markov_models = {}
for theme in theme_data:
    theme_lower = theme.lower()
    theme_data_file = os.path.join(story_folder, f"{theme_lower.capitalize()}.txt")
    
    with open(theme_data_file, encoding="utf-8") as f:
        text_data = f.read()
        
    markov_models[theme] = markovify.Text(text_data)

# Create the main application window
app = tk.Tk()
app.title("Transforming Teller App")

# Initialize variables
current_theme = tk.StringVar(value="Fantasy")  # Default theme
current_page = 0

#declare global vars to store the background music/sounds for each story
global background_music
background_music = None
files_to_delete = [] #empty list to store temp files speech to call and delete them
# Create a function to perform text-to-speech
def perform_text_to_speech(text):
    global background_music
    try:          #use api speech
        audio_data = text_to_speech(api_key, voice_id, text)
        if audio_data:
            #create a temporary file: use a unique UUID to avoid conflicts with bg sounds
            temp_filename = f"temp_{uuid.uuid4()}.mp3"
            with open(temp_filename, 'wb') as temp_audio:
                temp_audio.write(audio_data)
            files_to_delete.append(temp_filename)

            # Debugging: Check if file exists and is not empty
            if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                print(f"File {temp_filename} exists and is not empty.")
            else:
                print(f"File {temp_filename} either doesn't exist or is empty.")
                return

            # Play the generated audio
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()

            # Get the current time in milliseconds
            start_time = pygame.time.get_ticks()
#measure the time it takes for the text-to-speech to complete and handle the VOICE_READING_DONE event 
            # Wait for the voice reading to complete
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == VOICE_READING_DONE:
                        if background_music:
                            background_music.stop()
                        waiting = False

            # Calculate the time elapsed since starting so that it can be deleted after reading
            elapsed_time = pygame.time.get_ticks() - start_time

            # delay before deleting the file 
            if elapsed_time < 5000:  # Wait for 5 seconds before deleting
                pygame.time.wait(5000 - elapsed_time)

            #  delete the temp audio file
            os.remove(temp_filename)
#error handling
    except Exception as e:
        print(f"Text-to-speech error: {e}")

#to clean up the audio temp files
def cleanup_files():
    global files_to_delete
    for f in files_to_delete:
        try:
            os.remove(f)
            files_to_delete.remove(f)
        except Exception as e:
            pass  # if error occurs, pass and try again later
       
# Create a function to update the story based on user choices
def update_story():
    global current_page #declare global to modify later
    theme = current_theme.get() #retrieve theme from Tkinter StringVar
    text_model = markov_models[theme]#call the marko model
    
    # Check if story has ended
    if current_page >= len(theme_data[theme]):
        text_label.config(text="The story has ended. Choose a new theme.")
        image_label.config(image=None)
        pygame.mixer.music.stop()
        current_page = 0
        return #reset to main page
    
    # Generate text for the story, set it to generate 1 paragragh, by default marko generate sentences
    generated_sentences = [text_model.make_sentence() for _ in range(5)]
    filtered_sentences = [s for s in generated_sentences if s is not None]
    generated_paragraph = " ".join(filtered_sentences) #prevent generate incomplete/odd sentences
    text_label.config(text=generated_paragraph)
    
    # Get the image and sound paths for the current theme and page
    img_path, sound_path = theme_data[theme][current_page]

    # Update the image for the story
    image = PhotoImage(file=img_path)
    image_label.config(image=image)
    image_label.image = image
    
    # Set background music and its volume
    background_music = pygame.mixer.Sound(sound_path)
    background_music.set_volume(0.2)  # Set to 20% volume
    background_music.play(-1)#loop indef sound

    # Delay the text-to-speech by 0.5sec to let background music to start 1st
    app.after(500, perform_text_to_speech, generated_paragraph)
    #incre the page var to move to next page
    current_page += 1


# Create a function to return to the main menu and choose a new theme
def return_to_main_menu():
    global current_page
    current_page = 0 #reset to the main page
    text_label.config(text="Choose a new theme.")
    image_label.config(image=None)
    pygame.mixer.stop()

# Create the GUI elements
#                                App title
theme_label = tk.Label(app, text="☠ WELCOME TO THE TRANSFORMING TELLER APP", font=("Arial", 30), fg="dark red", bg="black")
theme_label.pack(pady=20)  # Move away from the margin top

# Introduction label
intro_text = (
    "Transforming Teller app is your gateway to captivating adventures across five distinct genres. "
    "In the realm of Fantasy, embark on epic quests and mystical journeys. For those who dare, explore the spine-tingling tales of Horror. "
    "Solve intricate puzzles and delve into the enigmatic world of Mystery. Experience the magic of Romance, where love stories unfold in captivating settings. "
    "And finally, voyage to distant galaxies and futuristic worlds in the realm of Sci-Fi. "
    "Immerse yourself in enchanting stories narrated by our soothing voices as we transport you to far-off lands with our captivating tales."
)
intro_label = tk.Label(app, text=intro_text, font=("Arial", 14), fg="#B8860B", bg="black", wraplength=1800)  # Adjust wraplength as needed
intro_label.pack(pady=20)


# Create a frame to group theme selection and start buttons
button_frame = tk.Frame(app, bg="black")  # Set the background color to black
button_frame.pack()
#group the button for selecting themes and marko
theme_menu = tk.OptionMenu(button_frame, current_theme, *markov_models.keys())
theme_menu.configure(bg="#333333")  # Set the background color
theme_menu.pack(side=tk.LEFT, padx=20)  # Add padding and adjust alignment

start_button = tk.Button(button_frame, text="Start Story", command=lambda: update_story())
start_button.configure(bg="#006400")  # Set the background color
start_button.pack(side=tk.LEFT, padx=20)  # Add padding and adjust alignment

return_button = tk.Button(app, text="Return to Menu", command=return_to_main_menu, bg="#800000")
return_button.pack()
#                                   text display horizontally
text_label = tk.Label(app, text="", wraplength=1500, bg="black", fg="grey")  # bg is black and text color is grey
text_label.pack()

# Displaying images within your GUI
image_label = tk.Label(app)
image_label.pack()

app.geometry("800x600")  # Screen initial loading size
app.configure(bg="black")  # Background

#try to perform clean up deleting temp audio files
def periodic_cleanup():
    cleanup_files()
    app.after(2000, periodic_cleanup)  # Run cleanup every 5 seconds

periodic_cleanup()

def on_closing():
    """Called when the Tkinter window is closing."""
    pygame.mixer.music.stop()  # Stop any active playback
    pygame.time.wait(500)  # Give pygame some time to release files
    cleanup_files()  # Cleanup the temporary files
    pygame.quit()  # Ensure pygame exits cleanly
    app.destroy()  # Close the tkinter app

# Start the Tkinter main loop
app.mainloop()
# Cleanup any remaining files after the mainloop is terminated
cleanup_files()
