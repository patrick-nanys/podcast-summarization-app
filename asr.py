from subprocess import Popen, PIPE, STDOUT
import time

if __name__ == '__main__':

    #parameters to the subprocess call
    WHISPER_MAIN_LOCATION = './whisper_models/main.exe'
    WHISPER_MODEL_LOCATION = './whisper_models/ggml-model-whisper-small.bin'

    target_file_name = 'bryan_gee_short.wav'
    thread_count = '4'

    p = Popen([WHISPER_MAIN_LOCATION, '-m', WHISPER_MODEL_LOCATION, '-t', thread_count, '-f', target_file_name], stdin=PIPE, stdout=PIPE, stderr=STDOUT)

    #Monitoring the result of the subprocess call, writing the lines to a text file and printing the time it takes for each processing step
    start = time.perf_counter()

    #text buffers
    misc_lines = []
    lines = []
    file_number = 0
    first_file_write = True

    for line in p.stdout:
        line = line.decode('ascii').strip('\n') #stripping the newline at the end so it does not make 2 new lines

        end = time.perf_counter()
        interval = end-start

        #write into the buffer
        if '[' in line :
            lines.append(line)
        else:
            misc_lines.append(line)

        #if a long time elapses (meaning it takes more than 1 second for the model to do the inference on the part of the podcast) the buffer gets written to a file
        #the buffer gets written and reset exactly at the next "long time" occasion
        if interval > 1:
            print(interval)
            if not first_file_write:
                with open(f'{target_file_name}_{file_number}.txt', 'w') as file:
                    file.writelines(lines)
                    file_number += 1
                    lines = []
            else:
                first_file_write = False

        start = time.perf_counter()

    #at the end the buffer is always written out
    with open(f'{target_file_name}_{file_number}.txt', 'w') as file:
        file.writelines(lines)

    #metadata returned by the model is saved as well
    with open(f'{target_file_name}_misc.txt', 'w') as file:
        file.writelines(misc_lines)
            