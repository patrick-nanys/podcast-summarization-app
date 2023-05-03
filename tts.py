from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import torch.nn.functional as F
import soundfile as sf
import torchaudio
from speechbrain.pretrained import EncoderClassifier
import os
import numpy as np
from elevenlabslib import ElevenLabsUser
from pydub import AudioSegment
import io

def custom_speaker_embeddings(path, custom_tensor_path=None):
    classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-xvect-voxceleb")
    if type(path) == str: #path is a string, containing one soundwave
        signal, fs = torchaudio.load(path)
    elif hasattr(path, '__iter__'): #path is an iterable, containing multiple soundwaves
        signal = torch.cat([torchaudio.load(single_path)[0] for single_path in path], 1)
    else:
        raise ValueError('Path is neither a string or an iterable!')
    with torch.no_grad():
        embeddings = classifier.encode_batch(signal)
        embeddings = F.normalize(embeddings, dim=2)
        embeddings = embeddings.squeeze(0).cpu()
        if custom_tensor_path:
            np.savetxt(custom_tensor_path, embeddings.numpy())
    return embeddings

def cmu_arctic_xvector_embeddings(index):
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_embeddings = torch.tensor(embeddings_dataset[index]["xvector"]).unsqueeze(0) #7306

    return speaker_embeddings


def get_speaker_embeddings(embedding_type, path=None, custom_tensor_path=None):

    embedding_type_to_index_mapper = {
        'female1': 2700,
        'female2': 7500,
        'male1': 500,
        'male2': 1500,
        'male3': 3900,
        'male4': 5300,
        'male5': 6500,
    }

    if embedding_type.lower() == 'custom' and not path:
        raise ValueError('Custom voices need a path to load the custom voice from!')
    
    if embedding_type.lower() == 'custom':
        return custom_speaker_embeddings(path, custom_tensor_path)
    else:
        return cmu_arctic_xvector_embeddings(embedding_type_to_index_mapper[embedding_type.lower()])
    
def speecht5_tts(input_text, embedding_type, custom_embedding_path = None, embedding_tensor_path = None, output_path = 'tts_example.wav'):
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

    inputs = processor(text=input_text, return_tensors="pt")
    speaker_embeddings = get_speaker_embeddings(embedding_type, custom_embedding_path, embedding_tensor_path)

    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
    sf.write(output_path, speech.numpy(), samplerate=16000)

#ElevenLabs TTS: This could be costly. Voice cloning is only a paid feature, free TTS: 10000 characters/month

def elevenlabs_audio_bytes_from_chunk(input_text, API_KEY, voice_name):
    user = ElevenLabsUser(API_KEY)
    voice = user.get_voices_by_name(voice_name)[0]
    returned_value = voice.generate_audio_bytes(input_text)

    return returned_value

def elevenlabs_tts(chunks, API_KEY, voice_name, output_path):
    mp3_bytes = [elevenlabs_audio_bytes_from_chunk(chunk, API_KEY, voice_name) for chunk in chunks]
    all_audio = b''.join(mp3_bytes)
    recording = AudioSegment.from_file(io.BytesIO(all_audio), format="mp3")
    recording.export(output_path, format='mp3') #ElevenLabs always returns mp3 bytes. Maybe it should be converted to wav with ffmpeg?

if __name__ == '__main__':

    input_text = "Dear Fellow Scholars, this is 2 Minute Papers with Dr. Károly Zsolnai-Fehér.\
         This is GPT-4, OpenAI's new language model AI that we just talked about and today I would love to show you that it has barely been out and it is already taking the world by storm."
    
    embedding_path_list = [os.path.join('downloaded_voices', file) for file in os.listdir('downloaded_voices') if file.endswith('wav')][:60]
    custom_ebedding_path = '2minutepaper.wav'
    
    speecht5_tts(input_text, embedding_type = 'custom', custom_embedding_path = embedding_path_list, embedding_tensor_path = 'karoly_60.txt', output_path = 'tts_example_60.wav')
    
    
    