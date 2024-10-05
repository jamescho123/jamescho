import os

import streamlit as st
import music21 as m21
import openai
import subprocess
import os

import streamlit as st
import subprocess
import music21 as m21
import os
import streamlit as st
import music21 as m21
import librosa
import pretty_midi
import numpy as np
from io import BytesIO
from openai import OpenAI
import openai
client = OpenAI(
    api_key=st.secrets.OpenAI_key
)
def create_accompaniment(musicxml_content):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Create an accompaniment for the following melody in MusicXML format:\n\n{musicxml_content}"}
        ]
    )
    return response.choices[0].message.content.strip() if response else None
def process_midi_file(midi_file_path):
    try:
        # Convert MIDI to MusicXML
        score = m21.converter.parse(midi_file_path)
        st.write("MIDI file has been processed.")

        musicxml_output_path = midi_file_path.rsplit('.', 1)[0] + '.musicxml'
        score.write('musicxml', fp=musicxml_output_path)
        st.write(f"Converted MIDI to MusicXML: {musicxml_output_path}")

        # Read the MusicXML content
        with open(musicxml_output_path, 'r') as file_object:
            musicxml_content = file_object.read()

        with st.expander("MusicXML of the uploaded file"):
            st.code(musicxml_content, language='xml')

        # Create accompaniment using OpenAI
        accompaniment_musicxml = create_accompaniment(musicxml_content)
        st.write("Accompaniment created.")

        # Save the accompaniment to a new MusicXML file
        accompaniment_output_path = midi_file_path.rsplit('.', 1)[0] + '_accompaniment.musicxml'
        with open(accompaniment_output_path, 'w') as file_object:
            file_object.write(accompaniment_musicxml)

        st.write(f"Accompaniment MusicXML saved at: {accompaniment_output_path}")

        with st.expander("MusicXML of the generated accompaniment"):
            st.code(accompaniment_musicxml, language='xml')

        # Provide a download link for the new MusicXML file
        with open(accompaniment_output_path, 'rb') as file:
            st.download_button(
                label="Download Accompaniment MusicXML",
                data=file,
                file_name=os.path.basename(accompaniment_output_path),
                mime="application/xml"
            )

        # Return the accompaniment output path
        return accompaniment_output_path

    except Exception as e:
        st.error(f"An error occurred while processing the MIDI file: {e}")
        return None
# Function to generate sheet music image using MuseScore
def generate_sheet_image(midi_output_path):
    output_image_path = midi_output_path.rsplit('.', 1)[0] + '.png'
    
    result = subprocess.run(
        ['MuseScore4', midi_output_path, '-o', output_image_path],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        st.error(f"MuseScore error: {result.stderr}")
        return None
    
    st.success("MuseScore ran successfully.")
    return output_image_path if os.path.exists(output_image_path) else None

# Main processing logic
audio = st.file_uploader("Please upload a MIDI or WAV file", type=["WAV", "MID"])
if audio:
    saved_file_path = os.path.join("uploads", audio.name)
    os.makedirs(os.path.dirname(saved_file_path), exist_ok=True)
    
    with open(saved_file_path, 'wb') as f:
        f.write(audio.getbuffer())

    st.write(f"File saved at: {saved_file_path}")

    # Process the MIDI file
    if saved_file_path.endswith('.mid'):
        st.write("MIDI file detected, processing...")
        accompaniment_file = process_midi_file(saved_file_path)
        
        # Generate and display sheet image
        if accompaniment_file:
            sheet_image = generate_sheet_image(accompaniment_file)
            if sheet_image:
                st.image(sheet_image, caption="Generated Sheet Music")
    else:
        st.write("Please upload a MIDI file.")
def generate_sheet_image(midi_file_path):
    midi_file_path = os.path.abspath(midi_file_path)
    output_image_path = midi_file_path.rsplit('.', 1)[0] + '.png'
    

    # Run MuseScore to generate the image
    result = subprocess.run(
        [r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe', midi_file_path, '-o', output_image_path],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        st.error(f"MuseScore error: {result.stderr}")
    else:
        st.success("MuseScore ran successfully.")
  
    
    st.write(output_image_path)# Check if the image file was created
    

    return None


# Streamlit file uploader
uploaded_file = st.file_uploader("Upload a MIDI file", type=["MID"])

if uploaded_file is not None:
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    saved_file_path = os.path.join(uploads_dir, uploaded_file.name)
    with open(saved_file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    st.write(f"File saved at: {saved_file_path}")

    # Generate sheet music image
    sheet_image_path = generate_sheet_image(saved_file_path)
    if sheet_image_path and os.path.exists(sheet_image_path):
        # Create a local URL-like path
        sheet_image_path = sheet_image_path.replace("C:\\Users\hp\Documents\GitHub\jamescho\\uploads\\", "/uploads/")
        st.image(sheet_image_path, caption='Generated Sheet Music', use_column_width=True)
        st.write(f"Image can be accessed at: {sheet_image_path}")

        st.image(sheet_image_path, caption='Generated Sheet Music', use_column_width=True)
import glob
uploads_dir="uploads"

files=glob.glob(uploads_dir+"/"+uploaded_file.name.replace(".mid","*.png"))
for file in files:
    st.image(file, caption=file, use_column_width=True)
