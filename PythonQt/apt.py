import numpy as np
import scipy.io.wavfile
import scipy.signal
import sys
from PIL import Image

class APT(object):
    RATE = 20800
    NOAA_LINE_LENGTH = 2080

    def __init__(self, filename, channel_crop=None):
        (rate, self.signal) = scipy.io.wavfile.read(filename)
        if rate != self.RATE:
            raise Exception("Resample audio file to {}".format(self.RATE))

        # Keep only one channel if audio is stereo
        if self.signal.ndim > 1:
            left = self.signal[:, 0]
            right = self.signal[:, 1]
            self.signal = right #(left + right) / 2
        
        self.performChannelCrop = False
        if channel_crop is not None:
            self.performChannelCrop = True
            
        truncate = self.RATE * int(len(self.signal) // self.RATE)
        self.signal = self.signal[:truncate]

    def decode(self, ui, channel, outfile=None):
        ui.setFormat("Enveloping...")
        hilbert = scipy.signal.hilbert(self.signal) # envoloping 
        ui.setValue(ui.value()+16)
        ui.setFormat("Filtering...")
        filtered = scipy.signal.medfilt(np.abs(hilbert), 5)
        ui.setValue(ui.value()+16)
        ui.setFormat("Reshaping...")
        reshaped = filtered.reshape(len(filtered) // 5, 5)
        ui.setValue(ui.value()+16)
        ui.setFormat("Digitizing...")   
        digitized = self._digitize(reshaped[:, 2]) 
        ui.setValue(ui.value()+16)
        ui.setFormat("Reshaping...")
        matrix = self._reshape(digitized)
        ui.setValue(ui.value()+16)
        ui.setFormat("Creating image...")
        image = Image.fromarray(matrix)
        
        ui.setValue(ui.value()+16)

        width, height = image.size
        if not outfile is None:
            image.save(outfile)
            if self.performChannelCrop: 
                self.channelCropper.crop(image, outfile)
        #image.show()
        
        return matrix

    def _digitize(self, signal, plow=0.5, phigh=99.5):
        '''
        Convert signal to numbers between 0 and 255.
        '''
        (low, high) = np.percentile(signal, (plow, phigh))
        delta = high - low
        data = np.round(255 * (signal - low) / delta)
        data[data < 0] = 0
        data[data > 255] = 255
        return data.astype(np.uint8)

    def _reshape(self, signal):
        '''
        Find sync frames and reshape the 1D signal into a 2D image.

        Finds the sync A frame by looking at the maximum values of the cross
        correlation between the signal and a hardcoded sync A frame.

        The expected distance between sync A frames is 2080 samples, but with
        small variations because of Doppler effect.
        '''
        # sync frame to find: seven impulses and some black pixels (some lines
        # have something like 8 black pixels and then white ones)
        syncA = [0, 128, 255, 128]*7 + [0]*7

        # list of maximum correlations found: (index, value)
        peaks = [(0, 0)]

        # minimum distance between peaks
        mindistance = 2000

        # need to shift the values down to get meaningful correlation values
        signalshifted = [x-128 for x in signal]
        syncA = [x-128 for x in syncA]
        for i in range(len(signal)-len(syncA)):
            corr = np.dot(syncA, signalshifted[i : i+len(syncA)])

            # if previous peak is too far, keep it and add this value to the
            # list as a new peak
            if i - peaks[-1][0] > mindistance:
                peaks.append((i, corr))

            # else if this value is bigger than the previous maximum, set this
            # one
            elif corr > peaks[-1][1]:
                peaks[-1] = (i, corr)

        # create image matrix starting each line on the peaks found
        matrix = []
        for i in range(len(peaks) - 1):
            matrix.append(signal[peaks[i][0] : peaks[i][0] + 2080])

        return np.array(matrix)
    
    def channelCropper(self, image, outfile):
        #These were shamelessly taken from aptdec
        APT_SYNC_WIDTH = 39
        APT_SPC_WIDTH = 47
        APT_TELE_WIDTH = 45
        APT_FRAME_LEN = 128
        APT_CH_WIDTH = 909
        
        i = image
        xsize,ysize = i.size
        cha = Image.new('RGB', (APT_CH_WIDTH,ysize))
        chb = Image.new('RGB', (APT_CH_WIDTH,ysize))
        (left, upper, right, lower) = (APT_SYNC_WIDTH+APT_SPC_WIDTH, 1,APT_SYNC_WIDTH+APT_SPC_WIDTH+APT_CH_WIDTH-10,ysize)
        cha = i.crop((left, upper, right, lower))
        
        (left, upper, right, lower) = (APT_SYNC_WIDTH+APT_SPC_WIDTH+APT_CH_WIDTH+APT_SYNC_WIDTH+APT_SPC_WIDTH+APT_TELE_WIDTH, 1,APT_SYNC_WIDTH+APT_SPC_WIDTH+APT_CH_WIDTH+APT_SYNC_WIDTH+APT_SPC_WIDTH+APT_CH_WIDTH+10,ysize)

        chb = i.crop((left, upper, right, lower))

        cha = cha.resize((909,ysize), Image.LANCZOS)
        chb = chb.resize((909,ysize), Image.LANCZOS)
        outfile = outfile.split(".")[0]
        
        cha.save(f"{outfile}_cha.png")
        chb.save(f"{outfile}_chb.png")

if __name__ == '__main__':
    apt = APT(sys.argv[1])

    if len(sys.argv) > 2:
        outfile = sys.argv[2]
    else:
        outfile = None
    apt.decode(outfile)
