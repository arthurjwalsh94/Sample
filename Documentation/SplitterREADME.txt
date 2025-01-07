Overview:
This tool uses Demucs to separate .wav, .mp3, or other supported audio files into individual stems (e.g., vocals, drums, bass). The results are then moved to a flat file structure in the Output folder.

Requirements:
	•	Python 3.10
	•	A virtual environment named “Splitter” (optional, but recommended)

Setup Steps:
	1.	(Optional) Set local Python version if using pyenv:
pyenv install 3.10.x        # only if not already installed
pyenv local 3.10.x
pyenv which python          # verify it points to your chosen 3.10.x
	2.	Create and activate the “Splitter” virtual environment:
python3.10 -m venv Splitter
source Splitter/bin/activate
	3.	Install dependencies:
pip install –upgrade pip
pip install -r Splitter_requirements.txt
(This installs Demucs, Torch, and other libraries required by the script.)
	4.	Place your audio files in the “Data” folder.
	•	By default, the script looks at:
input_folder = “/Users/arthurwalsh/Desktop/Machine/Data”
output_folder = “/Users/arthurwalsh/Desktop/Machine/Output/SplitStems”
	5.	Run the splitter:
python Splitter.py
	•	The script processes each audio file found in the input folder, creates separated stems, and saves them in the output directory.
	6.	Deactivate the environment when done:
deactivate

Notes:
	•	Supported extensions include .mp3, .wav, .flac, etc.
	•	If you get environment or library errors, confirm your virtual environment is active and that the pinned dependencies in “Splitter_requirements.txt” are installed.
	•	Large .dylib or .so files from Torch can exceed GitHub’s file-size limit; remember to add your “Splitter/” environment folder to .gitignore.