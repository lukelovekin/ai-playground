# Step 1
# pip3 install virtualenv 
# virtualenv my_env # create a virtual environment my_env
# source my_env/bin/activate # activate my_env

# # installing required libraries in my_env
# pip install --force-reinstall "setuptools<70" transformers==4.36.0 torch==2.1.1 gradio==5.23.2 langchain==0.0.343 ibm_watson_machine_learning==1.0.335 huggingface-hub==0.28.1

# sudo apt update

# sudo apt install ffmpeg -y

# Step 2
# import requests

# # URL of the audio file to be downloaded
# url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-GPXX04C6EN/Testing%20speech%20to%20text.mp3"

# # Send a GET request to the URL to download the file
# response = requests.get(url)

# # Define the local file path where the audio file will be saved
# audio_file_path = "downloaded_audio.mp3"

# # Check if the request was successful (status code 200)
# if response.status_code == 200:
#     # If successful, write the content to the specified local file path
#     with open(audio_file_path, "wb") as file:
#         file.write(response.content)
#     print("File downloaded successfully")
# else:
#     # If the request failed, print an error message
#     print("Failed to download the file")

# python3 simple_speech2text.py




# Step 3

import torch
from transformers import pipeline

# Initialize the speech-to-text pipeline from Hugging Face Transformers
# This uses the "openai/whisper-tiny.en" model for automatic speech recognition (ASR)
# The `chunk_length_s` parameter specifies the chunk length in seconds for processing
pipe = pipeline(
  "automatic-speech-recognition",
  model="openai/whisper-tiny.en",
  chunk_length_s=30,
)

# Define the path to the audio file that needs to be transcribed
sample = 'downloaded_audio.mp3'

# Perform speech recognition on the audio file
# The `batch_size=8` parameter indicates how many chunks are processed at a time
# The result is stored in `prediction` with the key "text" containing the transcribed text
prediction = pipe(sample, batch_size=8)["text"]

# Print the transcribed text to the console
print(prediction)
