from subprocess import Popen, PIPE, STDOUT
import time

if __name__ == '__main__':

    #parameters to the subprocess call
    WHISPER_MAIN_LOCATION = './whisper_models/main.exe'
    WHISPER_MODEL_LOCATION = './whisper_models/ggml-model-whisper-small.bin'

    target_file_name = 'bryan_gee.wav'
    thread_count = '4'

    p = Popen([WHISPER_MAIN_LOCATION, '-m', WHISPER_MODEL_LOCATION, '-t', thread_count, '-f', target_file_name], stdin=PIPE, stdout=PIPE, stderr=STDOUT)

    #Monitoring the result of the subprocess call, writing the lines to a text file and printing the time it takes for each processing step
    start = time.perf_counter()
    with open(f'{target_file_name}.txt', 'w') as file1:
        for line in p.stdout:
            end = time.perf_counter()
            file1.write(line.decode('ascii'))
            interval = end-start
            if interval > 1:
                print(interval)
            start = time.perf_counter()
            