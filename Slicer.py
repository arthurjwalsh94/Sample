import os
import madmom
import numpy as np
from madmom.audio import Signal
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
import soundfile as sf

# 🎧 Paths Configuration (absolute paths)
DATA_DIR = "/Users/arthurwalsh/Desktop/Sample/Data"    # Input audio folder
OUTPUT_DIR = "/Users/arthurwalsh/Desktop/Sample/Output"  # Folder for sliced audio files
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure Output folder exists

def slice_audio_by_8bars(audio_file):
    print(f"🎧 Processing: {audio_file}")
    
    # Load Audio
    signal = Signal(audio_file, sample_rate=44100)
    print(f"✅ Loaded Audio Signal: {len(signal)} samples")
    
    # Detect Beats
    beat_processor = RNNBeatProcessor()
    beat_activation = beat_processor(audio_file)
    
    beat_tracker = DBNBeatTrackingProcessor(beats_per_bar=[4], fps=100)
    beats = beat_tracker(beat_activation)
    print(f"✅ Detected Beats: {len(beats)}")
    
    # Ensure there are enough beats for slicing (needs at least 32 beats)
    if len(beats) < 32:
        print("⚠️ Not enough beats detected for an 8-bar slice. Skipping file.")
        return
    
    # Slice Audio Based on 8-Bar Segments (32 beats per slice)
    beats_per_segment = 32  # 8 bars × 4 beats per bar
    num_segments = len(beats) // beats_per_segment
    
    for i in range(num_segments):
        start_time = beats[i * beats_per_segment]
        if (i + 1) * beats_per_segment < len(beats):
            end_time = beats[(i + 1) * beats_per_segment]
        else:
            end_time = beats[-1]
        
        start_sample = int(start_time * 44100)  # Convert time to sample index
        end_sample = int(end_time * 44100)
        
        slice_audio = signal[start_sample:end_sample]
        output_filename = os.path.join(
            OUTPUT_DIR,
            f"{os.path.splitext(os.path.basename(audio_file))[0]}_8bar_segment_{i + 1}.wav"
        )
        sf.write(output_filename, slice_audio, 44100)
        print(f"✅ Saved 8-bar slice: {output_filename}")
    
    print("🎉 All 8-bar slices saved successfully!")

# 🥁 Process Each .wav File in Data Directory
if __name__ == "__main__":
    for file in os.listdir(DATA_DIR):
        if file.lower().endswith(".wav"):
            audio_path = os.path.join(DATA_DIR, file)
            slice_audio_by_8bars(audio_path)
    
    print("🎧 All files in 'Data' have been processed and sliced into 8-bar segments successfully!")