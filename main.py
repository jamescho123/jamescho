import streamlit as st
import verovio
import os

# Initialize the Verovio toolkit
vrvToolkit = verovio.toolkit()

st.title("Chordsync.AI")
st.subheader("welcome to a free piano accompaniment website")
st.write("Uploading Files")
st.markdown("---")

st.slider("This is a slider")

import os
from openai import OpenAI

client = OpenAI(
    api_key=st.secrets.OpenAI_key
)


import streamlit as st
import music21 as m21
import openai
import subprocess
import os

# Initialize OpenAI client with API key from Streamlit secrets
client = openai.OpenAI(
    api_key=st.secrets.OpenAI_key
)

def create_accompaniment(musicxml_content):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Create an accompaniment for the following melody in MusicXML format, do not say anything before our after the MusicXML you provide:\n\n{musicxml_content}"}
        ],
        temperature=0.7,
        max_tokens=1500  # Adjust token limit as needed
    )
    return response.choices[0].message.content.strip()

audio = st.file_uploader("Please upload an audio or MIDI file", type=["WAV", "MP3", "MP4", "MID"])


options = ['Option 1', 'Option 2', 'Option 3']

# Create the selectbox with a default value
selected_option = st.selectbox(
    'Select an option:',
    options,
    index=1,  # Default value is 'Option 2'
    help='Choose an option from the dropdown menu'  # Tooltip
)
hi="Option 1"

# Display the selected option
st.write('You selected:', selected_option)
if audio is not None:
    # Display audio player
    st.audio(audio)
    st.write(f"Uploaded file: {audio.name}")

    # Save the uploaded file to disk
    with open(audio.name, 'wb') as f:
        f.write(audio.getbuffer())

    # Path of the saved file
    saved_file_path = audio.name
    st.write(f"File saved at: {saved_file_path}")

    # Process the MIDI file if it ends with .mid
    if saved_file_path.endswith('.mid'):
        score = m21.converter.parse(saved_file_path)
        st.write("MIDI file has been processed.")

        # Convert MIDI to MusicXML
        musicxml_output_path = saved_file_path.replace('.mid', '.musicxml')
        score.write('musicxml', fp=musicxml_output_path)
        st.write(f"Converted MIDI to MusicXML: {musicxml_output_path}")
        
        # Read the MusicXML content
        with open(musicxml_output_path, 'r') as file_object:
            musicxml_content = file_object.read()
        
        # Display the MusicXML content
        st.text(musicxml_content)
        
        # Create accompaniment using OpenAI
        accompaniment_musicxml = create_accompaniment(musicxml_content)
        st.write("Accompaniment created.")
        
        # Save the accompaniment to a new MusicXML file
        accompaniment_output_path = musicxml_output_path.replace('.musicxml', '_accompaniment.musicxml')
        with open(accompaniment_output_path, 'w') as file_object:
            file_object.write(accompaniment_musicxml)
        
        st.write(f"Accompaniment MusicXML saved at: {accompaniment_output_path}")
        
    
        # Optionally display the accompaniment MusicXML content
        st.text(accompaniment_musicxml)
        
        # Provide a download link for the new MusicXML file
        with open(accompaniment_output_path, 'rb') as file:
            st.download_button(
                label="Download Accompaniment MusicXML",
                data=file,
                file_name=os.path.basename(accompaniment_output_path)
            )
existing_file_path = accompaniment_output_path  # Change this to the path of your existing file

# Display the provided Mu   sicXML file path
st.write(f"Using existing file: {existing_file_path}")

# Process the MusicXML file
score = m21.converter.parse(existing_file_path)
st.write("MusicXML file has been processed.")

# Convert MusicXML to MIDI
midi_output_path = existing_file_path.replace('.musicxml', '.mid').replace('.xml', '.mid')
score.write('midi', fp=midi_output_path)
st.write(f"Converted MusicXML to MIDI: {midi_output_path}")

# Display a download link for the MIDI file
with open(midi_output_path, 'rb') as file:
    btn = st.download_button(
        label="Download MIDI",
        data=file,
        file_name=midi_output_path,
        mime='audio/midi'
    )
st.audio(midi_output_path)
