import whisper
from whisper.utils import get_writer
import os

def generate_subtitles(audio_path, output_dir, model_size="base"):
    """
    Transcribes audio using Whisper and saves it as a WebVTT file.
    """
    try:
        # Load the Whisper model (base is good for testing speed/accuracy)
        model = whisper.load_model(model_size)
        
        # Transcribe the audio
        print(f"Transcribing {os.path.basename(audio_path)}...")
        result = model.transcribe(audio_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Use Whisper's built-in writer for WebVTT format
        vtt_writer = get_writer("vtt", output_dir)
        vtt_writer(result, audio_path)
        
        return True
    except Exception as e:
        print(f"Transcription Error: {e}")
        return False