import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from google.cloud import pubsub_v1
import json
from mutagen.mp3 import MP3
import tempfile
from pydub import AudioSegment
from io import BytesIO
import random

# Initialize clients
storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()

def hello_gcs(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    # Extract metadata from the event
    project_id = "sandydev"
    topic_name = "audio_msg" 
    audio_path = 'gs://{}/{}'.format(file['bucket'], file['name'])
    read_file = storage_client.bucket(file['bucket']).get_blob(file['name'])

    def mp3_to_linear16(mp3_data):
        # Convert MP3 data to Linear16 format using pydub
        audio = AudioSegment.from_mp3(BytesIO(mp3_data))
        linear16_audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        return linear16_audio.raw_data

    def mp3_to_text(mp3_data):
        # Initialize the Speech-to-Text client
        speech_client = speech.SpeechClient()

        # Convert MP3 data to Linear16 format
        linear16_audio = mp3_to_linear16(mp3_data)

        # Create the audio object
        audio = speech.RecognitionAudio(content=linear16_audio)

        # Set up the recognition configuration
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",  # Use "en-IN" for Indian English
            enable_automatic_punctuation=True,
            use_enhanced=True,
            speech_contexts=[
                {
                    "phrases": ["9438277391", "$FULLPHONENUM"],
                    "boost": 10.0,
                }
            ],
        )

        # Perform long-running recognition
        operation = speech_client.long_running_recognize(config=config, audio=audio)

        # Wait for the operation to complete and get the final recognition response
        response = operation.result()

        # Extract and return the transcribed text
        text_output = ""
        for result in response.results:
            text_output += result.alternatives[0].transcript

        return text_output

    # Helper function to get audio metadata
    def get_audio_metadata(path):
        import random
        # Download the audio file to a temporary location
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
            read_file.download_to_filename(temp_file.name)

            # Use mutagen to extract MP3 metadata
            audio = MP3(temp_file.name)
            duration = audio.info.length  # Duration in seconds

        return {'duration': duration}

    # Check if the uploaded file is an MP3 file
    if not file['name'].lower().endswith(".mp3"):
        print(f"Skipping non-MP3 file: {file['name']}.")
        return

    # Process audio and publish message to Pub/Sub
    metadata = get_audio_metadata(audio_path)

    # Convert MP3 to text
    text = mp3_to_text(read_file.download_as_bytes())
    random_number = str(random.randint(100, 999))


    # Create the Pub/Sub message
    pubsub_obj = {
        'audio_file_name':'dev' + random_number,
        'text': text,
        'duration': metadata['duration']
    }

    # Publish the message to Pub/Sub
    topic_path = publisher.topic_path(project_id, topic_name)
    message_data = json.dumps(pubsub_obj).encode('utf-8')
    future = publisher.publish(topic_path, data=message_data)
    print(f"Message {future.result()} published.")
