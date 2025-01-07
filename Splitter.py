import os
import subprocess
import sys
import shutil

# Supported audio file extensions
SUPPORTED_EXTENSIONS = ('.mp3', '.wav', '.flac', '.ogg', '.m4a')

# Function to run Demucs on a single file
def run_demucs(input_file, output_dir):
    """
    Runs Demucs to separate stems from the input audio file and flattens output filenames.

    Args:
        input_file (str): Path to the input audio file.
        output_dir (str): Path to the directory where output stems will be saved.

    Returns:
        None
    """
    # Ensure input file exists
    if not os.path.isfile(input_file):
        print(f"❌ Error: Input file '{input_file}' not found.")
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Temporary output folder for Demucs
    temp_output_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_output_dir, exist_ok=True)

    print(f"🔄 Running Demucs on '{input_file}'...")
    try:
        subprocess.run(
            [
                "demucs",
                input_file,
                "--out",
                temp_output_dir
            ],
            capture_output=True,
            text=True,
            check=True
        )

        print(f"✅ Demucs finished processing '{input_file}'.")

        # Move files to flat structure with naming convention
        move_demucs_files(temp_output_dir, output_dir, input_file)

    except subprocess.CalledProcessError as e:
        print("❌ Error running Demucs:\n", e.stderr)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Clean up temporary folders safely
        if os.path.exists(temp_output_dir):
            print(f"🧹 Cleaning up temporary folder: {temp_output_dir}")
            shutil.rmtree(temp_output_dir, ignore_errors=True)


# Function to move and rename Demucs files
def move_demucs_files(temp_folder, output_folder, input_file):
    """
    Moves and renames Demucs output files to a flat structure.

    Args:
        temp_folder (str): Temporary folder with Demucs outputs.
        output_folder (str): Final output folder for flattened files.
        input_file (str): Original input file path.

    Returns:
        None
    """
    # Locate Demucs output folder
    demucs_output_dir = None
    for root, dirs, files in os.walk(temp_folder):
        for dir in dirs:
            if dir.startswith("htdemucs"):
                demucs_output_dir = os.path.join(root, dir)
                break

    if not demucs_output_dir:
        print(f"❌ No 'htdemucs' folder found in {temp_folder}")
        return

    # Check for nested song folder
    song_folder = None
    for folder in os.listdir(demucs_output_dir):
        folder_path = os.path.join(demucs_output_dir, folder)
        if os.path.isdir(folder_path):
            song_folder = folder_path
            break

    if not song_folder:
        print(f"❌ No song folder found in '{demucs_output_dir}'")
        return

    # Move and rename files
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    for file in os.listdir(song_folder):
        if file.endswith(".wav"):
            instrument = os.path.splitext(file)[0]
            new_filename = f"{base_name}_{instrument}.wav"
            source_path = os.path.join(song_folder, file)
            destination_path = os.path.join(output_folder, new_filename)
            print(f"🔄 Moving: {source_path} → {destination_path}")
            shutil.move(source_path, destination_path)

    print("✅ All files have been moved and renamed successfully.")


# Function to process all audio files in a folder
def process_audio_files(input_folder, output_folder):
    """
    Processes all supported audio files in a given folder with Demucs.

    Args:
        input_folder (str): Path to the folder containing audio files.
        output_folder (str): Path to the folder where separated stems will be saved.

    Returns:
        None
    """
    if not os.path.isdir(input_folder):
        print(f"❌ Error: Input folder '{input_folder}' not found.")
        sys.exit(1)
    
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through files in the folder
    for file in os.listdir(input_folder):
        if file.lower().endswith(SUPPORTED_EXTENSIONS):
            input_file_path = os.path.join(input_folder, file)
            print(f"\n🎵 Processing file: {input_file_path}")
            run_demucs(input_file_path, output_folder)


# Main function for execution
def main():
    # Paths (adjust if necessary)
    input_folder = "/Users/arthurwalsh/Desktop/Machine/Data"
    output_folder = "/Users/arthurwalsh/Desktop/Machine/Output/SplitStems"

    # Process all audio files in the input folder
    process_audio_files(input_folder, output_folder)


if __name__ == "__main__":
    main()