import tiktoken
import nltk
import openai
import os
import numpy as np

API_COST_PER_THOUSAND_TOKENS = 0.002

openai.api_key = os.getenv("OPENAI_API_KEY")
nltk.download('punkt')
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def split_to_sentences(text: str):
    return sent_detector.tokenize(text)


def match_chunks_with_timestamps(chunk_token_counts, timestamps_dict):
    chunk_start_timestamps = []
    dict_keys_numpy = np.array(list(timestamps_dict.keys()))
    sum_token_counts = np.cumsum(chunk_token_counts)
    for i, _ in enumerate(chunk_token_counts):
        if i == 0:
            chunk_start_timestamps.append(list(timestamps_dict.values())[0])
        else:
            value_to_search = sum_token_counts[i-1]
            max_idx = np.max(dict_keys_numpy[dict_keys_numpy <= value_to_search])
            chunk_start_timestamps.append(timestamps_dict[max_idx])

    return chunk_start_timestamps


def create_chunks_from_text(text: str, token_threshold, timestamps_dict, model="gpt-3.5-turbo-0301"):
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
            
    chunk_token_counts = [count for chunk, count in texts]
    print('Final chunks token counts: ', chunk_token_counts)
    chunk_start_timestamps = match_chunks_with_timestamps(chunk_token_counts, timestamps_dict)
    
    chunks = [chunk for chunk, token_count in texts]
    print(f'Split the text into {len(chunks)} chunks.')
    print('chunk_start_timestamps', chunk_start_timestamps)
    return chunks, chunk_start_timestamps


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


def summarize_text(text: str, timestamps_dict):
    chunks, chunk_start_timestamps = create_chunks_from_text(text, 3000, timestamps_dict)
    responses = summarize_chunks(chunks)

    # Check for errors
    for i, resp in enumerate(responses):
        finish_reason = resp['choices'][0]['finish_reason']
        if finish_reason != 'stop':
            print(f'There was a problem with generating a summary for chunk {i}. Reason: {finish_reason}.')
            
    print('Cost of summary was: ', calculate_cost(responses))
    
    summarized_chunks = [resp['choices'][0]['message']['content'] for resp in responses]
    return ' '.join(summarized_chunks), summarized_chunks, chunk_start_timestamps

if __name__=='__main__':
    long_text = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur ac dapibus est. Proin finibus arcu nibh, et vehicula purus malesuada vitae. In non feugiat elit. Maecenas tincidunt venenatis porta. Sed mauris justo, pretium ac urna sit amet, venenatis volutpat arcu. Donec et nisl semper odio mattis porttitor nec at nulla. Quisque eu facilisis eros. Etiam at nisl et elit vestibulum mattis. Suspendisse id quam sed neque tempus dictum. Pellentesque in erat aliquet, dapibus mi a, luctus nisl. Aliquam vitae pulvinar neque. Pellentesque sed faucibus leo. Praesent non congue magna, sit amet finibus sem. Donec molestie orci placerat molestie tempus. Duis mollis, lorem id efficitur molestie, enim quam blandit quam, at venenatis orci urna sit amet felis. Fusce varius semper justo, ut tincidunt elit ultricies eu.

Fusce at tempus lacus, at placerat leo. Morbi nec volutpat mi, at accumsan metus. Vivamus feugiat tortor scelerisque feugiat molestie. Duis vitae venenatis felis. Pellentesque quis ultrices felis. Mauris lectus mauris, scelerisque ut sagittis eget, feugiat ut ex. Nunc vel diam dolor. Integer nec risus eu nulla varius viverra in id diam. Vestibulum ut turpis egestas, vestibulum nisi vitae, cursus nibh. Pellentesque id ipsum ac lectus fringilla gravida. Nunc dui justo, laoreet vel tristique vel, elementum eu nisl. Aenean at suscipit felis. Nullam elementum porttitor enim, id vehicula diam. Praesent tempor euismod pharetra. Maecenas sit amet vehicula enim, eget condimentum purus.

Sed pulvinar consectetur quam. Vivamus eros urna, venenatis ut vulputate in, posuere non urna. Pellentesque tortor nibh, pulvinar eget dolor eget, sodales ornare ligula. Maecenas fringilla finibus pulvinar. Integer eu dui non nisi maximus commodo vel eget leo. Praesent molestie consectetur facilisis. Duis egestas ex dui, ultrices lobortis mi auctor a. Aliquam porta bibendum purus vitae elementum. Pellentesque elit augue, imperdiet eu velit vel, tristique dignissim turpis. Etiam rhoncus massa odio, nec elementum ante consequat in. Sed sed pharetra elit. Maecenas egestas feugiat est, sit amet tincidunt leo porta vel. Fusce cursus lectus ut sem suscipit, at consequat lectus rutrum.

Etiam ut ligula volutpat, euismod arcu quis, viverra odio. Praesent eget orci et magna tempus dapibus. Etiam nisl ex, porta id eros et, vestibulum rhoncus odio. Vestibulum augue leo, bibendum eu pellentesque vehicula, gravida vitae arcu. Donec id vehicula arcu. Nam nisl lectus, vehicula mattis tortor ac, tempus consequat purus. Quisque gravida enim purus, vel hendrerit urna porttitor vitae. Duis vulputate arcu in fringilla rhoncus.

Phasellus facilisis lobortis sem, eget luctus ex ultrices vitae. Pellentesque sit amet placerat felis. Etiam in massa consectetur, faucibus sem a, fringilla sem. Aliquam est elit, auctor ac efficitur sit amet, finibus a eros. Interdum et malesuada fames ac ante ipsum primis in faucibus. Proin ornare, justo sit amet finibus hendrerit, massa ante sagittis lacus, id auctor mi nibh sed nulla. Duis tempus luctus ex, sed congue velit consequat vehicula. Praesent pretium dolor vel leo venenatis lobortis. Cras malesuada erat at aliquet efficitur. Nulla suscipit justo ac semper cursus. In sit amet leo pretium, feugiat ipsum at, posuere felis.

In placerat euismod dui, tempus tincidunt purus malesuada vitae. Etiam vehicula mi risus, in bibendum turpis posuere id. Nunc eu cursus urna. Nulla et velit at erat pretium interdum in vel ipsum. Aliquam risus lorem, blandit mattis fringilla nec, condimentum non nulla. Aliquam sagittis laoreet elit vel posuere. Sed nec quam aliquam, auctor erat nec, faucibus nunc. Nullam at pellentesque felis, non semper urna. Quisque vehicula, turpis vitae dapibus vestibulum, nulla mauris ultrices erat, quis vehicula magna odio vel felis.

Donec interdum sit amet diam vel venenatis. Cras sit amet consequat mi, et tempus quam. Integer est urna, lobortis ultrices quam id, scelerisque lacinia turpis. Nullam arcu quam, congue et arcu ac, porta blandit nunc. Fusce eros neque, rhoncus non aliquam ut, blandit id enim. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Sed bibendum et justo at cursus. Mauris tempus risus vel erat porttitor facilisis. Sed sollicitudin quam id nibh auctor, non euismod elit congue.

Aenean odio arcu, auctor vel convallis non, pharetra vel magna. Proin condimentum congue vulputate. Nullam ac quam placerat, aliquam leo non, mollis massa. Nunc pellentesque, nibh id iaculis congue, ipsum odio mattis lacus, id tristique felis lorem ut enim. Proin enim nibh, dignissim eu venenatis at, convallis elementum ante. Sed blandit tempus diam. Ut pellentesque faucibus lorem et laoreet. Etiam eget velit rutrum, laoreet neque eu, sagittis ex. Aliquam lacinia scelerisque ornare. Vivamus mattis sed sem et imperdiet. In lacinia mi nec justo vehicula, vitae sodales nisl tincidunt. Aenean condimentum blandit erat, quis cursus nisl. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Nulla quis fringilla ante, sit amet lobortis odio. Quisque rutrum placerat enim quis pretium.

Aenean fringilla a nunc eget tincidunt. Donec iaculis, lectus ut ornare luctus, mauris nunc euismod enim, eget volutpat ante erat sit amet tellus. Etiam varius aliquam augue ac molestie. Pellentesque at accumsan diam. Nulla sit amet risus vitae diam dapibus convallis ut sed tortor. Morbi pellentesque augue id arcu aliquam, vitae sagittis magna egestas. Nunc turpis risus, hendrerit nec aliquet id, ultricies luctus est. Donec eu laoreet ligula, eget vulputate ipsum. Nullam pulvinar eleifend rutrum.

Aliquam pellentesque semper auctor. Proin venenatis sem eros, at volutpat neque sollicitudin ac. Fusce leo purus, scelerisque eu gravida ac, ornare et enim. Pellentesque dictum quam id nulla vulputate pellentesque. Suspendisse at auctor enim, vitae fringilla turpis. Nullam molestie sagittis leo, blandit porta augue viverra at. Praesent vel convallis felis. Pellentesque malesuada laoreet nibh. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Mauris nulla mi, ultrices eget dolor nec, pretium ornare eros. Proin bibendum varius iaculis. Nulla commodo interdum lacus id posuere. Praesent venenatis euismod massa, in euismod turpis porttitor sed. Aenean accumsan metus orci, sed imperdiet quam consectetur et.

Quisque imperdiet sodales lorem, nec ornare enim dignissim vel. Aliquam mauris sem, rhoncus non aliquet ac, bibendum eu arcu. Vivamus sit amet felis ullamcorper, elementum justo in, malesuada diam. Donec ornare sed nisi eu porttitor. Nulla suscipit purus erat, vitae gravida elit efficitur id. Nunc nunc dolor, laoreet ut lectus et, rhoncus elementum velit. Ut in leo ac quam mollis vestibulum. Duis non lacinia lacus. In vel magna non magna interdum tincidunt. Etiam varius euismod enim eget tincidunt. Sed accumsan erat et varius sodales. In justo quam, condimentum eu metus posuere, faucibus semper lorem. Pellentesque leo nisl, convallis a feugiat sed, maximus id ante. Donec aliquam volutpat laoreet.

In cursus vitae sem nec luctus. Mauris ac tincidunt tortor, fermentum venenatis ipsum. Ut lacinia congue maximus. Ut eleifend rhoncus elit eget tempus. Duis sagittis orci et orci efficitur pellentesque. Etiam fermentum nibh vitae nunc porttitor rhoncus. Proin tortor quam, pretium vitae nulla vitae, ullamcorper placerat dui. Etiam vitae nulla luctus, tempus mauris ut, lacinia leo. Phasellus varius ultrices erat venenatis fermentum. Donec eget posuere ligula, in semper sapien. Integer consequat at turpis id pretium. Pellentesque mattis lacus fermentum, varius risus sit amet, ullamcorper sapien. Nulla mattis malesuada urna vitae molestie. Curabitur sit amet volutpat arcu, sed imperdiet neque. Morbi blandit, risus eu facilisis venenatis, neque est mattis lorem, vel rhoncus metus mauris eget orci. Nulla facilisi.

Etiam vel imperdiet nunc, eget ullamcorper tortor. Pellentesque at congue ex. Phasellus euismod nisl ut ligula tristique, et malesuada sem tincidunt. Donec et scelerisque dolor. Ut tristique augue elit, pulvinar dignissim dui ultrices eu. Pellentesque eget finibus nibh. Sed fringilla ac quam id condimentum. Vestibulum ut iaculis metus. Proin id ante nec mi sollicitudin mollis in eu risus. Suspendisse potenti. Aenean sed orci sed augue mollis pellentesque.

Fusce faucibus arcu ut pretium sollicitudin. Quisque ex nunc, vehicula eget placerat in, rhoncus id quam. Ut diam justo, egestas sit amet ornare et, dapibus at massa. Nulla sit amet blandit lorem, vel faucibus risus. Sed hendrerit dui in sem suscipit fringilla. Morbi egestas mattis egestas. Vestibulum in dignissim elit, sit amet pretium velit. Quisque gravida posuere ex fermentum maximus. Pellentesque eu consequat nisi. Aenean at tellus massa.

Vivamus gravida sed nulla non tempus. Maecenas fringilla magna lacus, ut mollis elit aliquam at. Interdum et malesuada fames ac ante ipsum primis in faucibus. Aliquam ullamcorper magna purus, et pharetra enim rhoncus quis. Mauris id quam nec augue iaculis condimentum quis non nisi. Sed tincidunt tellus vestibulum eros congue pulvinar. Nam non justo eu ex auctor viverra vitae a nisi. Cras aliquet, tellus ut imperdiet finibus, tortor lorem volutpat leo, id consequat magna nibh eget augue. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In aliquet consequat magna. Quisque sit amet mauris interdum, vestibulum sem nec, fermentum velit. In ut feugiat urna, ut pharetra lectus.

Fusce eu arcu viverra, convallis eros finibus, vehicula ante. Donec tincidunt lorem quis lacus rhoncus tristique. Ut ex nisl, pretium et ipsum vitae, eleifend aliquam turpis. Aenean vitae leo eget ligula pulvinar gravida. Vivamus condimentum felis sed eros lacinia, in finibus erat posuere. Morbi ultricies elit ante, sed euismod mauris rhoncus non. Praesent sollicitudin tempor leo fermentum luctus. Interdum et malesuada fames ac ante ipsum primis in faucibus.

Suspendisse vel ipsum sed augue efficitur luctus nec cursus urna. Proin auctor ex non lacus placerat, nec cursus mauris hendrerit. Curabitur mauris tellus, sagittis at sollicitudin a, faucibus non quam. Nunc elementum felis sed purus fermentum, at scelerisque sem aliquam. Pellentesque ut urna tellus. Phasellus imperdiet, nisl et pharetra placerat, orci nibh iaculis lorem, nec efficitur diam tellus eget nibh. Nam metus elit, ultricies sed tellus et, varius ultricies erat. Morbi ac felis vitae elit euismod imperdiet in nec massa. Nunc in efficitur tellus.

Donec efficitur, neque et facilisis efficitur, dui turpis aliquam sem, id auctor ipsum enim eu enim. Cras euismod quam volutpat ante viverra sagittis. Ut et est id risus ornare sagittis ut vitae diam. Aenean a augue purus. Donec aliquam ex felis, sed feugiat augue faucibus in. Proin fringilla consectetur est ut hendrerit. Nam vestibulum, quam ut laoreet venenatis, sem est eleifend ex, ut laoreet lacus leo a eros. Phasellus nec ullamcorper augue, non laoreet est. Aenean egestas, diam non aliquet vulputate, lacus nibh lacinia massa, in malesuada lectus sem id mauris.

Nullam enim dolor, pretium nec eleifend at, ornare eu lectus. Praesent semper sodales libero, id pulvinar metus ultrices ut. Proin ac turpis id lectus posuere gravida nec ut nulla. Sed sit amet nibh sed quam placerat volutpat. Suspendisse potenti. Integer sed lacus leo. Proin pellentesque suscipit efficitur. Sed purus felis, tincidunt a eros a, lobortis congue nulla. In pulvinar mi in ligula finibus, non sodales urna finibus. Etiam iaculis bibendum leo. Etiam justo nulla, tristique et augue sed, fringilla viverra justo. Nullam odio libero, rutrum vel euismod eget, mattis at lectus. Praesent ac libero condimentum leo efficitur semper a sed mi. Pellentesque gravida diam at tincidunt cursus. Quisque efficitur nisi in mauris commodo consequat.

Sed sit amet vestibulum dui. Sed ante sapien, luctus et sem tempor, condimentum fermentum elit. Nullam non urna a dui tempus commodo sed sit amet orci. In dapibus felis sed est porttitor, eu bibendum quam pellentesque. Ut a nunc sollicitudin mi vehicula euismod. Sed vel consequat mauris. Donec ornare, arcu vel porttitor semper, justo enim eleifend dui, ut semper elit enim ac mi. Aliquam venenatis arcu eget dolor dignissim ultrices. Sed enim ex, placerat interdum luctus vel, lobortis vitae ante. Aliquam malesuada pretium est. In ac quam a nisl iaculis porttitor. Nulla dictum lacus nec sapien cursus, nec auctor lectus porttitor. Fusce vitae semper mauris. Quisque semper odio sit amet imperdiet vehicula.

Donec eu mauris eleifend, laoreet metus sed, egestas ligula. Quisque iaculis commodo arcu. Suspendisse potenti. Integer semper dolor quam, non vehicula nibh dapibus suscipit. Praesent pellentesque malesuada erat, et facilisis justo consequat non. Vivamus et nulla ac orci bibendum consequat. Quisque aliquam accumsan elementum. Fusce maximus rutrum est at dignissim. Sed malesuada nunc non metus vestibulum, vel pretium ex scelerisque. Nunc sodales odio mauris, id laoreet quam mattis eget. Proin consectetur rhoncus elit, semper pharetra risus facilisis nec. Phasellus ullamcorper, nisl sit amet lobortis pharetra, felis arcu vulputate nisl, elementum dictum felis eros congue ipsum. Duis eros dui, vehicula a nisi vitae, dictum cursus nulla. Fusce ipsum lectus, dignissim at congue ut, commodo eget turpis.

Mauris fringilla libero eu diam iaculis, sit amet commodo purus sagittis. Cras augue velit, pulvinar quis porttitor id, maximus et odio. Praesent volutpat felis vel neque hendrerit, vitae mattis velit malesuada. Pellentesque ornare diam viverra magna pellentesque, ut bibendum lacus sodales. Pellentesque fermentum felis eu eros elementum vehicula. Ut blandit, odio ac consectetur fringilla, nunc nunc malesuada velit, eu vestibulum arcu libero ac quam. Suspendisse vitae condimentum quam. Nulla nulla nisl, semper ut eros et, vulputate accumsan augue. Curabitur accumsan augue eu sapien consequat, in dapibus metus dictum. Sed posuere varius dignissim. In eget velit ligula. Aenean tempus a turpis sed vehicula. Praesent feugiat sit amet erat eu vestibulum.

Morbi non orci elit. Maecenas vitae vulputate dolor. Duis sed dui nisi. Pellentesque a dignissim velit. Donec ligula felis, mattis vel viverra eu, bibendum quis erat. In hac habitasse platea dictumst. Maecenas congue tellus eu velit tempus, at convallis ipsum pretium. Ut blandit aliquet ornare. Nam sagittis vitae sem ac volutpat. Fusce sit amet purus orci. Nunc venenatis magna ac erat consectetur laoreet. Maecenas quis cursus justo, id eleifend leo. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

Praesent tristique lacus at nisl facilisis, vitae tincidunt felis varius. Vestibulum dapibus diam nisi, ut mollis urna condimentum sit amet. Curabitur condimentum elementum commodo. Suspendisse placerat erat vitae enim faucibus tempus eget id eros. Quisque tempor nibh lectus, ac rutrum nisl dapibus non. Vestibulum felis nulla, tincidunt a congue id, varius vel purus. Vivamus sit amet urna vestibulum, vestibulum purus non, ultricies tortor. Etiam nunc nisi, euismod a ligula nec, scelerisque suscipit quam. Aliquam non tempus urna.

Integer blandit odio eu ante rhoncus porttitor. Vestibulum sodales placerat urna vitae vulputate. Mauris mauris libero, sollicitudin at tellus eu, euismod pulvinar felis. Sed urna enim, tristique vitae augue a, faucibus tincidunt nunc. Phasellus ut mollis dui. Aenean tortor tortor, ornare nec dignissim vel, euismod quis urna. Integer euismod, felis eu euismod tincidunt, dolor mauris elementum felis, eget gravida elit neque ut lectus. Nam id sapien tempus, mattis nisl eu, pretium quam. Pellentesque eu arcu non tellus viverra iaculis at quis erat. Maecenas dui sapien, tempus vitae dui sit amet, consequat faucibus lorem. Morbi non mollis justo, dapibus mollis quam. Mauris id consequat erat, hendrerit commodo lacus. Integer posuere dui tellus. Ut eget tincidunt diam. Praesent id sapien purus.

Nam ut interdum nisl. Morbi dapibus ultrices tincidunt. Proin pulvinar magna condimentum luctus eleifend. Integer ut mauris nunc. Morbi augue sapien, tincidunt vitae pellentesque in, dictum ac velit. Cras ut luctus ex. Aliquam interdum, elit a feugiat rhoncus, metus felis dictum lectus, in consequat turpis nisi eget quam. Curabitur ante sapien, scelerisque eget elit vel, vehicula sodales orci. Phasellus eget augue eu justo consequat venenatis ac sit amet metus. Nunc id arcu at nulla fermentum eleifend.

Nam quis arcu euismod dolor dignissim sollicitudin. Ut a porttitor felis, at sollicitudin orci. Vivamus viverra cursus metus at imperdiet. Integer tincidunt a risus finibus eleifend. Vestibulum aliquet est non quam varius luctus. Donec vehicula aliquet lorem sit amet molestie. Curabitur nec nibh sed ipsum ullamcorper interdum. Proin sed odio eros. In porttitor, tortor vel faucibus pulvinar, arcu ligula elementum erat, a tempus augue lectus ac lectus.

Phasellus eu auctor tellus. Cras ullamcorper dui a tellus volutpat tincidunt. Morbi pharetra faucibus leo vel tristique. Sed id ipsum leo. Curabitur vel ligula iaculis, scelerisque elit eu, vulputate ante. In faucibus tincidunt dui, eget eleifend ex rutrum vel. Cras aliquet ultrices massa vitae malesuada. Ut convallis venenatis justo a consectetur. Mauris eget mi id tellus pretium suscipit vitae ac metus.

Morbi quis nisl ultricies urna suscipit aliquet. Pellentesque ut imperdiet sapien, eu tincidunt lacus. Vivamus tincidunt libero fermentum tempor fringilla. Vivamus tincidunt risus ut nisi laoreet blandit vestibulum eget mi. Vestibulum urna purus, tincidunt nec ligula et, imperdiet dictum est. Cras finibus eu augue eget tincidunt. Aliquam metus nisi, consequat molestie tincidunt consectetur, vestibulum quis augue. Maecenas eu finibus lorem.

Donec eu nulla sapien. Cras vestibulum, ipsum in iaculis consequat, sem lectus cursus nulla, nec vehicula odio ex ac tortor. Duis id hendrerit libero, quis feugiat velit. Nulla erat sapien, efficitur sed tempus at, maximus id eros. Quisque blandit, sem vel bibendum tincidunt, orci nibh porta arcu, in lacinia mauris nisi quis justo. Proin nec luctus tellus. Aenean sed ornare ligula. Pellentesque sed dignissim eros. Nulla tristique, augue scelerisque dignissim luctus, ipsum velit tincidunt massa, sed imperdiet elit ante sit amet dui. Mauris placerat sodales libero eget pulvinar. Fusce eget dignissim augue. Pellentesque mattis, arcu sed sodales porttitor, velit odio porttitor velit, sed faucibus tortor urna mattis urna. Praesent id ex at purus semper venenatis.

Nam semper lobortis dictum. Pellentesque vestibulum mi nec dolor blandit, quis vehicula magna finibus. Curabitur eget placerat orci. Sed nec est sagittis, molestie purus condimentum, rutrum tortor. Sed ornare maximus leo quis mattis. Vestibulum et elementum orci. Sed a est molestie, dictum lacus a, tincidunt mauris. Proin molestie elit quis imperdiet placerat.

Curabitur lectus odio, placerat in ante ut, vulputate luctus purus. Nullam at auctor nibh. Curabitur urna urna, elementum quis facilisis sed, luctus at mi. Etiam mollis, dolor ac iaculis posuere, sapien ex bibendum lorem, id feugiat lacus lacus quis metus. Aliquam elementum, magna sit amet maximus porta, libero nulla feugiat nisl, sit amet condimentum mi magna nec urna. Praesent ac dui imperdiet, vulputate magna non, faucibus magna. Mauris id bibendum arcu. Duis euismod vehicula tellus eget euismod.

Proin convallis dignissim nisi. Vivamus semper luctus libero id accumsan. Aliquam id elit fermentum, interdum tortor sed, placerat leo. Morbi pretium nisi eget mollis pharetra. Nulla ut blandit est, ac volutpat erat. Praesent id libero eget libero vestibulum dictum. Nulla id condimentum purus, et laoreet est. Duis sit amet euismod erat.

Duis lectus lorem, sagittis et ligula consequat, tincidunt ornare nisi. Ut at justo ante. Vivamus vitae justo tortor. Sed vestibulum, dui non ultricies luctus, sapien velit bibendum nunc, vel feugiat elit mauris quis mi. Aliquam vitae rutrum tellus, eu pretium tellus. Vivamus molestie ipsum nec arcu consequat efficitur. Cras nisi risus, consequat at imperdiet et, sodales a arcu. Quisque aliquam odio eget ullamcorper bibendum. Duis bibendum in diam eu congue.

Etiam sit amet pulvinar nisi. Nam placerat metus vel purus viverra suscipit. Fusce interdum mauris in nulla venenatis, vel volutpat erat faucibus. Quisque sit amet sagittis leo. Nulla vehicula ipsum tempor nulla aliquet, vel pretium turpis efficitur. Integer condimentum, metus non malesuada mollis, felis felis mollis felis, vel egestas nisi lacus id felis. Cras euismod, lacus pellentesque vestibulum ultrices, nulla augue interdum tellus, faucibus mattis massa nisi et augue. Quisque ac tristique elit.

Aliquam ullamcorper euismod arcu, eget aliquet tellus bibendum eu. Nam vel bibendum nibh. Etiam nec sem cursus, laoreet felis quis, dignissim libero. Sed eu dui sit amet nibh ultricies pretium at at diam. Nulla finibus enim tellus, a auctor augue sollicitudin at. Donec tristique nulla augue, eu sollicitudin nibh suscipit ut. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Aenean semper dui hendrerit nunc venenatis ultrices id maximus dui. Morbi tempor ex nec arcu malesuada, id cursus ligula faucibus. Maecenas aliquet sem ut efficitur ultricies. Aliquam sit amet ex vitae erat ultricies aliquet placerat eget sem. Cras fermentum urna ex, vitae pulvinar sem viverra sed.

Fusce at sem ut dolor euismod semper id at purus. Suspendisse id pellentesque leo. Curabitur ac tristique felis. Quisque finibus est a odio posuere, eget hendrerit arcu mattis. Quisque mollis tincidunt nisl sed tincidunt. Vestibulum ut est ut enim interdum facilisis vestibulum sit amet lectus. Nunc ac ultrices libero, ac feugiat ante. Phasellus elementum neque eget viverra lacinia. Duis a quam consectetur, rhoncus lectus eget, lobortis sem. Praesent ut tristique diam. Nunc commodo eros accumsan ipsum vestibulum condimentum.

Etiam rutrum egestas dapibus. Morbi odio nulla, posuere ut vulputate nec, sagittis sit amet magna. Nulla sodales scelerisque massa, in egestas lectus semper non. Aenean hendrerit nunc quis tortor sodales tempus. Maecenas hendrerit odio risus, eget blandit justo venenatis faucibus. In hac habitasse platea dictumst. Curabitur vestibulum egestas urna, nec imperdiet ligula efficitur sed. Proin vulputate porta euismod. Praesent ultrices erat quam, nec interdum sapien elementum quis. Morbi vitae mattis nibh. Duis molestie blandit justo, sed aliquet erat ullamcorper vitae. In commodo facilisis neque, vel pellentesque dui dignissim eget. In mattis nunc odio, at mollis arcu bibendum efficitur. Proin tincidunt mollis velit in pulvinar. Phasellus risus lectus, fermentum vitae hendrerit at, pellentesque tempus tortor.

Pellentesque et purus ultricies, malesuada nunc nec, vestibulum erat. Nullam in orci a arcu tincidunt lobortis et ac velit. In porttitor quam eget nulla cursus mattis. In posuere enim neque, id tincidunt sem feugiat sed. Sed bibendum commodo leo, vitae commodo libero semper a. Nulla pharetra suscipit felis, in venenatis lectus ultrices imperdiet. Interdum et malesuada fames ac ante ipsum primis in faucibus. Donec ultrices augue vitae nisl ultricies tristique.

Etiam eleifend quam nec dui semper, ut molestie enim elementum. Cras non imperdiet magna. In tincidunt egestas diam ac malesuada. Fusce rhoncus ante sed dolor placerat, ut laoreet leo mattis. Suspendisse nunc lacus, hendrerit ac porttitor quis, tristique ac est. Sed elementum est nisl, elementum convallis neque molestie non. Vivamus sed augue vitae sapien interdum volutpat vel et tortor. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Curabitur lobortis urna sapien, a vehicula lorem semper ut. Morbi sit amet convallis ex, in mattis quam. Nulla facilisi. Nullam sed mauris tempor, egestas velit nec, lobortis lectus. Aliquam a porttitor lorem, porta consequat ligula. Integer vestibulum eros luctus neque condimentum ultrices. Donec pretium mauris id eros tempus, et pretium purus sagittis. Quisque euismod condimentum ante, at vulputate sem rhoncus at.

Pellentesque eu semper elit. Cras quis diam velit. Nulla mauris leo, lobortis eu felis nec, cursus tincidunt leo. Curabitur suscipit sed ligula quis consectetur. Pellentesque lobortis faucibus magna in volutpat. Morbi erat metus, sagittis at volutpat in, condimentum gravida orci. Maecenas non cursus nulla. Sed ultrices pretium congue. Nam venenatis lacus quis nisl sodales, gravida iaculis mauris dignissim. Vivamus erat velit, hendrerit tempor gravida ut, porttitor nec magna. Morbi vitae facilisis risus, mollis facilisis ex. Phasellus semper, massa sit amet pellentesque luctus, ligula ipsum vehicula elit, a varius enim est a neque. Aenean enim enim, dapibus id nulla eu, vulputate mollis metus. Fusce luctus dolor lacinia quam pulvinar, eget posuere eros mattis.

Donec nibh magna, sollicitudin eu semper sed, dignissim in ligula. Suspendisse eu risus sit amet purus auctor blandit ut id odio. Fusce elementum ante velit, sit amet ultrices leo rutrum ac. Integer sem orci, finibus vel fringilla eget, imperdiet porttitor tortor. Etiam justo est, laoreet eget lacus sed, posuere pharetra odio. Sed sit amet blandit lectus. Fusce elementum lorem ac erat hendrerit, eu egestas justo consectetur.

Nam fringilla eget leo nec imperdiet. Nullam eu pellentesque urna. Pellentesque fermentum placerat iaculis. Mauris suscipit ullamcorper vehicula. Sed venenatis bibendum nisl congue imperdiet. Donec sollicitudin sollicitudin odio, et tincidunt tortor tincidunt non. Quisque sed mi fermentum, ornare enim nec, suscipit ligula. Duis at augue et elit malesuada pellentesque non id enim. Suspendisse eget lorem eu justo finibus dapibus. Maecenas quis velit lacinia, egestas leo eu, porttitor mauris.

Quisque lacinia malesuada velit eu viverra. Nunc vel metus iaculis, tristique elit ac, euismod augue. Quisque quam ex, ultricies non blandit non, varius non massa. Suspendisse nunc felis, convallis at nunc eu, iaculis porta felis. Curabitur nisl magna, ornare sed lectus at, mollis malesuada lacus. Aliquam tempor iaculis fermentum. Curabitur lobortis lorem risus, fringilla posuere libero accumsan eu. Mauris ex erat, ullamcorper in arcu sed, blandit gravida nulla. Fusce commodo, tellus et tristique aliquam, odio augue luctus quam, efficitur congue dui nisi sit amet velit. Donec non ultricies magna. Sed tincidunt vitae metus in interdum. Morbi ut erat sed turpis venenatis vehicula eu a purus. Pellentesque porta nulla velit, et dignissim libero ullamcorper eget. Duis tincidunt non felis in egestas. Pellentesque et est in est vehicula egestas. Phasellus blandit blandit nulla, ac sagittis libero porttitor tristique.

Aliquam laoreet aliquet massa et lacinia. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque lacus odio, tempor nec dui sed, malesuada accumsan erat. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Ut posuere risus eget posuere bibendum. In ac imperdiet mi. Sed ultrices dui eget urna finibus tristique. Donec malesuada nisi semper mauris tempus ornare. Quisque turpis ligula, pellentesque ut enim eget, ultrices congue erat. Proin eget nisi tincidunt, tempus sapien non, sodales augue. Cras vel iaculis purus. Nam in eros efficitur, porta sapien id, condimentum quam. Nam vitae mi felis. Duis porta nisl eget est laoreet commodo. Phasellus vitae mauris sed ipsum ornare pulvinar. Quisque elit justo, vestibulum sit amet purus quis, cursus tincidunt tortor.

Sed eget diam elit. Duis varius eleifend ligula, ac bibendum risus blandit non. Nam et justo felis. Quisque sodales, tortor sed bibendum sagittis, ante mauris ullamcorper purus, in euismod risus mi sit amet ipsum. Nam egestas dui egestas vestibulum pellentesque. Fusce maximus finibus malesuada. Phasellus eget rutrum ex. Integer pretium sit amet metus ac fermentum.

Maecenas sit amet vulputate felis, at dapibus odio. Aliquam eleifend libero vitae porta consequat. Sed venenatis, nulla vel fermentum porttitor, mi sapien sollicitudin mauris, et pellentesque dui lorem pulvinar odio. In aliquam purus lacinia vehicula pulvinar. Suspendisse luctus consectetur mauris, sit amet sodales ex. Quisque a semper diam, a mattis lorem. Nunc fermentum pharetra accumsan. Sed aliquet ex vitae ante ornare, eget vulputate leo porttitor. Aliquam lorem tellus, tincidunt non fermentum in, rhoncus at libero.

Morbi porttitor sem vitae nisl placerat accumsan. Aenean mattis massa quis dignissim posuere. Nulla sagittis et enim et mollis. Etiam blandit, lacus in malesuada luctus, diam lectus rutrum nunc, ut euismod ligula odio pretium mauris. Aliquam fringilla velit quis turpis porta, sit amet tincidunt lacus tincidunt. Proin non pellentesque quam. Phasellus ante ligula, eleifend in justo sit amet, ullamcorper tristique ante. Mauris in tincidunt neque.

Nam aliquam blandit arcu ut rhoncus. Mauris vestibulum, leo aliquam fringilla malesuada, enim tortor porta lectus, id facilisis turpis nunc non est. Quisque dapibus sapien est, vel vulputate lectus placerat et. Interdum et malesuada fames ac ante ipsum primis in faucibus. Cras eu quam varius, bibendum dolor vestibulum, ullamcorper velit. Maecenas accumsan nec odio dignissim tempus. Praesent eu ligula lacinia, consectetur diam eu, placerat elit. Ut tempus enim augue, tempus condimentum lectus commodo non. Proin sit amet neque euismod, lacinia nulla id, suscipit ex. Proin finibus erat sit amet ipsum efficitur efficitur. Aliquam in aliquet lorem.

Proin cursus rutrum sem, nec rhoncus odio tincidunt at. Quisque quis congue nunc, et euismod arcu. Mauris ac odio sed erat scelerisque ultrices. Cras pharetra, neque non malesuada ultrices, lectus lorem finibus urna, nec vulputate arcu justo vel tortor. Praesent ac ligula massa. Sed rhoncus neque porttitor pulvinar posuere. Phasellus quis mauris molestie, dignissim diam ut, maximus justo. Nullam mattis libero at sem suscipit, a accumsan ex efficitur. Sed id pellentesque est, ut pellentesque nisl. Nam vestibulum lobortis faucibus. Pellentesque convallis finibus diam at varius. Phasellus pellentesque dictum felis, sit amet suscipit diam auctor in. Pellentesque in sem neque. Nunc pharetra odio at molestie maximus.'''


    char_counts = [0, 3000, 4000, 5000, 1340000]
    timestamps = ['000', 'time3', '4', '5', '6']
    timestamp_dict = dict(zip(char_counts, timestamps))
    chunks = create_chunks_from_text(long_text, 3000, timestamp_dict)