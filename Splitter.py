import os
import sys
import shutil
import subprocess

SUPPORTED_EXTENSIONS = ('.mp3', '.wav', '.flac', '.ogg', '.m4a')

def run_demucs(input_file, output_dir):
    """
    Runs Demucs to separate stems from the input audio file, 
    then flattens output filenames into output_dir.
    """
    if not os.path.isfile(input_file):
        print(f"❌ Error: Input file '{input_file}' not found.")
        return

    os.makedirs(output_dir, exist_ok=True)

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
        move_demucs_files(temp_output_dir, output_dir, input_file)
    except subprocess.CalledProcessError as e:
        print("❌ Error running Demucs:\n", e.stderr)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if os.path.exists(temp_output_dir):
            print(f"🧹 Cleaning up temporary folder: {temp_output_dir}")
            shutil.rmtree(temp_output_dir, ignore_errors=True)

def move_demucs_files(temp_folder, output_folder, input_file):
    """
    Moves and renames Demucs output files to a flat structure.
    """
    demucs_output_dir = None
    for root, dirs, files in os.walk(temp_folder):
        for d in dirs:
            if d.startswith("htdemucs"):
                demucs_output_dir = os.path.join(root, d)
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

def process_audio_files(input_folder, output_folder):
    """
    Processes all supported audio files in a given folder with Demucs.
    """
    if not os.path.isdir(input_folder):
        print(f"❌ Error: Input folder '{input_folder}' not found.")
        sys.exit(1)
    
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.lower().endswith(SUPPORTED_EXTENSIONS):
            input_file_path = os.path.join(input_folder, file)
            print(f"\n🎵 Processing file: {input_file_path}")
            run_demucs(input_file_path, output_folder)

def main():
    """
    Usage:
        python Splitter.py [input_folder]

    If [input_folder] is not provided, it defaults to "Data".
    The output folder will be at "Output/<input_folder_name>_SplitStems".
    """
    # 1) Determine input folder
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = "Data"
    
    # 2) Derive a name for the output folder based on input folder
    folder_name = os.path.basename(os.path.normpath(input_dir))
    output_dir = os.path.join("Output", f"{folder_name}_SplitStems")
    os.makedirs(output_dir, exist_ok=True)

    # 3) Process
    process_audio_files(input_dir, output_dir)

if __name__ == "__main__":
    main()