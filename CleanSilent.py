import os
import soundfile as sf
import numpy as np

def remove_silent_audio_recursively(root_folder, silence_threshold=1e-4):
    """
    Recursively walks through 'root_folder' and all its subfolders.
    For each audio file (wav, mp3, flac, ogg, m4a), checks if it’s near-silent
    by measuring the max amplitude. If below 'silence_threshold', deletes the file.
    
    Prints a summary of all removed files.
    """
    valid_exts = (".wav", ".mp3", ".flac", ".ogg", ".m4a")

    removed_files = []  # Keep track of which files get removed

    for current_path, dirs, files in os.walk(root_folder):
        for filename in files:
            # Only consider audio files
            if not filename.lower().endswith(valid_exts):
                continue
            
            file_path = os.path.join(current_path, filename)

            try:
                data, sr = sf.read(file_path)
                # Flatten if multi-channel
                if data.ndim > 1:
                    data = data.flatten()

                max_amp = np.max(np.abs(data))
                if max_amp < silence_threshold:
                    print(f"File '{file_path}' is near-silent (max amp={max_amp}). Deleting...")
                    os.remove(file_path)
                    removed_files.append(file_path)
            except Exception as e:
                print(f"Could not process '{file_path}': {e}")

    # Print a final summary of what got removed
    if removed_files:
        print("\nSummary of removed files:")
        for f in removed_files:
            print(f"  - {f}")
    else:
        print("\nNo files were removed.")

if __name__ == "__main__":
    # Example usage:
    root = "Output"  # or wherever your top-level folder is
    remove_silent_audio_recursively(root, silence_threshold=1e-4)