import os
import sys
import numpy as np
import soundfile as sf
from madmom.audio import Signal
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor

def slice_4bars(file_path, out_folder):
    """
    Loads audio from 'file_path', slices it into 4-bar segments (16 beats each),
    and writes each slice as a .wav file into 'out_folder'.
    """
    print(f"🎧 Processing 4-bar slices for: {file_path}")
    
    # Load audio at 44,100 Hz
    signal = Signal(file_path, sample_rate=44100)
    print(f"   ✅ Loaded Audio Signal: {len(signal)} samples")
    
    # Detect Beats
    beat_processor = RNNBeatProcessor()
    beat_activation = beat_processor(file_path)
    beat_tracker = DBNBeatTrackingProcessor(beats_per_bar=[4], fps=100)
    beats = beat_tracker(beat_activation)
    print(f"   ✅ Detected Beats: {len(beats)}")
    
    # Need at least 16 beats for one 4-bar slice
    if len(beats) < 16:
        print("   ⚠️ Not enough beats for a 4-bar slice. Skipping file.")
        return

    beats_per_segment = 16  # 4 bars * 4 beats per bar
    num_segments = len(beats) // beats_per_segment

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    for i in range(num_segments):
        start_beat_index = i * beats_per_segment
        end_beat_index = (i + 1) * beats_per_segment
        start_time = beats[start_beat_index]
        end_time = beats[end_beat_index] if end_beat_index < len(beats) else beats[-1]
        
        start_sample = int(start_time * 44100)
        end_sample = int(end_time * 44100)
        slice_audio = signal[start_sample:end_sample]

        out_filename = f"{base_name}_4bar_segment_{i + 1}.wav"
        out_path = os.path.join(out_folder, out_filename)
        sf.write(out_path, slice_audio, 44100)
        print(f"   ✅ Saved 4-bar slice: {out_path}")

    print("   🎉 Finished slicing.\n")

def main():
    """
    Usage:
        python Slicer4Bar.py [input_folder]

    If [input_folder] is not provided, it defaults to 'Data'.

    This script:
      - Scans [input_folder] for .wav and .mp3 files.
      - Slices each song into 4-bar segments (16 beats per segment).
      - Saves the slices into 'Output/Slices'.
    """
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "Data"

    if not os.path.isdir(input_dir):
        print(f"❌ Error: Input folder '{input_dir}' not found.")
        sys.exit(1)

    # Accept both .wav and .mp3 files
    audio_files = [f for f in os.listdir(input_dir) if f.lower().endswith((".wav", ".mp3"))]
    if not audio_files:
        print(f"⚠️ No .wav or .mp3 files found in '{input_dir}'.")
        sys.exit(0)

    print(f"🎧 Found {len(audio_files)} audio file(s) in {input_dir}.")

    # Set output folder to "Output/Slices"
    output_dir = os.path.join("Output", "Slices")
    os.makedirs(output_dir, exist_ok=True)

    # Process each file
    for filename in audio_files:
        file_path = os.path.join(input_dir, filename)
        slice_4bars(file_path, output_dir)

    print("✅ All done! Your 4-bar slices are organized in the 'Output/Slices' folder.")

if __name__ == "__main__":
    main()