import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
st.write("Hello World")
st.title("AI piano accompaniment")
st.subheader("HI")

st.title("Uploading Files")
st.markdown("---")
audio=st.file_uploader("Please upload an audio or MIDI file",type=["WAV","MP3","MP4","MID"])
if audio is not None:
    st.audio(audio)
st.slider("This is a slider")

import os
from openai import OpenAI

client = OpenAI(
    api_key=st.secrets.OpenAI_key
)

prompt=st.text_input("what do you want to ask?")
def search_word_information(word):
    prompt = word

    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
 
    )
    generated_text = response.choices[0].text
    return generated_text

if len(prompt)>5:
    st.text(search_word_information(prompt))




