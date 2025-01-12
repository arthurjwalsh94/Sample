import os
import sys
import librosa
import numpy as np

# Major/Minor templates (Krumhansl or Temperley-like profiles)
# These are simplified example values.
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 
                          4.09, 2.52, 6.59, 5.19, 2.39, 
                          3.66, 2.29])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 
                          3.53, 2.54, 4.75, 3.98, 2.69, 
                          3.34, 3.17])

# Pitch class names in order: C, C#, D, D#, E, 
#                             F, F#, G, G#, A, A#, B
PITCH_CLASSES = ["C", "C#", "D", "D#", "E", 
                 "F", "F#", "G", "G#", "A", "A#", "B"]

def estimate_bpm(y, sr):
    """Use librosa's beat_track to estimate BPM from the percussive component."""
    # Separate harmonic/percussive
    _, y_percussive = librosa.effects.hpss(y)
    # Estimate tempo
    tempo, _ = librosa.beat.beat_track(y=y_percussive, sr=sr)
    
    # In case tempo is returned as a numpy array, extract the first element
    # and convert to float before rounding
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]
    return round(float(tempo))

def estimate_key_advanced(y, sr):
    """
    Estimate the musical key (major or minor) by:
      1) Separating harmonic from percussive audio.
      2) Computing chroma from the harmonic portion.
      3) Shifting the chroma and matching against major/minor templates 
         to find the best key fit.
    """
    # 1) Harmonic-percussive separation
    y_harmonic, _ = librosa.effects.hpss(y)

    # 2) Compute chroma from the harmonic signal
    chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
    chroma_avg = np.mean(chroma, axis=1)  # shape: (12,)

    best_score = float("-inf")
    best_key = None

    # 3) Try all 12 possible rotations (each pitch as "C") for major/minor
    for semitone_shift in range(12):
        rotated = np.roll(chroma_avg, -semitone_shift)

        major_score = np.dot(rotated, MAJOR_PROFILE)
        minor_score = np.dot(rotated, MINOR_PROFILE)

        if major_score > minor_score:
            if major_score > best_score:
                best_score = major_score
                note_name = PITCH_CLASSES[semitone_shift]
                best_key = f"{note_name} major"
        else:
            if minor_score > best_score:
                best_score = minor_score
                note_name = PITCH_CLASSES[semitone_shift]
                best_key = f"{note_name} minor"

    return best_key

def detect_key_bpm(file_path):
    """Load audio, estimate BPM, estimate key."""
    y, sr = librosa.load(file_path)
    bpm = estimate_bpm(y, sr)
    key = estimate_key_advanced(y, sr)
    return bpm, key

def label_files_with_key_bpm(input_folder):
    """
    For each .mp3 or .wav in 'input_folder':
    1) Detect key & BPM
    2) Rename the file:
       'MySong_bass.mp3' -> 'MySong_120BPM_G# major_bass.mp3'
    """
    valid_exts = (".mp3", ".wav")
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(valid_exts)]
    if not files:
        print(f"⚠️ No .mp3/.wav files found in '{input_folder}'")
        return

    for old_name in files:
        old_path = os.path.join(input_folder, old_name)
        bpm, key = detect_key_bpm(old_path)

        base, ext = os.path.splitext(old_name)  # e.g. "MySong_bass", ".mp3"
        parts = base.rsplit("_", 1)
        if len(parts) == 2:
            # e.g. "MySong", "bass"
            stem_name, instrument = parts
            # Insert BPM/Key between them
            new_base = f"{stem_name}_{bpm}BPM_{key}_{instrument}"
        else:
            # No underscore => just append
            new_base = f"{base}_{bpm}BPM_{key}"

        new_name = f"{new_base}{ext}"  # keep the original extension (.mp3 or .wav)
        new_path = os.path.join(input_folder, new_name)
        os.rename(old_path, new_path)
        print(f"✅ Renamed: {old_name} -> {new_name}")

def main():
    """
    Usage:
        python AdvancedKeyDetector.py [input_folder]

    If no input_folder is provided, defaults to 'Data'.

    This script:
      - For each .mp3/.wav file in [input_folder],
        - estimates BPM from the percussive signal
        - estimates key (major/minor) from the harmonic signal
        - renames the file to include BPM & key in the filename
    """
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
    else:
        input_folder = "Data"

    if not os.path.isdir(input_folder):
        print(f"❌ '{input_folder}' not found.")
        sys.exit(1)

    label_files_with_key_bpm(input_folder)

if __name__ == "__main__":
    main()