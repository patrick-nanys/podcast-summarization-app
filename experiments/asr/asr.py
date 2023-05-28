import subprocess
import time
import os


def whisper_asr(target_file_name):
    # parameters to the subprocess call
    WHISPER_MAIN_LOCATION = "./whisper_models/main.exe"
    WHISPER_MODEL_LOCATION = "./whisper_models/ggml-model-whisper-small.bin"

    # Whisper only works with wav files. If the input is an mp3, it has to be converted. A handy method for this is using ffmpeg, which has to be added to path before running the script.
    if target_file_name.endswith("mp3"):
        target_file_name_base, ext = os.path.splitext(target_file_name)
        new_target_file_name = target_file_name_base + ".wav"
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                target_file_name,
                "-ar",
                "16000",
                "-ac",
                "1",
                "-b:a",
                "96K",
                "-acodec",
                "pcm_s16le",
                new_target_file_name,
            ]
        )
        target_file_name = new_target_file_name

    thread_count = "4"

    p = subprocess.Popen(
        [WHISPER_MAIN_LOCATION, "-m", WHISPER_MODEL_LOCATION, "-t", thread_count, "-f", target_file_name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Monitoring the result of the subprocess call, writing the lines to a text file and printing the time it takes for each processing step
    start = time.perf_counter()

    # text buffers
    misc_lines = []
    lines = []
    file_number = 0
    first_file_write = True

    for line in p.stdout:
        line = line.decode("utf-8").strip("\n")  # stripping the newline at the end so it does not make 2 new lines

        end = time.perf_counter()
        interval = end - start

        # write into the buffer
        if line.startswith("["):
            line = line.lstrip("[")
            line = line.replace(" --> ", ";")
            line = line.replace("]   ", ";")
            lines.append(line)
        else:
            misc_lines.append(line)

        # if a long time elapses (meaning it takes more than 1 second for the model to do the inference on the part of the podcast) the buffer gets written to a file
        # the buffer gets written and reset exactly at the next "long time" occasion
        if interval > 1:
            print(interval)
            if not first_file_write:
                if lines:
                    with open(f"{target_file_name}_{file_number}.csv", "w") as file:
                        for line in lines:
                            file.write(line)
                            file.write('\n')
                        file_number += 1
                        lines = []
            else:
                first_file_write = False

        start = time.perf_counter()

    # at the end the buffer is always written out
    with open(f"{target_file_name}_{file_number}.csv", "w") as file:
        for line in lines:
            file.write(line)
            file.write('\n')

    # metadata returned by the model is saved as well
    with open(f"{target_file_name}_misc.txt", "w") as file:
        file.writelines(misc_lines)


if __name__ == "__main__":
    target_file_name = "2minutepaper.wav"
    whisper_asr(target_file_name)
