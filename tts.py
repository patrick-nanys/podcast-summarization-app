from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import torch.nn.functional as F
import soundfile as sf
import torchaudio
from speechbrain.pretrained import EncoderClassifier

def custom_speaker_embeddings(path):
    classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-xvect-voxceleb")
    signal, fs = torchaudio.load(path)
    with torch.no_grad():
        embeddings = classifier.encode_batch(signal)
        embeddings = F.normalize(embeddings, dim=2)
        embeddings = embeddings.squeeze(0).cpu()
    return embeddings

def cmu_arctic_xvector_embeddings(index):
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_embeddings = torch.tensor(embeddings_dataset[index]["xvector"]).unsqueeze(0) #7306

    return speaker_embeddings


def get_speaker_embeddings(embedding_type, path=None):

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
        return custom_speaker_embeddings(path)
    else:
        return cmu_arctic_xvector_embeddings(embedding_type_to_index_mapper[embedding_type.lower()])
    
def speecht5_tts(input_text, embedding_type, custom_embedding_path = None, output_path = 'tts_example.wav'):
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

    inputs = processor(text=input_text, return_tensors="pt")
    speaker_embeddings = get_speaker_embeddings(embedding_type, custom_embedding_path)

    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
    sf.write(output_path, speech.numpy(), samplerate=16000)

if __name__ == '__main__':

    input_text = "Dear Fellow Scholars, this is 2 Minute Papers with Dr. Károly Zsolnai-Fehér.\
         This is GPT-4, OpenAI's new language model AI that we just talked about and today I would love to show you that it has barely been out and it is already taking the world by storm."
    
    speecht5_tts(input_text, embedding_type = 'custom', custom_embedding_path = '2minutepaper.wav', output_path = 'tts_example.wav')
    
    
    