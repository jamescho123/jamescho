import streamlit as st


import librosa
import pretty_midi
import numpy as np
from io import BytesIO
st.title("Chord-sync")
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
                st.audio(selected_file_data, format="audio/mpeg")
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


import os
import streamlit as st
import music21 as m21
import librosa
import pretty_midi
import numpy as np
from io import BytesIO

# Assume create_accompaniment is defined elsewhere
def create_accompaniment(musicxml_content):
    # Placeholder implementation
    return musicxml_content  # Replace with actual accompaniment creation logic

# Function to convert WAV to MIDI using librosa and pretty_midi
def wav_to_midi_librosa(wav_file):
    # Load the WAV file using librosa
    y, sr = librosa.load(wav_file, sr=None)

    # Extract pitches and magnitudes using librosa's piptrack
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    # Create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()

    # Create an instrument instance (e.g., Acoustic Grand Piano)
    instrument = pretty_midi.Instrument(program=0)

    # Time array for each frame
    time_per_frame = librosa.frames_to_time(np.arange(pitches.shape[1]), sr=sr)

    # Loop through frames and extract pitch data
    for t in range(pitches.shape[1]):
        # Find the index of the maximum magnitude (loudest pitch in the frame)
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]

        # Only consider pitches above 0 (ignore frames with no detected pitch)
        if pitch > 0:
            # Convert the pitch from Hz to MIDI note number
            midi_note = pretty_midi.hz_to_note_number(pitch)

            # Create a MIDI note with the detected pitch and add it to the instrument
            note = pretty_midi.Note(
                velocity=100,  # Set velocity (how loud the note should be)
                pitch=int(midi_note),  # The detected MIDI note number
                start=time_per_frame[t],  # Start time of the note
                end=time_per_frame[t] + 0.1  # Duration of the note (adjust as needed)
            )
            instrument.notes.append(note)

    # Add the instrument to the PrettyMIDI object
    midi.instruments.append(instrument)

    # Save the MIDI data to a BytesIO object
    midi_io = BytesIO()
    midi.write(midi_io)
    midi_io.seek(0)

    return midi_io

# Function to process a MIDI file: convert to MusicXML and create accompaniment
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

# Main logic for file upload and processing
audio = st.file_uploader("Please upload a MIDI or WAV file", type=["WAV", "MID"])

if audio is not None:
    st.audio(audio)
    st.write(f"Uploaded file: {audio.name}")

    # Save the uploaded file to disk
    saved_file_path = os.path.join("uploads", audio.name)
    os.makedirs(os.path.dirname(saved_file_path), exist_ok=True)
    with open(saved_file_path, 'wb') as f:
        f.write(audio.getbuffer())

    st.write(f"File saved at: {saved_file_path}")

    # Detect whether the uploaded file is a WAV or MIDI file
    if saved_file_path.lower().endswith('.mid'):
        st.write("MIDI file detected. Processing as MIDI...")
        existing_file_path = process_midi_file(saved_file_path)

    elif saved_file_path.lower().endswith('.wav'):
        st.write("WAV file detected. Converting to MIDI...")

        # Convert WAV to MIDI
        midi_io = wav_to_midi_librosa(saved_file_path)

        # Save the generated MIDI file
        midi_output_path = saved_file_path.rsplit('.', 1)[0] + ".mid"
        with open(midi_output_path, 'wb') as f:
            f.write(midi_io.getbuffer())

        st.write(f"Converted WAV to MIDI: {midi_output_path}")

        # Process the generated MIDI file
        existing_file_path = process_midi_file(midi_output_path)

    # Display the existing file path
    if existing_file_path:
        st.write(f"Using existing file: {existing_file_path}")
else:
    st.info("Please upload a file to proceed.")



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

import streamlit as st
from midi2audio import FluidSynth
import fluidsynth

import os

    # Ensure the soundfont path is correct
soundfont_path = r"C:\Users\hp\Downloads\FluidR3_GM\FluidR3_GM.sf2"


if os.path.exists(soundfont_path):
        fs = FluidSynth(soundfont_path)
        
        # Convert MIDI to WAV
        wav_output_path = midi_output_path.replace(".mid", ".wav").replace(".midi", ".wav")
        st.write(midi_output_path)
      
        fs.midi_to_audio(midi_output_path, wav_output_path)
        st.write(wav_output_path)
        # Play the generated WAV file
        with open(wav_output_path, "rb") as audio_file:
            st.audio(audio_file.read(), format='audio/wav')

        # Provide a download link for the WAV file
        with open(wav_output_path, "rb") as file:
            st.download_button(
                label="Download WAV",
                data=file,
                file_name=os.path.basename(wav_output_path),
                mime="audio/wav"
            )
        
      
else:
        st.error("SoundFont file not found. Please ensure the path is correct.")
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


if midi_output_path is not None:
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    saved_file_path = os.path.join(uploads_dir, midi_output_path.name)
    with open(saved_file_path, 'wb') as f:
        f.write(midi_output_path.getbuffer())

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

files=glob.glob(uploads_dir+"/"+midi_output_path.name.replace(".mid","*.png"))
for file in files:
    st.image(file, caption=file, use_column_width=True)