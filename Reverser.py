import os
import sys
import soundfile as sf
import numpy as np

def combine_stems(stem_files, combined_file):
    """
    Given a list of .wav files, load each one, sum their sample data, and write out to 'combined_file'.

    Example usage:
        combine_stems(
            ["/path/to/Song_bass.wav", "/path/to/Song_vocals.wav", "/path/to/Song_other.wav"],
            "/path/to/Song_BassVocalsOther.wav"
        )
    """
    if not stem_files:
        print("⚠️ No stem files to combine.")
        return

    # Load the first file to get sample rate and shape
    data, sr = sf.read(stem_files[0])
    combined_data = np.array(data, dtype=np.float32)

    # Add each subsequent stem
    for stem_file in stem_files[1:]:
        stem_data, stem_sr = sf.read(stem_file)
        if stem_sr != sr:
            raise ValueError(f"Sample rate mismatch: {stem_file} has SR={stem_sr}, expected {sr}")

        # Ensure same length; if not, pad the shorter array or skip
        if len(stem_data) < len(combined_data):
            # Pad the shorter one
            padded = np.zeros_like(combined_data)
            padded[:len(stem_data)] = stem_data
            stem_data = padded
        elif len(stem_data) > len(combined_data):
            padded = np.zeros_like(stem_data)
            padded[:len(combined_data)] = combined_data
            combined_data = padded

        combined_data += stem_data

    sf.write(combined_file, combined_data, sr)
    print(f"✅ Combined stems -> {combined_file}")

def reverse_wav_file(in_path, out_path=None):
    """
    Reverses in_path and writes to out_path.
    If out_path is None, overwrites in_path.
    """
    data, sr = sf.read(in_path)
    reversed_data = np.flipud(data)
    if out_path is None:
        out_path = in_path
    sf.write(out_path, reversed_data, sr)
    print(f"✅ Reversed {in_path} -> {out_path}")

def process_reversal(split_folder):
    """
    1) For each 'base name' found (e.g., 'Song' in 'Song_bass.wav'),
       gather 'bass', 'vocals', 'other'.
    2) Combine them into 'Song_BassVocalsOther.wav'.
    3) Reverse that combined file -> 'Song_BassVocalsOther_reversed.wav'.
    """

    # Dictionary: { base_name: { 'bass': path, 'vocals': path, 'other': path, ... } }
    stems_dict = {}

    # Collect stems
    for filename in os.listdir(split_folder):
        if not filename.lower().endswith(".wav"):
            continue
        full_path = os.path.join(split_folder, filename)
        # Expected pattern: "Song_instrument.wav"
        base_name, instrument = parse_filename(filename)
        if base_name not in stems_dict:
            stems_dict[base_name] = {}
        stems_dict[base_name][instrument] = full_path

    # Combine & reverse for each base_name
    for base_name, instruments_map in stems_dict.items():
        # We only combine if all three exist, or you can adapt the logic:
        needed = ["bass", "vocals", "other"]
        existing_paths = []
        for needed_instrument in needed:
            if needed_instrument in instruments_map:
                existing_paths.append(instruments_map[needed_instrument])
        
        if len(existing_paths) < 1:
            # Nothing to combine
            continue
        
        combined_name = f"{base_name}_BassVocalsOther.wav"
        combined_path = os.path.join(split_folder, combined_name)
        
        # 1) Combine
        combine_stems(existing_paths, combined_path)
        
        # 2) Reverse the combined file (write to new file or overwrite)
        reversed_path = os.path.join(split_folder, f"{base_name}_BassVocalsOther_reversed.wav")
        reverse_wav_file(combined_path, reversed_path)

def parse_filename(filename):
    """
    Splits 'MySong_bass.wav' into ('MySong', 'bass').
    We'll handle the extension .wav and underscores.
    """
    name_only, _ = os.path.splitext(filename)  # "MySong_bass"
    # The last underscore usually separates base_name and instrument
    # e.g. "MySong_bass" -> base_name="MySong", instrument="bass"
    if "_" not in name_only:
        # fallback: treat everything as base_name, no instrument
        return name_only, "unknown"
    parts = name_only.rsplit("_", 1)
    base_name = parts[0]
    instrument = parts[1].lower()
    return base_name, instrument

def main():
    """
    Usage:
        python Reverser.py [input_folder]

    If [input_folder] is not provided, it defaults to "Data".

    We'll look for stems in "Output/<folder_name>_SplitStems" 
    and do:
      - combine (bass + vocals + other)
      - reverse that combined file
    """
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = "Data"

    folder_name = os.path.basename(os.path.normpath(input_dir))
    split_folder = os.path.join("Output", f"{folder_name}_SplitStems")

    if not os.path.isdir(split_folder):
        print(f"❌ Error: Could not find split folder: {split_folder}")
        sys.exit(1)

    print(f"🔄 Combining and reversing stems in {split_folder} ...")
    process_reversal(split_folder)
    print("🎉 Done!")

if __name__ == "__main__":
    main()