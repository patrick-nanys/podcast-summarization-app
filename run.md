## Running the ASR feature

Since I was unable to build the program in the original repo https://github.com/ggerganov/whisper.cpp, I used this instead https://github.com/regstuff/whisper.cpp_windows. This is a prebuilt version for windows. The contents of it are in the repository (main.exe and the linked whisper.dll)  
Currently the requirements.txt is empty, because the imported modules are in the standard python library. Note that I'm using python version 3.10.10.  
  
1. Download a model from https://ggml.ggerganov.com/ (in my case I used the ggml-model-whisper-small.bin version, which I didn't push because of its large size)  
2. Have a wav file, which you would create text from. (with ffmpeg, the script can convert an mp3 to wav)  
3. Put the path of that wav file into the target_file_name variable in asr.py (later this could be a cli argument or something)  
4. Put the path of the downloaded model into the WHISPER_MODEL_LOCATION variable in asr.py  
5. Run the asr script with the following command: 
```
python asr.py
```  

The script will generate csv files from the input wav, containing the recognized texts. The texts will be in the form: start;end;text meaning it is easy to parse by setting the delimiter to ; with for example pandas.read_csv(). The algorithm will create multiple output files, this way, when the input wav is long, for the earlier parts you don't have to wait until the program terminates.

## Running the TTS feature

1. Install requirements with the following command:
```
pip install -r requirements.txt
```
2. In the tts.py file do the following:
     1. Specify input text
     2. Specify the speaker's voice by setting speaker embedding type to one of the following: custom, female1, female2, male1, male2, male3, male4, male5
     3. If using custom speaker embedding provide a path to a wav file containing the custom voice
     4. Provide the output path
3. Run the script:
```
python tts.py
``` 