import os
import sys
import madmom
import numpy as np
from madmom.audio import Signal
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
import soundfile as sf

def slice_audio_by_8bars(audio_file, output_dir):
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
    
    # Ensure there are enough beats for slicing (needs at least 32)
    if len(beats) < 32:
        print("⚠️ Not enough beats detected for an 8-bar slice. Skipping file.")
        return
    
    # Slice Audio Based on 8-Bar Segments (32 beats per slice)
    beats_per_segment = 32
    num_segments = len(beats) // beats_per_segment
    
    for i in range(num_segments):
        start_time = beats[i * beats_per_segment]
        end_time = beats[(i + 1) * beats_per_segment] if (i + 1) * beats_per_segment < len(beats) else beats[-1]
        
        start_sample = int(start_time * 44100)
        end_sample = int(end_time * 44100)
        
        slice_audio = signal[start_sample:end_sample]
        
        # Construct the output filename
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_filename = os.path.join(
            output_dir,
            f"{base_name}_8bar_segment_{i + 1}.wav"
        )
        sf.write(output_filename, slice_audio, 44100)
        print(f"✅ Saved 8-bar slice: {output_filename}")
    
    print("🎉 All 8-bar slices saved successfully!")

def main():
    """
    Usage:
        python Slicer.py [input_folder]

    If [input_folder] is not provided, it defaults to "Data".
    The output folder will be created at "Output/<input_folder_name>".
    """
    # 1) Determine input folder
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = "Data"

    # 2) Derive a name for the output folder based on input folder
    folder_name = os.path.basename(os.path.normpath(input_dir))
    output_dir = os.path.join("Output", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # 3) Check if the input directory actually exists
    if not os.path.isdir(input_dir):
        print(f"❌ Error: Input folder '{input_dir}' not found.")
        sys.exit(1)
    
    # 4) Process .wav files in the input directory
    audio_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".wav")]
    if not audio_files:
        print(f"⚠️ No .wav files found in '{input_dir}'")
    
    for file in audio_files:
        audio_path = os.path.join(input_dir, file)
        slice_audio_by_8bars(audio_path, output_dir)
    
    print(f"🎧 All .wav files in '{input_dir}' have been processed and sliced into 8-bar segments successfully!")

if __name__ == "__main__":
    main()