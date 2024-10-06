import os
import streamlit as st
import music21 as m21
import librosa
import pretty_midi
import numpy as np
from io import BytesIO
import openai
import subprocess
import glob

# Constants
UPLOAD_DIR = "uploaded_files"
SOUNDFONT_PATH = r"C:\fluid\FluidR3_GM\FluidR3_GM.sf2"
MUSESCORE_PATH = r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe'

# Initialize OpenAI client
client = openai.OpenAI(api_key=st.secrets.OpenAI_key)

# Function definitions
def create_accompaniment(musicxml_content, style):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Create an accompaniment in {style} style for the following melody entirely in MusicXML format. Provide only the complete MusicXML content and also part and measures in this format ""!--========================= Measure  ==========================-->, without any additional text, comments, or markup. Do not include XML tags or any other formatting such as '''. and end with </score-partwise>, The response should be ready to be parsed as valid MusicXML:\n\n{musicxml_content}"}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()

def wav_to_midi_librosa(wav_file):
    y, sr = librosa.load(wav_file, sr=None)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)
    time_per_frame = librosa.frames_to_time(np.arange(pitches.shape[1]), sr=sr)
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            midi_note = pretty_midi.hz_to_note_number(pitch)
            note = pretty_midi.Note(
                velocity=100,
                pitch=int(midi_note),
                start=time_per_frame[t],
                end=time_per_frame[t] + 0.1
            )
            instrument.notes.append(note)
    midi.instruments.append(instrument)
    midi_io = BytesIO()
    midi.write(midi_io)
    midi_io.seek(0)
    return midi_io

def process_midi_file(midi_file_path, style):
    try:
        score = m21.converter.parse(midi_file_path)
        st.write("MIDI file has been processed.")
        musicxml_output_path = midi_file_path.rsplit('.', 1)[0] + '.musicxml'
        score.write('musicxml', fp=musicxml_output_path)
        st.write(f"Converted MIDI to MusicXML: {musicxml_output_path}")
        with open(musicxml_output_path, 'r') as file_object:
            musicxml_content = file_object.read()
        with st.expander("MusicXML of the uploaded file"):
            st.code(musicxml_content, language='xml')
        
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            accompaniment_musicxml = create_accompaniment(musicxml_content, style)
            st.write("Accompaniment created.")
            accompaniment_output_path = midi_file_path.rsplit('.', 1)[0] + '_accompaniment.musicxml'
            with open(accompaniment_output_path, 'w') as file_object:
                file_object.write(accompaniment_musicxml)
            st.write(f"Accompaniment MusicXML saved at: {accompaniment_output_path}")
            
            try:
                # Try to parse the generated MusicXML
                accompaniment_score = m21.converter.parse(accompaniment_output_path)
                # If parsing succeeds, break the loop
                break
            except Exception as e:
                st.warning(f"Failed to parse generated MusicXML (Attempt {attempts + 1}/{max_attempts}): {e}")
                attempts += 1
                if attempts == max_attempts:
                    st.error("Failed to generate valid MusicXML after multiple attempts. Please try again.")
                    return None
        
        with st.expander("MusicXML of the generated accompaniment"):
            st.code(accompaniment_musicxml, language='xml')
        with open(accompaniment_output_path, 'rb') as file:
            st.download_button(
                label="Download Accompaniment MusicXML",
                data=file,
                file_name=os.path.basename(accompaniment_output_path),
                mime="application/xml"
            )
        return accompaniment_output_path
    except Exception as e:
        st.error(f"An error occurred while processing the MIDI file: {e}")
        return None

def generate_sheet_image(midi_output_path):
    midi_output_path = os.path.abspath(midi_output_path)
    output_image_path = midi_output_path.rsplit('.', 1)[0] + '.png'
    result = subprocess.run(
        [MUSESCORE_PATH, midi_output_path, '-o', output_image_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:  
        st.error(f"MuseScore error: {result.stderr}")
    else:
        st.success("MuseScore ran successfully.")
    st.write(output_image_path)
    return output_image_path

# Streamlit UI
st.title("Chord-sync")
st.subheader("Welcome to a free piano accompaniment website")

st.markdown("""
## Instructions:
1. **Upload a file**: Use the file uploader below to upload a MIDI or WAV file of your melody.
2. **Select a style**: Enter the style of accompaniment you'd like (e.g., "jazz", "classical", "pop").
3. **Process the file**: The app will convert your file to MIDI if necessary and create an accompaniment.
4. **Download results**: You can download the generated MIDI, WAV, and sheet music files.
5. **View sheet music**: The generated sheet music will be displayed at the bottom of the page.

**Note**: If you've previously uploaded files, you can select them from the list below instead of uploading a new file.
""")

st.markdown("---")

# File selection
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
existing_files = os.listdir(UPLOAD_DIR)
selected_files = st.multiselect(
    'Select a file:',
    existing_files,
    help='Choose a file from the list',
    max_selections=1
)

if selected_files:
    selected_file = selected_files[0]
    st.write('You selected:', selected_file)
    file_path = os.path.join(UPLOAD_DIR, selected_file)
    if os.path.exists(file_path):
        st.write("Proceed with the selected file as an audio or MIDI file:")
        try:
            if selected_file.lower().endswith(('wav', 'mp3', 'mp4', 'mid')):
                st.audio(file_path, format="audio/mpeg")
                st.write("Audio or MIDI file accepted.")
                with open(file_path, "rb") as file:
                    audio = file.read()
            else:
                st.write("Please select an audio or MIDI file")
        except Exception as e:
            st.write(f"Error processing the selected file: {str(e)}")
else:
    st.write("No file selected.")

# File upload and processing
audio = st.file_uploader("Please upload a MIDI or WAV file", type=["WAV", "MID"])
style = st.text_input("Write the style of the accompaniment")
if style:
    st.write(f"Selected style: {style}")

if audio is not None:
    st.audio(audio)
    st.write(f"Uploaded file: {audio.name}")
    saved_file_path = os.path.join("uploads", audio.name)
    os.makedirs(os.path.dirname(saved_file_path), exist_ok=True)
    with open(saved_file_path, 'wb') as f:
        f.write(audio.getbuffer())
    st.write(f"File saved at: {saved_file_path}")

    if saved_file_path.lower().endswith('.mid'):
        st.write("MIDI file detected. Processing as MIDI...")
        existing_file_path = process_midi_file(saved_file_path, style)
    elif saved_file_path.lower().endswith('.wav'):
        st.write("WAV file detected. Converting to MIDI...")
        midi_io = wav_to_midi_librosa(saved_file_path)
        midi_output_path = saved_file_path.rsplit('.', 1)[0] + ".mid"
        with open(midi_output_path, 'wb') as f:
            f.write(midi_io.getbuffer())
        st.write(f"Converted WAV to MIDI: {midi_output_path}")
        existing_file_path = process_midi_file(midi_output_path, style)

    if existing_file_path:
        st.write(f"Using existing file: {existing_file_path}")
        try:
            score = m21.converter.parse(existing_file_path)
            st.write("MusicXML file has been processed.")
            midi_output_path = existing_file_path.replace('.musicxml', '.mid').replace('.xml', '.mid')
            score.write('midi', fp=midi_output_path)
            st.write(f"Converted MusicXML to MIDI: {midi_output_path}")
        except Exception as e:
            st.error(f"Failed to convert MusicXML to MIDI: {e}")
            st.write("Attempting to regenerate MusicXML...")
            existing_file_path = process_midi_file(midi_file_path, style)
            if existing_file_path:
                score = m21.converter.parse(existing_file_path)
                midi_output_path = existing_file_path.replace('.musicxml', '.mid').replace('.xml', '.mid')
                score.write('midi', fp=midi_output_path)
                st.write(f"Regenerated and converted MusicXML to MIDI: {midi_output_path}")
            else:
                st.error("Failed to regenerate valid MusicXML. Please try again with a different file or style.")
           

        # Continue with the rest of the processing...
        with open(midi_output_path, 'rb') as file:
            st.download_button(
                label="Download MIDI",
                data=file,
                file_name=os.path.basename(midi_output_path),
                mime='audio/midi'
            )
        score = m21.converter.parse(midi_output_path)
        st.write("MIDI file has been processed.")
        st.write(midi_output_path)
        st.audio(midi_output_path, format="audio/mid")

        if os.path.exists(SOUNDFONT_PATH):
            wav_output_path = midi_output_path.replace(".mid", ".wav").replace(".midi", ".wav")
            st.write("MIDI Path:", midi_output_path)
            st.write("WAV Path:", wav_output_path)
            cmd = ['fluidsynth', '-ni', SOUNDFONT_PATH, midi_output_path, '-F', wav_output_path]
            try:
                subprocess.run(cmd, check=True)
                st.write(f"Conversion successful! WAV file saved to {wav_output_path}")
                with open(wav_output_path, "rb") as file:
                    st.download_button(
                        label="Download WAV",
                        data=file,
                        file_name=os.path.basename(wav_output_path),
                        mime="audio/wav"
                    )
                st.audio(wav_output_path, format="audio/wav")
            except subprocess.CalledProcessError as e:
                st.write(f"Error during conversion: {e}")
        else:
            st.error("SoundFont file not found. Please ensure the path is correct.")

        sheet_image_path = generate_sheet_image(midi_output_path)
        if sheet_image_path and os.path.exists(sheet_image_path):
            sheet_image_path = sheet_image_path.replace("C:\\Users\hp\Documents\GitHub\jamescho\\uploads\\", "/uploads/")
            st.image(sheet_image_path, caption='Generated Sheet Music', use_column_width=True)
            st.write(f"Image can be accessed at: {sheet_image_path}")

        uploads_dir = "uploads"
        files = glob.glob(os.path.join(uploads_dir, os.path.basename(midi_output_path).replace(".mid", "*.png")))
        for file in files:
            st.image(file, caption=file, use_column_width=True)
    else:
        st.error("Failed to process the uploaded file. Please try again with a different file.")
else:
    st.info("Please upload a file to proceed.")