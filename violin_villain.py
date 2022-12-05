import crepe
import sounddevice

MUSICAL_NOTES = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

def generate_frequency_dict():
  starting_note = 440 #A4
  frequency_dict = {}
  #calculate [a1,a6)
  #starting value is -48 (the number of steps from a1 to a4
  exponent = -48
  for i in range(6):
    for j in range(12):
      note_sub_offset = i + int(j>=3)
      frequency_dict[starting_note*pow(pow(2,1/12),exponent)] = MUSICAL_NOTES[j] + str(note_sub_offset)
      exponent +=1
  return frequency_dict

def execute(frequency_dict):
  fs = 16000
  duration = 0.1 #seconds, match with step size~
  recording = sounddevice.rec(int(duration * fs), samplerate=fs, channels=2,dtype='float64')
  sounddevice.wait()
  # get one sample for the entire duration or something
  time, frequency, confidence, activation = crepe.predict(recording, fs, viterbi=True, step_size=100, verbose=0)

  # find the last frequency smaller than the recorded frequency
  freq = frequency[0]
  index = 0
  smaller_freq = 0
  larger_freq = 0
  for k in frequency_dict.keys():
    if k < freq:
      smaller_freq = k
      continue
    else:
      larger_freq = k
      break
  #now see which is closer
  if smaller_freq > 0:
    closest_freq = smaller_freq if freq-smaller_freq < larger_freq-freq else larger_freq
  else:
    closest_freq = larger_freq

  if closest_freq == 0 or confidence[0] < 0.25:
    print("heard nothing")
  else:
    print(f'{frequency_dict[closest_freq]}, {freq-closest_freq}, {confidence}')



if __name__ == "__main__":
  frequency_dict = generate_frequency_dict()
  print(frequency_dict)
  while True:
    execute(frequency_dict)
