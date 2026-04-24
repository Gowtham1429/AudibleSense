import os
import argparse
import time

# Import project modules
from src.modules.video_processor import extract_audio, merge_audio_video
from src.modules.subtitle_generator import generate_subtitles
from src.modules.translator import translate_vtt
from src.modules.speech_synthesizer import synthesize_speech
from src.modules.gender_detector import detect_video_gender
from src.modules.youtube_downloader import download_youtube_video

def main():
    parser = argparse.ArgumentParser(description="Full Pipeline: Extract audio from video, translate it, and attach back to the video.")
    parser.add_argument("video_file", help="Path to the original video file (e.g., video.mp4)")
    parser.add_argument("--lang", default="hi", help="Target language code (e.g., 'hi' for Hindi, 'es' for Spanish, 'fr' for French)")
    parser.add_argument("--gender", default="automatic", help="Voice gender ('automatic', 'male' or 'female')")
    parser.add_argument("--output_dir", default="pipeline_output", help="Directory to store intermediate and final files")
    
    args = parser.parse_args()
    
    video_path = args.video_file
    target_lang = args.lang
    gender = args.gender
    base_out = args.output_dir
    
    if video_path.startswith("http://") or video_path.startswith("https://"):
        print(f"\n--- STEP 0: Downloading YouTube Video ---")
        os.makedirs(base_out, exist_ok=True) # Ensure it exists
        downloaded = download_youtube_video(video_path, base_out)
        if not downloaded:
            return print("Error downloading YouTube video.")
        video_path = downloaded
        print(f"Downloaded to: {video_path}")
    elif not os.path.exists(video_path):
        print(f"Error: The video file '{video_path}' does not exist.")
        return

    # Create directories for intermediate steps
    audio_dir = os.path.join(base_out, "1_extracted_audio")
    sub_dir = os.path.join(base_out, "2_original_subtitles")
    trans_dir = os.path.join(base_out, "3_translated_subtitles")
    synth_dir = os.path.join(base_out, "4_synthesized_audio")
    final_dir = os.path.join(base_out, "5_final_video")
    
    for d in [audio_dir, sub_dir, trans_dir, synth_dir, final_dir]:
        os.makedirs(d, exist_ok=True)
        
    print("\n" + "="*50)
    print("STARTING FULL AUDIO TRANSLATION PIPELINE")
    print("="*50)
    
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # 1. Extract audio from video
    print("\n--- STEP 1: Extracting Audio from Video ---")
    audio_path = os.path.join(audio_dir, f"{base_name}.wav")
    success = extract_audio(video_path, audio_path)
    if not success:
        return print("Pipeline terminated at Step 1.")

    # 2. Translating the audio to comfortable audio
    # 2a. ASR (Speech to Text)
    print("\n--- STEP 2a: Generating Subtitles (ASR) ---")
    success = generate_subtitles(audio_path, sub_dir, model_size="base")
    vtt_path = os.path.join(sub_dir, f"{base_name}.vtt")
    if not success or not os.path.exists(vtt_path):
        return print("Pipeline terminated at Step 2a.")
        
    # 2b. Translate the VTT
    print(f"\n--- STEP 2b: Translating Text to '{target_lang}' ---")
    success = translate_vtt(vtt_path, trans_dir, target_lang=target_lang)
    trans_vtt_path = os.path.join(trans_dir, f"{base_name}.vtt")
    if not success or not os.path.exists(trans_vtt_path):
        return print("Pipeline terminated at Step 2b.")
        
    pitch_adjustment = "+0Hz"
    # 2c. Synthesize Translated Audio (Text to Speech)
    if gender == 'automatic':
        print("\n--- STEP 2c (Pre): Automatically detecting gender and pitch from original audio ---")
        gender, pitch_adjustment = detect_video_gender(audio_path)
        
    print(f"\n--- STEP 2c: Synthesizing Translated Audio as {gender.upper()} (Pitch Shift: {pitch_adjustment}) ---")
    success = synthesize_speech(trans_vtt_path, synth_dir, lang=target_lang, gender=gender, original_audio_path=audio_path, pitch_shift=pitch_adjustment)
    synth_audio_path = os.path.join(synth_dir, f"{base_name}.mp3")
    if not success or not os.path.exists(synth_audio_path):
        return print("Pipeline terminated at Step 2c.")
        
    # 3. Attach the audio to the original video
    print("\n--- STEP 3: Attaching Translated Audio to Original Video ---")
    final_video_path = os.path.join(final_dir, f"{base_name}_{target_lang}.mp4")
    success = merge_audio_video(video_path, synth_audio_path, final_video_path)
    if not success:
        return print("Pipeline terminated at Step 3.")
        
    print("\n" + "="*50)
    print(f"PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Your final video with '{target_lang}' audio is at:")
    print(final_video_path)
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
