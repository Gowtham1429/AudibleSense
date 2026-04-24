import os
import asyncio
import edge_tts
import webvtt
from pydub import AudioSegment

async def get_voice(lang, gender):
    """Dynamically finds the best edge-tts voice for a given language code and gender."""
    try:
        voices = await edge_tts.list_voices()
        
        # 1. Try to find exact language and gender (e.g. 'hi' -> starts with 'hi-', gender 'female')
        for v in voices:
            if v['Locale'].lower().startswith(lang.lower() + '-') and v['Gender'].lower() == gender.lower():
                return v['Name']
                
        # 2. Fallback to this language but any gender
        for v in voices:
            if v['Locale'].lower().startswith(lang.lower() + '-'):
                return v['Name']
                
    except Exception as e:
        print(f"Error fetching voice list: {e}")
        
    # 3. Ultimate Fallback
    return 'en-US-AriaNeural'

async def generate_audio(text, lang, gender, output_path, pitch="+0Hz"):
    voice = await get_voice(lang, gender)
    print(f"Using voice: {voice} for ({lang}, {gender}) with Pitch {pitch}")
    communicate = edge_tts.Communicate(text, voice, rate="+0%", pitch=pitch)
    await communicate.save(output_path)

def synthesize_speech(vtt_path, output_folder, lang='hi', gender='female', original_audio_path=None, pitch_shift="+0Hz"):
    """
    Extracts text from VTT with exact timestamps overlaying it onto a silent
    audio canvas using pydub and edge-tts, preserving the original timing natively.
    """
    if not os.path.exists(vtt_path):
        print(f"Error: {vtt_path} not found.")
        return False

    try:
        # Load VTT file
        vtt = webvtt.read(vtt_path)
        
        if not vtt:
            print("No subtitles found.")
            return False
            
        # Create a base silent canvas exactly matching the original video duration
        # This prevents the audio from naturally clipping off early if the final words
        # are spoken before the actual video ends.
        if original_audio_path and os.path.exists(original_audio_path):
            original = AudioSegment.from_file(original_audio_path)
            base_audio = AudioSegment.silent(duration=len(original))
            print(f"Set Base Canvas Duration to original length: {len(original)} ms")
        else:
            base_audio = AudioSegment.silent(duration=0)
            
        temp_out = os.path.join(output_folder, "temp_chunk.mp3")
        
        for caption in vtt:
            txt = caption.text.strip()
            # Whisper sometimes creates multi-line captions or empty ones
            txt = txt.replace('\n', ' ')
            if not txt:
                continue
                
            # Convert VTT start string to milliseconds
            start_parts = caption.start.split(':')
            start_s = float(start_parts[0])*3600 + float(start_parts[1])*60 + float(start_parts[2])
            start_ms = int(start_s * 1000)
            
            # Synthesize this specific time chunk
            print(f"Synthesizing: [{caption.start}] {txt[:30]}... (Pitch {pitch_shift})")
            asyncio.run(generate_audio(txt, lang, gender, temp_out, pitch=pitch_shift))
            
            if os.path.exists(temp_out):
                snippet = AudioSegment.from_file(temp_out)
                
                # Expand base canvas if snippet + offset goes past end of current base canvas
                required_len = start_ms + len(snippet)
                if len(base_audio) < required_len:
                    padding_needed = required_len - len(base_audio)
                    # Add exact silence needed
                    base_audio += AudioSegment.silent(duration=padding_needed)
                
                # Overlay at the exact millisecond offset
                base_audio = base_audio.overlay(snippet, position=start_ms)
                os.remove(temp_out)
                
        # Export final
        filename = os.path.splitext(os.path.basename(vtt_path))[0] + ".mp3"
        output_path = os.path.join(output_folder, filename)
        
        base_audio.export(output_path, format="mp3")
        print(f"Synthesized synced audio saved to: {output_path}")
        return True

    except Exception as e:
        print(f"Synthesis Error: {e}")
        return False