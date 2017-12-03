import librosa
import numpy as np
import scipy
import pickle
import os
import math

ranges = [40, 80, 120, 180, 300]
fft_frame_size = 2000


def remove_zeros(vec):
    temp = np.transpose(vec == 0)
    indices = np.argwhere(temp == False)
    return vec[indices[0][0]:indices[len(indices) - 1][0]]

def get_fft_chunks(time_data):
    num_samples= len(time_data)//fft_frame_size
    return [np.fft.fft(time_data[i*fft_frame_size:(i+1)*fft_frame_size]) for i in range(num_samples)]

def get_magnitudes(fft):
    #return high_mags, a 2d array
    #high_mags[i][0] is for 0-40
    #high_mags[i][1] is for 40-80
    #etc. where i is in range(len(fft)), or each fft window 
    high_mags = [np.zeros(len(ranges)) for k in range(len(fft))]
    
    def max_mag_in_window(index, high_mags):
        nonlocal i
        #tuple in form (current highest magnitude, index of current highest magnitude)
        mag = (0, 0)
        while(fft_freqs[i] < ranges[index]): 
            curr_mag = math.log10(abs(window[i])+1)
            if curr_mag > mag[0]:
                mag = (curr_mag, i)
            i += 1
            high_mags[fft_window][index] = fft_freqs[mag[1]]
            
    for fft_window in range(len(fft)):
        window = fft[fft_window]
        i = 0
        #find the maximum magnitudes in each window of ranges (0-40, 40-80, etc.)
        for j in range(len(ranges)):
            max_mag_in_window(j, high_mags)
    return high_mags

#a key is a set of 5 magnitudes that are the greatest in the ranges represented as a string
#0-40, 40-80, 80-120, 120-180, and 180-300 Hz
#the values are dictionaries mapping song -> time indices
#time is the "window" (an index) and song is a string such as "furelise"

def populate_database(mags, database, song_name):
    for i in range(len(mags)): #i = index of "window" so it corresponds to what we can consider "time" i suppose
        key = str(mags[i])
        if key not in database:
            database[key] = {}
        if song_name not in database[key]:
            database[key][song_name] = []
        database[key][song_name].append(i)

#replace with the name of the input file
original_wav = "furelise.wav"
songs_wav = [song for song in os.listdir("songs") if song[-3:] == "wav"]

with open('song_data.pickle', 'rb') as handle:
    database = pickle.load(handle)
original, sample_rate = librosa.load("songs/" + original_wav)
# song_data = [original] + [librosa.load("songs/" + song)[0] for song in songs_wav]

freq = np.fft.fftfreq(fft_frame_size)
fft_freqs = [abs(freq[i]*sample_rate) for i in range(fft_frame_size)] #frequencies at indices of the dft

#process original/input song 
original = remove_zeros(original)
original_fingerprint = {}
original_fft = get_fft_chunks(original)
mags = get_magnitudes(original_fft)
populate_database(mags, original_fingerprint, original_wav)

#initialize dictionary (song->similarity)
similarities = {key[:-4]:0 for key in songs_wav}
#for each set of 5 notes in the original/input song, check if in other songs
for key in original_fingerprint.keys():
    if key in database:
        for song_name in database[key]:
            similarities[song_name] += len(database[key][song_name]) * len(original_fingerprint[key])
print(similarities)
def knn(k, sim_dict):
    sorted_dict = sorted(sim_dict, key=sim_dict.get, reverse=True)[:k]
    counts = {}
    for s in sorted_dict:
        name = s[:-1]
        if name not in counts:
            counts[name] = 0
        counts[name] += 1
    return max(counts, key=counts.get)

out = knn(3, similarities)
print(out)