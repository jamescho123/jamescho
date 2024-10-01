import os
import streamlit as st
import subprocess


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
