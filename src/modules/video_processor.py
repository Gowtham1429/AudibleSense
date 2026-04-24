import ffmpeg
import os

def extract_audio(video_input_path, audio_output_path):
    """
    Extracts the audio stream from a video file and saves it as a WAV file.
    """
    try:
        # Check if output directory exists
        os.makedirs(os.path.dirname(audio_output_path), exist_ok=True)
        
        # FFmpeg command: -vn (no video), -acodec pcm_s16le (standard WAV)
        stream = ffmpeg.input(video_input_path)
        stream = ffmpeg.output(stream, audio_output_path, vn=None, acodec='pcm_s16le', ar='16000')
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        print(f"Successfully extracted: {os.path.basename(audio_output_path)}")
        return True
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
        return False

def merge_audio_video(video_path, audio_path, output_video_path):
    """
    Replaces the audio of a video with a new audio file.
    """
    try:
        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
        
        # Load video and audio streams
        video_stream = ffmpeg.input(video_path)
        audio_stream = ffmpeg.input(audio_path)
        
        # Merge streams - taking video from video_stream and audio from audio_stream
        stream = ffmpeg.output(video_stream.video, audio_stream.audio, output_video_path, vcodec='copy', acodec='aac', strict='experimental')
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        print(f"Successfully merged. Saved to: {output_video_path}")
        return True
    except ffmpeg.Error as e:
        print(f"FFmpeg Merge Error: {e.stderr.decode('utf8') if e.stderr else e}")
        return False