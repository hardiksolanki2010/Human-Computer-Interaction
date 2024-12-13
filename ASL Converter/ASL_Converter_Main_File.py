import os
from PIL import Image, ImageSequence
import streamlit as st
from gtts import gTTS
import tempfile
import speech_recognition as sr
from word2number import w2n


# Function for Text Speech to ASL Conversion
def text_to_asl_gif(text, output_path="asl_output.gif"):
    text = text.upper()
    frames = []

    for char in text:
        if char.isalpha():
            gif_path = os.path.join("asl_gifs", f"{char}.gif")
            if os.path.exists(gif_path):
                try:
                    with Image.open(gif_path) as img:
                        for frame in ImageSequence.Iterator(img):
                            frames.append(frame.copy())
                except Exception as e:
                    st.error(f"Error processing GIF for '{char}': {e}")
            else:
                st.warning(f"GIF for '{char}' not found at path: {gif_path}")
        else:
            st.info(f"Skipping non-alphabet character: '{char}'")

    if frames:
        frames[0].save(
            output_path, save_all=True, append_images=frames[1:], duration=500, loop=0
        )
        return output_path
    else:
        return None


# Function for Numerical Speech to ASL Conversion
def text_to_asl_number_gif(text, image_folder="asl_blender", output_path="asl_number_output.gif"):
    digits = ''.join(filter(str.isdigit, text))
    if not digits:
        st.error("No numeric content found in the spoken input.")
        return None

    frames = []

    for digit in digits:
        image_path = os.path.join(image_folder, f"{digit}.png")
        if os.path.exists(image_path):
            with Image.open(image_path) as img:
                for _ in range(5):
                    frames.append(img.copy())
        else:
            st.warning(f"Image for digit '{digit}' not found.")

    if frames:
        frames[0].save(
            output_path, save_all=True, append_images=frames[1:], duration=500, loop=0
        )
        return output_path
    else:
        return None


# Speech Recognition Function
def recognize_speech_to_text(time_limit=5):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening for speech... Please speak.")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=time_limit)
            st.info("Processing speech...")
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Error with the speech recognition service: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    return ""


# Word to Number Conversion for Numerical ASL
def convert_words_to_numbers(text):
    try:
        return str(w2n.word_to_num(text.lower()))
    except ValueError:
        st.error("Unable to convert spoken input to a valid number.")
        return None


# Streamlit App
st.title("ASL Converter")
st.write("Select an option to convert your speech to ASL.")

# Text Speech to ASL Button
if st.button("Text Speech to ASL"):
    st.header("Text Speech to ASL")
    spoken_text = recognize_speech_to_text(time_limit=5)
    if spoken_text:
        st.success(f"Recognized Text: {spoken_text}")
        gif_path = text_to_asl_gif(spoken_text)
        if gif_path:
            st.success("ASL GIF created successfully!")
            st.image(gif_path)

# Numerical Speech to ASL Button
if st.button("Numerical Speech to ASL"):
    st.header("Numerical Speech to ASL (Blender Images)")
    spoken_text = recognize_speech_to_text(time_limit=3)
    if spoken_text:
        numeric_text = convert_words_to_numbers(spoken_text)
        if numeric_text:
            st.success(f"Converted to Numeric Text: {numeric_text}")
            gif_path = text_to_asl_number_gif(numeric_text)
            if gif_path:
                st.success("ASL GIF created successfully!")
                st.image(gif_path)
