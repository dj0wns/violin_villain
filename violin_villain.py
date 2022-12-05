import crepe
import sounddevice
import math
import pygame
from collections import OrderedDict

A4 = 440
MUSICAL_NOTES = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
NUM_NOTES = 12
NUM_OCTAVES = 8

GAME_X = 500
GAME_Y = 500


def get_percent_note_freq_delta(freq, reference_freq):
  return 1200 * math.log2(freq/reference_freq)

def get_frequency_percentage(freq):
  #from https://math.stackexchange.com/a/1471919
  position = 12*(math.log2(freq) - math.log2(A4))
  # make the bottom zero rather than the center
  position += (NUM_NOTES*NUM_OCTAVES/2)
  return position/(NUM_NOTES*NUM_OCTAVES)

def generate_note_dict():
  starting_note = A4
  note_dict = OrderedDict()
  #calculate [a0,a7)
  #starting value is -48 (the number of steps from a1 to a4
  exponent = -60
  for i in range(NUM_OCTAVES):
    for j in range(NUM_NOTES):
      note_sub_offset = i + int(j>=3) - 1
      note_dict[MUSICAL_NOTES[j] + str(note_sub_offset)] = {"frequency":starting_note*pow(pow(2,1/12),exponent),
                                                            "position_to_a4":exponent,
                                                            "position_on_staff":-1}
      exponent +=1
  return note_dict

def draw_staff(note_dict):
  scalar = get_frequency_percentage(note_dict["E4"]["frequency"])
  #flip Y
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

  scalar = get_frequency_percentage(note_dict["G4"]["frequency"])
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

  scalar = get_frequency_percentage(note_dict["B4"]["frequency"])
  #flip Y
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

  scalar = get_frequency_percentage(note_dict["D5"]["frequency"])
  #flip Y
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

  scalar = get_frequency_percentage(note_dict["F5"]["frequency"])
  #flip Y
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

def gameloop(note_dict, frequency_to_note_dict):
  # Did the user click the window close button?
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          return False

  screen.fill((255,255,255))

  draw_staff(note_dict)

  freq, closest_note, confidence = get_frequency_from_microphone(note_dict, frequency_to_note_dict)

  if confidence > 0.40:
    position_scalar = get_frequency_percentage(freq)
    #flip y
    pygame.draw.circle(screen, (0, 0, 255), (100, GAME_Y - (GAME_Y * position_scalar)), 10)

    print(f'{closest_note}, {get_percent_note_freq_delta(freq, note_dict[closest_note]["frequency"])}, {confidence}, {position_scalar}')
  else:
    print("nothing heard")

  pygame.display.flip()
  return True

def get_frequency_from_microphone(note_dict, frequency_to_note_dict):
  fs = 16000
  duration = 0.1 #seconds, match with step size~
  recording = sounddevice.rec(int(duration * fs), samplerate=fs, channels=2,dtype='float64')
  sounddevice.wait()
  # get one sample for the entire duration or something
  time, frequency, confidence, activation = crepe.predict(recording, fs, viterbi=True, step_size=100, verbose=0)

  # find the last frequency smaller than the recorded frequency
  freq = frequency[0]
  index = 0
  smaller_note = -1
  larger_note = -1
  for k, v in frequency_to_note_dict.items():
    if k < freq:
      smaller_note = v
      continue
    else:
      larger_note = v
      break
  #now see which is closer
  if smaller_note > 0:
    closest_note = smaller_note if abs(get_percent_note_freq_delta(freq, note_dict[smaller_note]["frequency"])) < \
        abs(get_percent_note_freq_delta(freq, note_dict[larger_note]["frequency"])) else larger_note
  else:
    closest_note = larger_note

  return freq, closest_note, confidence[0]

if __name__ == "__main__":
  note_dict = generate_note_dict()
  frequency_to_note_dict = OrderedDict()
  for k,v in note_dict.items():
    frequency_to_note_dict[v["frequency"]] = k
  pygame.init()
  screen = pygame.display.set_mode([GAME_X, GAME_Y])

  while gameloop(note_dict, frequency_to_note_dict):
    pass

  pygame.quit()
