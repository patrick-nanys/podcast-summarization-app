## Running the workflow script

  
1. Download a model from https://ggml.ggerganov.com/ (in my case I used the ggml-model-whisper-small.bin version, which I didn't push because of its large size)  
2. Put the path of the downloaded model into the WHISPER_MODEL_LOCATION variable in asr.py  
3. 
```
pip install workflow_script_requirements.txt
```  
4. Set the default parameters in the workflow.py script  
5. 
```
python workflow.py
```  