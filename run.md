## Running the ASR feature

Since I was unable to build the program in the original repo https://github.com/ggerganov/whisper.cpp, I used this instead https://github.com/regstuff/whisper.cpp_windows. This is a prebuilt version for windows. The contents of it are in the repository (main.exe and the linked whisper.dll)  
Currently the requirements.txt is empty, because the imported modules are in the standard python library. Note that I'm using python version 3.10.10.  
  
1. Download a model from https://ggml.ggerganov.com/ (in my case I used the ggml-model-whisper-small.bin version, which I didn't push because of its large size)  
2. Have a wav file, which you would create text from.  
3. Put the path of that wav file into the target_file_name variable in asr.py (later this could be a cli argument or something)  
4. Put the path of the downloaded model into the WHISPER_MODEL_LOCATION variable in asr.py  
5. Run the asr script with the following command: python asr.py  

The script will generate txt files from the input wav, containing the recognized texts. The algorithm will create multiple output files, this way, when the input wav is long, for the earlier parts you don't have to wait until the program terminates.