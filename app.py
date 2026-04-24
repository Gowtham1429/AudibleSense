import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

# Importing your logic modules
from src.modules.video_processor import extract_audio
from src.modules.subtitle_generator import generate_subtitles
from src.modules.translator import translate_vtt
from src.modules.speech_synthesizer import synthesize_speech
from src.modules.video_processor import extract_audio, merge_audio_video
from src.modules.gender_detector import detect_video_gender
from src.modules.youtube_downloader import download_youtube_video

app = Flask(__name__, 
            template_folder='src/templates', 
            static_folder='src/static')

# Folder configurations
BASE_DATA = 'data'
UPLOAD_FOLDER = 'data/uploads'
AUDIO_FOLDER = 'data/extracted_audio'
SUB_FOLDER = 'data/subtitles/original'
TRANS_FOLDER = 'data/subtitles/translated'
OUTPUT_FOLDER = 'data/audio_output'
FINAL_FOLDER = 'data/final_video'

# Ensure all directories exist
for folder in [UPLOAD_FOLDER, AUDIO_FOLDER, SUB_FOLDER, TRANS_FOLDER, OUTPUT_FOLDER, FINAL_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Helper to serve files from the data folder
@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory(BASE_DATA, filename)

# --- NAVIGATION ---
@app.route('/')
def home(): return render_template('index.html')

@app.route('/module1')
def m1(): 
    return render_template('tasks/module1.html', error=request.args.get('error'))

@app.route('/module2')
def m2(): return render_template('tasks/module2.html')

@app.route('/module3')
def m3(): return render_template('tasks/module3.html')

@app.route('/module4')
def m4(): return render_template('tasks/module4.html')

@app.route('/module5')
def m5(): return render_template('tasks/module5.html')

@app.route('/about')
def about(): return render_template('about.html')

# --- PIPELINE LOGIC ---

@app.route('/run_module1', methods=['POST'])
def run_m1():
    # Clear all pipeline folders to prevent old files from being used
    for folder in [UPLOAD_FOLDER, AUDIO_FOLDER, SUB_FOLDER, TRANS_FOLDER, OUTPUT_FOLDER, FINAL_FOLDER]:
        for fn in os.listdir(folder):
            file_path = os.path.join(folder, fn)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing {file_path}: {e}")

    youtube_url = request.form.get('youtube_url', '').strip()
    video_path = None
    
    if youtube_url:
        # Download from YouTube
        video_path = download_youtube_video(youtube_url, UPLOAD_FOLDER)
        if not video_path:
            return redirect(url_for('m1', error="YouTube Download Failed. Ensure it is a valid, public video URL (or try another video)."))
    else:
        # Standard File Upload
        video = request.files.get('video_file')
        if not video or video.filename == '':
            return redirect(url_for('m1', error="Please provide a valid MP4 file or YouTube link."))
            
        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)
        
    out_name = os.path.splitext(os.path.basename(video_path))[0] + ".wav"
    extract_audio(video_path, os.path.join(AUDIO_FOLDER, out_name))
    
    return redirect(url_for('m2'))

@app.route('/run_module2', methods=['POST'])
def run_m2():
    audio_files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith('.wav')]
    audio_files.sort(key=lambda x: os.path.getmtime(os.path.join(AUDIO_FOLDER, x)), reverse=True)
    
    if not audio_files: return redirect(url_for('m1'))
    
    latest_audio = audio_files[0]
    generate_subtitles(os.path.join(AUDIO_FOLDER, latest_audio), SUB_FOLDER)
    
    vtt_name = os.path.splitext(latest_audio)[0] + ".vtt"
    content = ""
    with open(os.path.join(SUB_FOLDER, vtt_name), 'r', encoding='utf-8') as f:
        content = f.read()
            
    return render_template('tasks/module3.html', transcription=content, current_file=latest_audio)

@app.route('/run_module3', methods=['POST'])
def run_m3():
    target_lang = request.form.get('language', 'hi')
    vtt_files = [f for f in os.listdir(SUB_FOLDER) if f.endswith('.vtt')]
    vtt_files.sort(key=lambda x: os.path.getmtime(os.path.join(SUB_FOLDER, x)), reverse=True)
    
    if not vtt_files: return redirect(url_for('m2'))

    latest_vtt = vtt_files[0]
    translate_vtt(os.path.join(SUB_FOLDER, latest_vtt), TRANS_FOLDER, target_lang)
    
    eng, trans = "", ""
    with open(os.path.join(SUB_FOLDER, latest_vtt), 'r', encoding='utf-8') as f: eng = f.read()
    with open(os.path.join(TRANS_FOLDER, latest_vtt), 'r', encoding='utf-8') as f: trans = f.read()
            
    return render_template('tasks/module4.html', original_text=eng, translated_text=trans, target_lang=target_lang)

@app.route('/run_module4', methods=['POST'])
def run_m4():
    target_lang = request.form.get('target_lang', 'hi')
    gender = request.form.get('gender', 'automatic')
    
    # Get latest original audio to use for gender detection and duration matching
    audio_files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith('.wav')]
    original_audio_path = None
    if audio_files:
        audio_files.sort(key=lambda x: os.path.getmtime(os.path.join(AUDIO_FOLDER, x)), reverse=True)
        original_audio_path = os.path.join(AUDIO_FOLDER, audio_files[0])
        
    pitch_adjustment = "+0Hz"
    if gender == 'automatic':
        if original_audio_path:
            gender, pitch_adjustment = detect_video_gender(original_audio_path)
        else:
            gender = 'female'
            
    vtt_files = [f for f in os.listdir(TRANS_FOLDER) if f.endswith('.vtt')]
    vtt_files.sort(key=lambda x: os.path.getmtime(os.path.join(TRANS_FOLDER, x)), reverse=True)
    
    if not vtt_files: return redirect(url_for('m3'))
    
    latest_vtt = vtt_files[0]
    # Synthesis happens here
    success = synthesize_speech(
        os.path.join(TRANS_FOLDER, latest_vtt), 
        OUTPUT_FOLDER, 
        lang=target_lang, 
        gender=gender, 
        original_audio_path=original_audio_path,
        pitch_shift=pitch_adjustment
    )
    
    last_audio = os.path.splitext(latest_vtt)[0] + ".mp3" if success else ""
    
    eng, trans = "", ""
    with open(os.path.join(SUB_FOLDER, latest_vtt), 'r', encoding='utf-8') as f: eng = f.read()
    with open(os.path.join(TRANS_FOLDER, latest_vtt), 'r', encoding='utf-8') as f: trans = f.read()
            
    import time
    ts = int(time.time())
    return render_template('tasks/module4.html', final_audio=last_audio, original_text=eng, translated_text=trans, ts=ts)

@app.route('/run_module5', methods=['POST'])
def run_m5():
    # Get latest synthesized audio
    audio_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.mp3')]
    audio_files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_FOLDER, x)), reverse=True)
    if not audio_files: return redirect(url_for('m4'))
    latest_audio = audio_files[0]
    
    # Get latest original media
    video_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(('.mp4', '.avi', '.mov', '.mkv', '.MP4', '.mp3', '.wav', '.m4a'))]
    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    if not video_files: return redirect(url_for('m1'))
    latest_video = video_files[0]
    
    audio_path = os.path.join(OUTPUT_FOLDER, latest_audio)
    
    # If the original was just audio, skip merge and just copy the final audio
    if latest_video.lower().endswith(('.mp3', '.wav', '.m4a')):
        out_name = os.path.splitext(latest_video)[0] + "_final.mp3"
        final_path = os.path.join(FINAL_FOLDER, out_name)
        import shutil
        shutil.copy(audio_path, final_path)
    else:
        out_name = os.path.splitext(latest_video)[0] + "_final.mp4"
        video_path = os.path.join(UPLOAD_FOLDER, latest_video)
        final_path = os.path.join(FINAL_FOLDER, out_name)
        merge_audio_video(video_path, audio_path, final_path)
    import time
    ts = int(time.time())
    
    return render_template('tasks/module5.html', final_video=out_name, ts=ts)

if __name__ == '__main__':
    app.run(debug=True)