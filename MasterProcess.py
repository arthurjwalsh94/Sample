import sys
import os
import subprocess
import shutil

def main():
    """
    Usage:
        python MasterProcess.py [input_folder]

    Steps:
      1) Run AdvancedKeyDetector on the input folder -> renames .mp3/.wav files with BPM & Key
      2) Run Splitter on the input folder -> Output/<folder>_SplitStems
      3) Run Reverser on that same input folder (which internally finds the split folder)
      4) Run Slicer on the newly created stems folder
      5) Remove the leftover _SplitStems folder
    """
    # 1) Parse input folder argument
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
    else:
        input_folder = "Data"

    folder_name = os.path.basename(os.path.normpath(input_folder))
    splitted_folder = os.path.join("Output", f"{folder_name}_SplitStems")

    # 1) Advanced Key Detection (BPM & Key) on raw audio
    print(f"\n--- Running AdvancedKeyDetector on: {input_folder} ---")
    subprocess.run(["python", "AdvancedKeyDetector.py", input_folder], check=True)

    # 2) Run the Splitter
    print(f"\n--- Running Splitter on: {input_folder} ---")
    subprocess.run(["python", "Splitter.py", input_folder], check=True)

    # 3) Run the Reverser (by default references the same input_folder)
    print(f"\n--- Running Reverser on: {input_folder} ---")
    subprocess.run(["python", "Reverser.py", input_folder], check=True)

    # 4) Finally, run the Slicer on the splitted (and optionally reversed) stems folder
    print(f"\n--- Running Slicer on: {splitted_folder} ---")
    subprocess.run(["python", "Slicer.py", splitted_folder], check=True)

    print("\n✅ Master process complete! Stems have been split, reversed, and sliced.")

    # 5) Automatically remove the "_SplitStems" folder
    if os.path.isdir(splitted_folder):
        print(f"\n--- Removing leftover folder: {splitted_folder} ---")
        shutil.rmtree(splitted_folder)
        print("✅ SplitStems folder removed.\n")

if __name__ == "__main__":
    main()