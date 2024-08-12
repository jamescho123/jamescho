import streamlit as st

st.title("Chordsync.AI")
st.subheader("welcome to a free piano accompaniment website")
st.write("Uploading Files")
st.markdown("---")

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

us = m21.environment.UserSettings()
us_path = us.getSettingsPath()
if not os.path.exists(us_path):
    us.create()
print('Path to music21 environment', us_path)
print(us)

us['lilypondPath'] = r'C:\Users\hp\Desktop\bin\lilypond.exe'
# Rest of your Streamlit code


# Initialize OpenAI client with API key from Streamlit secrets
client = openai.OpenAI(
    api_key=st.secrets.OpenAI_key
)

# Allow users to upload multiple files
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
options=[""]
if uploaded_files:
    # Extract file names
    options = [uploaded_file.name for uploaded_file in uploaded_files]

    # Create the selectbox with the file names as options
    selected_file = st.selectbox(
        'Select a file:',
        options,
        help='Choose a file from the dropdown menu'  # Tooltip
    )

    # Find the selected file in the uploaded files
    selected_file_data = next(file for file in uploaded_files if file.name == selected_file)

    # Display the selected file name
    st.write('You selected:', selected_file)

    # Simulate re-uploading the selected file for audio or MIDI file upload
    if selected_file_data:
        st.write("Proceed with the selected file as an audio or MIDI file:")
        # Display the content or handle as needed
        try:
            if selected_file.lower().endswith(('wav', 'mp3', 'mp4', 'mid')):
                st.audio(selected_file_data)
                st.write("Audio or MIDI file accepted.")
                audio=selected_file_data
            else:
                st.write("please upload an audio or MIDI file")
                audio = st.file_uploader("Please upload an audio or MIDI file", type=["WAV", "MP3", "MP4", "MID"])
        except UnicodeDecodeError:
            st.write("Error processing the selected file.")
else:
    st.write("No files uploaded yet.")

def create_accompaniment(musicxml_content):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Create an accompaniment for the following melody in MusicXML format with measures, please do not say anything before or after the MusicXML you provided, it is important that you only provide the musicxml required and nothing else (don't add '''xml):\n\n{musicxml_content}"}
        ],
        temperature=0.7,
        max_tokens=1500  # Adjust token limit as needed
    )
    return response.choices[0].message.content.strip()


audio = st.file_uploader("Please upload an audio or MIDI file", type=["WAV", "MP3", "MP4", "MID"])

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
score = m21.converter.parse(midi_output_path)
st.write("MIDI file has been processed.")
st.write(midi_output_path)
st.audio(midi_output_path, format="audio/mid")
# Convert MusicXML to MIDI
mp3_output_path = midi_output_path.replace('.mid', '.wav').replace('.mid', '.wav')
score.write('midi', fp=mp3_output_path)
st.write(f"Converted MIDI to mp3: {mp3_output_path}")

with open(mp3_output_path, 'rb') as file:
    btn = st.download_button(
        label="Download mp3",
        data=file,
        file_name=mp3_output_path,
        mime='audio/wav'
    )
st.write(mp3_output_path)
st.audio(mp3_output_path, format="audio/wav")