import scipy.io.wavfile
import scipy.signal
import sys
import os

RATE = 20800


def resample(in_filename, out_filename ):
    (rate, signal) = scipy.io.wavfile.read(in_filename)
    directory, base = os.path.split(in_filename)
    outputPath = os.path.join(directory, f"{os.path.splitext(base)[0]}_resampled.wav")
    if rate != RATE:
        coef = RATE / rate
        samples = int(coef * len(signal))
        signal = scipy.signal.resample(signal, samples)
        scipy.io.wavfile.write(outputPath, RATE, signal)
    else: 
        outputPath = in_filename
    
    return outputPath

if __name__ == '__main__':
    resample(sys.argv[1], sys.argv[2])
