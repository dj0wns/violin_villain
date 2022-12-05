import crepe
import sounddevice
import math
import pygame

MUSICAL_NOTES = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

GAME_X = 500
GAME_Y = 500

def get_percent_note_freq_delta(freq, reference_freq):
  return 1200 * math.log2(freq/reference_freq)

#didnt want to do the math so kind of cheating 
def get_frequency_percentage(freq):
  return 1200 * math.log2(freq/1760.) #use a6 as a placeholder

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

def gameloop(frequency_dict):
  # Did the user click the window close button?
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          return False

  screen.fill((255,255,255))

  freq, closest_freq, confidence = get_frequency_from_microphone(frequency_dict)
  
  if confidence > 0.40:
    position_scalar = get_frequency_percentage(freq)
    pygame.draw.circle(screen, (0, 0, 255), (100, GAME_Y * position_scalar ), 25)

    print(f'{frequency_dict[closest_freq]}, {get_percent_note_freq_delta(freq, closest_freq)}, {confidence}, {position_scalar}')
  else:
    print("nothing heard")

  pygame.display.flip()
  return True

def get_frequency_from_microphone(frequency_dict):
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
    closest_freq = smaller_freq if abs(get_percent_note_freq_delta(freq, smaller_freq)) < \
        abs(get_percent_note_freq_delta(freq, larger_freq)) else larger_freq
  else:
    closest_freq = larger_freq

  return freq, closest_freq, confidence[0]

if __name__ == "__main__":
  frequency_dict = generate_frequency_dict()
  pygame.init()
  screen = pygame.display.set_mode([GAME_X, GAME_Y])

  while gameloop(frequency_dict):
    pass

  pygame.quit()
