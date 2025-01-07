Overview:
This tool slices .wav audio files into 8-bar segments by detecting beats with madmom. It saves each segment as a separate .wav file in the Output folder.

Requirements:
	•	Python 3.9 (preferably 3.9.17)
	•	(Optional) pyenv for managing Python versions

Setup Steps:
	1.	(Optional) Use pyenv to set local Python version:
pyenv install 3.9.17  # Only if not already installed
pyenv local 3.9.17
pyenv which python    # Verify it points to 3.9.17
	2.	Create and activate a virtual environment:
python -m venv Slicer
source Slicer/bin/activate
	3.	Install dependencies in two steps:
a) Pre-install critical packages:
pip install –upgrade pip
pip install numpy==1.21.6 Cython==0.29.36 soundfile
b) Install the rest from the requirements file:
pip install -r Slicer_requirements.txt
	4.	Place your .wav files in the “Data” folder.
	5.	Run the slicing script:
python Slicer.py
(Slices are saved in the “Output” folder.)
	6.	When finished, deactivate the environment:
deactivate

Notes:
	•	If no .wav files are detected, confirm that your files are truly .wav format and placed in the “Data” directory.
	•	If a file has fewer than 32 detected beats, it may be skipped.