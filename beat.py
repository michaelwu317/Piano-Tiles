# run the song
# read in when to send signals
# hit window is 0.5s (for now)
# keep a score and print out hit or miss
import multiprocess as mp
from pydub import AudioSegment
from pydub.playback import play
import time
import serial
import argparse

score = 0
parser = argparse.ArgumentParser()
parser.add_argument('-v, --verbose', dest='debug', help='increase output verbosity', action='store_true')
parser.add_argument('-p, --port', dest='port', help='where the kl46z board is connected', type=str, default='/dev/ttyACM0')
parser.add_argument('-g, --game', dest='game', help='select the game to play (easy.mp3 or med.mp3)', required=True)

args = parser.parse_args()

def hit(time_hit, correct_time):
    return time_hit - correct_time < 0.15

def update_score(total_points):
    global score
    score += 1
    print(f"Hit! Your current score: {score} out of {total_points}")

def lower_score(total_points):
    global score
    score -= 1
    print(f"Miss! Your current score: {score} out of {total_points}")

def audio_play():
    finished = False
    audio = AudioSegment.from_file(args.game, format="mp4")
    play(audio)
    finished = True


def start_game():
    ser = initialize_serial()
    times = []
    with open(f"{args.game.split('.')[0]}_correct.txt", "r") as f:
        for line in f:
            time_to_hit = float(line.replace("\n", ""))
            times.append(time_to_hit)
    f.close()
    total_points = len(times)
    start = time.time()
    i = 0
    while (True):
        current_time = time.time() - start
        if (len(times) == 0):
            break
        if (abs(current_time - times[0]) < 0.2):
            if i % 2 == 0:
                send_right(ser)
                if (wait_for_right(ser)):
                    update_score(total_points)
            else:
                send_left(ser)
                if (wait_for_left(ser)):
                    update_score(total_points)
            i += 1
            times.pop(0)
        else:
            x = ser.readline()
            if x == b'BADPRESS\r\n':
                lower_score(total_points)

def initialize_serial():
    """Initialize UART over serial for communication with the kl46z board"""
    return serial.Serial(args.port, 115200, timeout=0.01)

def send_left(ser):
    """Send a signal to the kl46z board that the left button should be pressed"""
    ser.write(b'LEFT\r')

def send_right(ser):
    """Send a signal to the kl46z board that the right button should be pressed"""
    ser.write(b'RIGHT\r')

def wait_for_right(ser):
    """
    This functions waits for the right button to be pressed
    If the button is pressed in time, the fuction returns true,
    otherwise it returns false
    """
    while 1:
        line = ser.readline()
        if line == b'ONTIMERIGHT\r\n':
            return True
        if line == b'MISSEDRIGHT\r\n':
            return False

def wait_for_left(ser):
    """
    This functions waits for the left button to be pressed
    If the button is pressed in time, the fuction returns true,
    otherwise it returns false
    """
    while 1:
        line = ser.readline()
        if args.debug: print(line.decode('utf-8').strip())
        if line == b'ONTIMELEFT\r\n':
            return True
        if line == b'MISSEDLEFT\r\n':
            return False

def main():
    mp.set_start_method('spawn')
    proc1 = mp.Process(target = audio_play)
    proc2 = mp.Process(target = start_game)
    proc1.start()
    proc2.start()
    proc1.join()
    proc2.join()
    print("Finished")

if __name__=="__main__":
    main()