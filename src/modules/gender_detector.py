import librosa
import numpy as np
import os

def detect_video_gender(audio_path):
    """
    Analyzes the `.wav` audio file using mathematical pitch (fundamental frequency f0).
    Returns (gender, pitch_shift_str) where pitch_shift_str is something like '+10Hz' or '-15Hz'.
    """
    if not os.path.exists(audio_path):
        print(f"Error: {audio_path} not found for auto-gender detection.")
        return 'female', '+0Hz' # Fallback
        
    try:
        print(f"Automatically analyzing gender pitch from: {os.path.basename(audio_path)}")
        # Load audio (downsample to 16kHz for fast processing)
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Calculate pitch/fundamental frequency using librosa.pyin
        f0, voiced_flag, voiced_probs = librosa.pyin(y, 
                                                    fmin=librosa.note_to_hz('C2'), 
                                                    fmax=librosa.note_to_hz('C6'))
        
        # Filter strictly for times where a voice is actually speaking
        valid_f0 = f0[voiced_flag]
        
        # If no voice is found in the whole video somehow
        if len(valid_f0) == 0:
            print("Could not detect enough clear vocal frames. Defaulting to female.")
            return 'female', '+0Hz'
            
        # Get the median pitch frequency
        median_f0 = np.nanmedian(valid_f0)
        print(f"Calculated Median Pitch Frequency: {median_f0:.1f} Hz")
        
        # Threshold: ~165 Hz separates typical male vs female vocal pitches
        if median_f0 < 165:
            print("Auto-detected gender: MALE")
            gender = 'male'
            baseline = 120 # Generic Male AI pitch is usually around 120Hz
        else:
            print("Auto-detected gender: FEMALE")
            gender = 'female'
            baseline = 210 # Generic Female AI pitch is usually around 210Hz
            
        # Calculate pitch shift needed to perfectly mimic the human!
        diff_hz = int(median_f0 - baseline)
        pitch_shift = f"{diff_hz:+d}Hz" 
        print(f"Calculated AI Pitch Shift adjustment: {pitch_shift}")
            
        return gender, pitch_shift
            
    except Exception as e:
        print(f"Gender Detection Error: {e}")
        return 'female', '+0Hz'
