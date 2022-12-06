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

#returns nearest note_name to a freq
def get_nearest_note(freq, note_dict):
  index = 0
  smaller_note = ""
  larger_note = ""
  for k, v in frequency_to_note_dict.items():
    if k < freq:
      smaller_note = v
      continue
    else:
      larger_note = v
      break
  #now see which is closer
  if smaller_note == "":
    closest_note = smaller_note if abs(get_percent_note_freq_delta(freq, note_dict[smaller_note]["frequency"])) < \
        abs(get_percent_note_freq_delta(freq, note_dict[larger_note]["frequency"])) else larger_note
  else:
    closest_note = larger_note
  return closest_note

def get_max_note_position(note_dict):
  return list(note_dict.values())[-1]["position_on_staff"]

def get_frequency_position(freq, note_dict):
  closest_note = get_nearest_note(freq, note_dict)
  return note_dict[closest_note]["position_on_staff"]

def generate_note_positions(note_dict):
  # increment position if first letter is not the same is prior
  current = "G" # arbitrary starting note
  position = 0;
  for k,v in note_dict.items():
    if k[0] != current[0]:
      position += 1
    v["position_on_staff"] = position
    current = k

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
                                                            "position_on_staff":-1,
                                                            "is_flat":len(MUSICAL_NOTES[j]) > 1 and MUSICAL_NOTES[j][1] == "b",
                                                            "is_sharp":len(MUSICAL_NOTES[j]) > 1 and MUSICAL_NOTES[j][1] == "#"}
      exponent +=1
  return note_dict

def draw_staff(note_dict, max_note_position):
  scalar = note_dict["E4"]["position_on_staff"] / max_note_position
  #flip Y
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

  scalar = note_dict["G4"]["position_on_staff"] / max_note_position
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

  scalar = note_dict["B4"]["position_on_staff"] / max_note_position
  #flip Y
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

  scalar = note_dict["D5"]["position_on_staff"] / max_note_position
  #flip Y
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

  scalar = note_dict["F5"]["position_on_staff"] / max_note_position
  #flip Y
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar)), (GAME_X, GAME_Y - (GAME_Y * scalar)), 5)

def gameloop(note_dict, frequency_to_note_dict, max_note_position):
  # Did the user click the window close button?
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          return False

  screen.fill((255,255,255))

  draw_staff(note_dict, max_note_position)

  freq, closest_note, confidence = get_frequency_from_microphone(note_dict, frequency_to_note_dict)

  if confidence > 0.40:
    position_scalar = get_frequency_position(freq, note_dict) / max_note_position
    #flip y
    pygame.draw.circle(screen, (0, 0, 255), (100, GAME_Y - (GAME_Y * position_scalar)), 10)
    if note_dict[closest_note]["is_flat"]:
      pygame.draw.line(screen, (0, 0, 255), (114, GAME_Y - (GAME_Y * position_scalar)), (120, GAME_Y - (GAME_Y * position_scalar)), 4)
    if note_dict[closest_note]["is_sharp"]:
      pygame.draw.line(screen, (0, 0, 255), (117, GAME_Y - (GAME_Y * position_scalar) - 3), (117, GAME_Y - (GAME_Y * position_scalar)+3), 4)


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
  closest_note = get_nearest_note(freq, note_dict)

  return freq, closest_note, confidence[0]

if __name__ == "__main__":
  note_dict = generate_note_dict()
  generate_note_positions(note_dict)
  max_note_position = get_max_note_position(note_dict)
  frequency_to_note_dict = OrderedDict()
  for k,v in note_dict.items():
    frequency_to_note_dict[v["frequency"]] = k
  pygame.init()
  screen = pygame.display.set_mode([GAME_X, GAME_Y])

  while gameloop(note_dict, frequency_to_note_dict, max_note_position):
    pass

  pygame.quit()
