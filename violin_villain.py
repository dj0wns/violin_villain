import crepe
import sounddevice

def execute():
  fs = 16000
  duration = 0.1 #seconds, match with step size~
  recording = sounddevice.rec(int(duration * fs), samplerate=fs, channels=2,dtype='float64')
  sounddevice.wait()
  time, frequency, confidence, activation = crepe.predict(recording, fs, viterbi=True, step_size=10)

  print(f'time: {time}, frequency: {frequency}, confidence: {confidence}')

if __name__ == "__main__":
  while True:
    execute() 
