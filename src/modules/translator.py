import os
from deep_translator import GoogleTranslator

def translate_vtt(input_path, output_folder, target_lang='hi'):
    """
    Translates only the text content of a VTT file, preserving timestamps.
    """
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return False

    translator = GoogleTranslator(source='auto', target=target_lang)
    translated_lines = []

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            stripped = line.strip()
            
            # Keep WEBVTT header, timestamps, and empty lines as they are
            if stripped == "WEBVTT" or "-->" in stripped or not stripped:
                translated_lines.append(line)
            else:
                # This is actual dialogue - Translate it!
                translation = translator.translate(stripped)
                translated_lines.append(translation + "\n")

        # Save the translated file with the same name in the translated folder
        output_path = os.path.join(output_folder, os.path.basename(input_path))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)
            
        print(f"Successfully translated {os.path.basename(input_path)} to {target_lang}")
        return True

    except Exception as e:
        print(f"Translation Error: {e}")
        return False