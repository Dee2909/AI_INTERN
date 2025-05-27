import streamlit as st
import requests
import os

st.title("Morning Market Brief")

# File uploader for voice input
audio_file = st.file_uploader("Upload voice query", type=["wav"])
query = st.text_input("Or enter text query", "What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?")

if st.button("Get Brief"):
    try:
        if audio_file:
            # Save uploaded audio
            with open("query.wav", "wb") as f:
                f.write(audio_file.read())
            response = requests.post("http://localhost:8000/orchestrate", json={"query": "", "audio_path": "query.wav"})
        else:
            response = requests.post("http://localhost:8000/orchestrate", json={"query": query})
        
        # Check response status
        if response.status_code != 200:
            st.error(f"Orchestrator failed with status {response.status_code}: {response.text}")
        else:
            try:
                data = response.json()
                st.write("**Market Brief:**")
                st.write(data["brief"])
            except ValueError as e:
                st.error(f"Failed to parse JSON response: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to orchestrator: {str(e)}")

if __name__ == "__main__":
    st.write("App running on Streamlit")