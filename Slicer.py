import os
import sys
import numpy as np
import soundfile as sf
from madmom.audio import Signal
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor

# Map the instrument text in the filename to a destination folder
INSTRUMENT_FOLDER_MAP = {
    "bass": "Bass",
    "drums": "Drums",
    "other": "Harmony",                  # Renamed from "Other"
    "vocals": "Vocals",
    "bassvocalsother": "NoDrums",        # Renamed from "Bass+Vocals+Other"
    "bassvocalsother_reversed": "NoDrums_Reversed",
}

def parse_instrument_from_filename(filename):
    """
    Example: "MySong_bass.wav" -> instrument = "bass"
             "MySong_drums.wav" -> instrument = "drums"
             "MySong_bassvocalsother_reversed.wav" -> instrument = "bassvocalsother_reversed"
    """
    name_only, _ = os.path.splitext(filename)  # e.g., "MySong_bass"
    parts = name_only.rsplit("_", 1)
    if len(parts) < 2:
        # No underscore or can't parse
        return None
    return parts[1].lower()

def slice_16bars(file_path, out_folder):
    """
    Loads audio from 'file_path', slices into 16-bar segments (64 beats each),
    up to 4 segments max, and places the resulting .wav files into 'out_folder'.
    """
    print(f"🎧 Processing 16-bar slices for: {file_path}")
    
    # Load audio at 44,100 Hz
    signal = Signal(file_path, sample_rate=44100)
    print(f"   ✅ Loaded Audio Signal: {len(signal)} samples")
    
    # Detect Beats
    beat_processor = RNNBeatProcessor()
    beat_activation = beat_processor(file_path)
    beat_tracker = DBNBeatTrackingProcessor(beats_per_bar=[4], fps=100)
    beats = beat_tracker(beat_activation)
    print(f"   ✅ Detected Beats: {len(beats)}")

    # Need at least 64 beats for a single 16-bar slice
    if len(beats) < 64:
        print("   ⚠️ Not enough beats for a 16-bar slice. Skipping file.")
        return

    # Each 16-bar slice is 64 beats
    beats_per_segment = 64
    num_segments = min(len(beats) // beats_per_segment, 4)

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    for i in range(num_segments):
        start_beat_index = i * beats_per_segment
        # The next slice either ends at (i+1)*64 or the last beat if shorter
        end_beat_index = min((i + 1) * beats_per_segment, len(beats) - 1)

        start_time = beats[start_beat_index]
        end_time = beats[end_beat_index]

        start_sample = int(start_time * 44100)
        end_sample = int(end_time * 44100)
        slice_audio = signal[start_sample:end_sample]

        # Construct output filename
        out_filename = f"{base_name}_16bar_segment_{i + 1}.wav"
        out_path = os.path.join(out_folder, out_filename)

        sf.write(out_path, slice_audio, 44100)
        print(f"   ✅ Saved 16-bar slice: {out_path}")

    print("   🎉 Finished slicing.\n")

def main():
    """
    Usage:
        python Slicer.py [input_folder]

    If [input_folder] is not provided, it defaults to 'Data'.

    This script:
      - Scans [input_folder] for .wav files
      - Parses instrument from each filename
      - Creates up to 4 segments of 16 bars (64 beats) each
      - Places slices into subfolders under 'Output/<Instrument>' (e.g., Output/Bass).
      - Unrecognized instruments default to 'Reverse'.
    """
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = "Data"

    if not os.path.isdir(input_dir):
        print(f"❌ Error: Input folder '{input_dir}' not found.")
        sys.exit(1)

    audio_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".wav")]
    if not audio_files:
        print(f"⚠️ No .wav files found in '{input_dir}'.")
        sys.exit(0)

    print(f"🎧 Found {len(audio_files)} .wav file(s) in {input_dir}.")
    
    # For each .wav, figure out which instrument folder to put the slices in
    for filename in audio_files:
        file_path = os.path.join(input_dir, filename)
        instrument = parse_instrument_from_filename(filename)
        
        if instrument is None:
            # Could not parse -> default to 'Reverse'
            folder_name = "Reverse"
        else:
            # e.g. "Bass" or "Harmony" etc.
            folder_name = INSTRUMENT_FOLDER_MAP.get(instrument, "Reverse")
        
        # Final path, e.g., Output/Bass
        instrument_folder = os.path.join("Output", folder_name)
        os.makedirs(instrument_folder, exist_ok=True)

        # Slice into 16-bar segments, up to 4
        slice_16bars(file_path, instrument_folder)

    print("✅ All done! Your 16-bar slices are organized in 'Output/<InstrumentFolder>'.")

if __name__ == "__main__":
    main()