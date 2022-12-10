import crepe
import sounddevice
import math
import pygame
import os
from collections import OrderedDict

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

A4 = 440
MUSICAL_NOTES = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
NUM_NOTES = 12
NUM_OCTAVES = 8

GAME_X = 1920
GAME_Y = 1080
WORLD_SCALAR = 2
CURSOR_POSITION = 140
CURSOR_RADIUS = 8
CURSOR_ACCIDENTAL_DISTANCE = 15
CURSOR_LINE_OFFSET = 5

TREBLE_CLEF = pygame.image.load(os.path.join(ASSET_DIR, "treble_clef.png"))
TREBLE_CLEF_INDENT = 30
TREBLE_X = 90
TREBLE_Y = 154

ACCIDENTAL_X = 10
ACCIDENTAL_Y = 29
SHARP = pygame.image.load(os.path.join(ASSET_DIR, "sharp.png"))
FLAT = pygame.image.load(os.path.join(ASSET_DIR, "flat.png"))

QUARTER_NOTE_X = 10
QUARTER_NOTE_Y = 29
QUARTER_NOTE = pygame.image.load(os.path.join(ASSET_DIR, "quarter_note.png"))

# from too low to too high, center is ideal
USER_NOTE_COLORS = [
(255,143,49),
(84,240,118),
(174,70,250),
]

NOTE_ZONE_COLOR = (255, 253, 208)
NOTE_ZONE_WIDTH = 50

def get_color_from_distance(cents_off):
  #stepwise coloring
  if cents_off > 20:
    return USER_NOTE_COLORS[0]
  elif cents_off > -20:
    return USER_NOTE_COLORS[1]
  else:
    return USER_NOTE_COLORS[2]

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
  if smaller_note != "":
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

def draw_note_zone():
   pygame.draw.line(screen, NOTE_ZONE_COLOR,
                    (WORLD_SCALAR * CURSOR_POSITION, 0),
                    (WORLD_SCALAR * CURSOR_POSITION, GAME_Y),
                    WORLD_SCALAR * NOTE_ZONE_WIDTH)

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

def position_to_y(position, max_note_position):
  return GAME_Y - (GAME_Y * (position / max_note_position))

def draw_static_images(note_dict, max_note_position):
  # center to center of staff
  staff_center_scalar = note_dict["B4"]["position_on_staff"] / max_note_position
  staff_center_y = GAME_Y - (GAME_Y * staff_center_scalar)
  screen.blit(TREBLE_CLEF, (WORLD_SCALAR*TREBLE_CLEF_INDENT - WORLD_SCALAR*TREBLE_X/2, staff_center_y - WORLD_SCALAR*TREBLE_Y/2))

def draw_sharp(color, center_x, center_y):
  screen.blit(SHARP, (center_x - WORLD_SCALAR*ACCIDENTAL_X/2, center_y - WORLD_SCALAR*ACCIDENTAL_Y/2))

def draw_flat(color, center_x, center_y):
  screen.blit(FLAT, (center_x - WORLD_SCALAR*ACCIDENTAL_X/2, center_y - 3*WORLD_SCALAR*ACCIDENTAL_Y/4))

def draw_quarter_note(note_position, center_x, max_note_position):
  position = position_to_y(note_position, max_note_position)
  screen.blit(QUARTER_NOTE, (center_x - WORLD_SCALAR * QUARTER_NOTE_X/2, position -  WORLD_SCALAR * QUARTER_NOTE_Y/2))

def draw_off_staff_lines(note, note_dict, max_note_position):
  if note_dict[note]["position_on_staff"] < note_dict["F5"]["position_on_staff"]:
    # below the staff
    # shift position by 2 so it goes over the current position
    for i in range(note_dict["F5"]["position_on_staff"]-2, note_dict[note]["position_on_staff"]-1, -2):
      scalar = i / max_note_position
      pygame.draw.line(screen, (0, 0, 0), (WORLD_SCALAR * (CURSOR_POSITION - CURSOR_RADIUS - CURSOR_LINE_OFFSET),  GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5),
                                          (WORLD_SCALAR * (CURSOR_POSITION + CURSOR_RADIUS + CURSOR_LINE_OFFSET), GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5),
                                          WORLD_SCALAR * 2)
  elif note_dict[note]["position_on_staff"] > note_dict["E4"]["position_on_staff"]:
    # above the staff
    # shift position by 2 so it goes over the current position
    for i in range(note_dict["E4"]["position_on_staff"]+2, note_dict[note]["position_on_staff"]+1, 2):
      scalar = i / max_note_position
      pygame.draw.line(screen, (0, 0, 0), (WORLD_SCALAR * (CURSOR_POSITION - CURSOR_RADIUS - CURSOR_LINE_OFFSET),  GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5),
                                          (WORLD_SCALAR * (CURSOR_POSITION + CURSOR_RADIUS + CURSOR_LINE_OFFSET), GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5),
                                          WORLD_SCALAR * 2)


def draw_staff(note_dict, max_note_position):
  scalar = note_dict["E4"]["position_on_staff"] / max_note_position
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), (GAME_X, GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), WORLD_SCALAR * 2)

  scalar = note_dict["G4"]["position_on_staff"] / max_note_position
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), (GAME_X, GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), WORLD_SCALAR * 2)

  scalar = note_dict["B4"]["position_on_staff"] / max_note_position
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), (GAME_X, GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), WORLD_SCALAR * 2)

  scalar = note_dict["D5"]["position_on_staff"] / max_note_position
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), (GAME_X, GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), WORLD_SCALAR * 2)

  scalar = note_dict["F5"]["position_on_staff"] / max_note_position
  pygame.draw.line(screen, (0, 0, 0), (0,  GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), (GAME_X, GAME_Y - (GAME_Y * scalar) - WORLD_SCALAR * 0.5), WORLD_SCALAR * 2)

def gameloop(note_dict, frequency_to_note_dict, max_note_position):
  # Did the user click the window close button?
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          return False

  screen.fill((255,255,255))

  draw_note_zone()
  draw_staff(note_dict, max_note_position)
  draw_static_images(note_dict, max_note_position)
  draw_quarter_note(note_dict["E4"]["position_on_staff"], GAME_X/2, max_note_position)

  freq, closest_note, confidence = get_frequency_from_microphone(note_dict, frequency_to_note_dict)

  if confidence > 0.60:
    color = get_color_from_distance(get_percent_note_freq_delta(freq, note_dict[closest_note]["frequency"]))
    position_scalar = get_frequency_position(freq, note_dict) / max_note_position
    #flip y
    y_position = GAME_Y - (GAME_Y * position_scalar)
    draw_off_staff_lines(closest_note, note_dict, max_note_position)
    pygame.draw.circle(screen, color, (WORLD_SCALAR * CURSOR_POSITION, y_position), WORLD_SCALAR * CURSOR_RADIUS)
    if note_dict[closest_note]["is_flat"]:
      draw_flat(color, WORLD_SCALAR * (CURSOR_POSITION - CURSOR_ACCIDENTAL_DISTANCE), y_position)
    if note_dict[closest_note]["is_sharp"]:
      draw_sharp(color, WORLD_SCALAR * (CURSOR_POSITION - CURSOR_ACCIDENTAL_DISTANCE), y_position)



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

def init_images():
  global TREBLE_CLEF
  global SHARP
  global FLAT
  global QUARTER_NOTE
  #set up images
  TREBLE_CLEF.convert_alpha()
  TREBLE_CLEF = pygame.transform.scale(TREBLE_CLEF,(WORLD_SCALAR*TREBLE_X, WORLD_SCALAR*TREBLE_Y))
  SHARP.convert_alpha()
  SHARP = pygame.transform.scale(SHARP,(WORLD_SCALAR*ACCIDENTAL_X, WORLD_SCALAR*ACCIDENTAL_Y))
  FLAT.convert_alpha()
  FLAT = pygame.transform.scale(FLAT,(WORLD_SCALAR*ACCIDENTAL_X, WORLD_SCALAR*ACCIDENTAL_Y))
  QUARTER_NOTE.convert_alpha()
  QUARTER_NOTE = pygame.transform.scale(QUARTER_NOTE,(WORLD_SCALAR*QUARTER_NOTE_X, WORLD_SCALAR*QUARTER_NOTE_Y))

if __name__ == "__main__":
  note_dict = generate_note_dict()
  generate_note_positions(note_dict)
  max_note_position = get_max_note_position(note_dict)
  frequency_to_note_dict = OrderedDict()
  for k,v in note_dict.items():
    frequency_to_note_dict[v["frequency"]] = k

  pygame.init()
  screen = pygame.display.set_mode([GAME_X, GAME_Y])
  init_images()

  while gameloop(note_dict, frequency_to_note_dict, max_note_position):
    pass

  pygame.quit()
