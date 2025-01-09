import sys
import os
import subprocess

def main():
    """
    Usage:
        python MasterProcess.py [input_folder]

    If no input_folder is provided, it defaults to 'Data'.
    
    Steps:
    1) Run Splitter on the input folder -> Output/<folder>_SplitStems
    2) Run Slicer on the newly created stems folder
    """
    # 1) Parse the input folder argument (default to "Data" if none given)
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
    else:
        input_folder = "Data"

    # 2) Run the Splitter script
    #    This will output stems to: Output/<folder>_SplitStems
    print(f"\n--- Running Splitter on: {input_folder} ---")
    subprocess.run(["python", "Splitter.py", input_folder], check=True)

    # 3) Figure out where Splitter put its output
    #    By default: Output/<folder>_SplitStems
    folder_name = os.path.basename(os.path.normpath(input_folder))
    splitted_folder = os.path.join("Output", f"{folder_name}_SplitStems")

    # 4) Run the Slicer script on the newly created stems folder
    #    By default, Slicer will create Output/<folder>_SplitStems if it doesn't already exist.
    print(f"\n--- Running Slicer on: {splitted_folder} ---")
    subprocess.run(["python", "Slicer.py", splitted_folder], check=True)

    print("\n✅ Master process complete! Stems have been split and sliced.")

if __name__ == "__main__":
    main()