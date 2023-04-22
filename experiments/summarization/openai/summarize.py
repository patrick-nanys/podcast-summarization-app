import tiktoken
import nltk
import openai
import os

API_COST_PER_THOUSAND_TOKENS = 0.002

openai.api_key = os.getenv("OPENAI_API_KEY")
nltk.download('punkt')
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def split_to_sentences(text: str):
    return sent_detector.tokenize(text)


def create_chunks_from_text(text: str, token_threshold, model="gpt-3.5-turbo-0301") -> list[str]:
    print(f'Text is {num_tokens_from_text(text)} tokens long.')
    sentences = split_to_sentences(text)
    # list of texts and their token counts
    texts: list[tuple] = []
    for sent in sentences:
        sent_token_count = num_tokens_from_text(sent)
        if len(texts) == 0 or texts[-1][1] + sent_token_count > token_threshold:
            texts.append((sent, sent_token_count))
        else:
            current_sent, current_token_count = texts[-1]
            texts[-1] = (current_sent + ' ' + sent, current_token_count + sent_token_count)
            
    print('Final chunks token counts: ', [count for chunk, count in texts])
    chunks = [chunk for chunk, token_count in texts]
    print(f'Split the text into {len(chunks)} chunks.')
    return chunks


def num_tokens_from_text(text, model="gpt-3.5-turbo-0301") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))


def create_message(prompt: str, text: str) -> list[dict]:
    return [{"role": "user", "content": f'{prompt} \n\n "{text}"'}]


def summarize_chunks(chunks: list[str]):
    prompt = "Summarize this podcast without including any kind of ads. Give only whole sentences. Do not have an intro."
    
    responses = []
    for chunk in chunks:
        responses.append(openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=create_message(prompt, chunk)
        ))
        
    return responses


def calculate_cost(responses: list[dict]) -> float:
    return sum([resp['usage']['total_tokens'] for resp in responses]) / 1000 * API_COST_PER_THOUSAND_TOKENS


def summarize_text(text: str) -> str:
    chunks = create_chunks_from_text(text, 3000)
    responses = summarize_chunks(chunks)

    # Check for errors
    for i, resp in enumerate(responses):
        finish_reason = resp['choices'][0]['finish_reason']
        if finish_reason != 'stop':
            print(f'There was a problem with generating a summary for chunk {i}. Reason: {finish_reason}.')
            
    print('Cost of summary was: ', calculate_cost(responses))
    
    return ' '.join([resp['choices'][0]['message']['content'] for resp in responses])

