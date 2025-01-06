import RPi.GPIO as GPIO
import time



def check_keypad():
    GPIO.setmode(GPIO.BCM)

    # Initialize GPIO and keypad matrix
    MATRIX = [['1', '2', '3', 'A'],
              ['4', '5', '6', 'B'],
              ['7', '8', '9', 'C'],
              ['*', '0', '#', 'D']]
    ROW = [5, 6, 13, 19]
    COL = [12, 16, 20, 21]


    for j in range(4):
        GPIO.setup(COL[j], GPIO.OUT)
        GPIO.output(COL[j], 1)
    for i in range(4):
        GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        start_stopCheck_time = time.time()
        while time.time() - start_stopCheck_time < 1:  # Run for up to 1 second
            for j in range(4):
                GPIO.output(COL[j], 1)
                for i in range(4):
                    if GPIO.input(ROW[i]) == GPIO.HIGH:
                        if MATRIX[i][j] == 'C':
                            print("Stopping Charging")
                            return True  # Return True if 'C' is pressed
                            raise StopIteration
                        while(GPIO.input(ROW[i]) == GPIO.HIGH):
                            pass
                GPIO.output(COL[j], 0)
    except StopIteration:
        GPIO.cleanup()
    return False



def keyboard_input(callback):
    GPIO.setmode(GPIO.BCM)
    MATRIX = [[1, 2, 3, 'A'],
              [4, 5, 6, 'B'],
              [7, 8, 9, 'C'],
              ['*', 0, '#', 'D']]
    ROW = [5, 6, 13, 19]
    COL = [12, 16, 20, 21]

    for j in range(4):
        GPIO.setup(COL[j], GPIO.OUT)
        GPIO.output(COL[j], 1)
    for i in range(4):
        GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        while True:
            for j in range(4):
                GPIO.output(COL[j], 1)
                for i in range(4):
                    if GPIO.input(ROW[i]) == GPIO.HIGH:
                        if MATRIX[i][j] == '#':
                            callback()  # Invoke the callback function when '#' is pressed
                            return
                            raise StopIteration

                        while(GPIO.input(ROW[i]) == GPIO.HIGH):
                            pass
                GPIO.output(COL[j], 0)
    except StopIteration:
        GPIO.cleanup()


    
    
    
def keypad():
    GPIO.setmode(GPIO.BCM)
    j = 0
    i = 0
    h = 0
    g = 0

    # elements of keypad
    MATRIX = [[1, 2, 3, 'A'],
              [4, 5, 6, 'B'],
              [7, 8, 9, 'C'],
              ['*', 0, '#', 'D']]

    # connections to GPIO pins
    ROW = [5, 6, 13, 19]  # rows of key
    COL = [12, 16, 20, 21]

    for j in range(4):
        GPIO.setup(COL[j], GPIO.OUT)
        GPIO.output(COL[j], 1)
    for i in range(4):
        GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    q = []
    n = []
    l = 0

    i = 0
    j = 0
    try:
        xmap = []
        while(j != 2 and i != 4):
            for j in range(4):
                GPIO.output(COL[j], GPIO.HIGH)
                for i in range(4):
                    if GPIO.input(ROW[i]) == 1:
                        a = MATRIX[i][j]
                        xmap.append(str(a))
                        print(a,end='')
                        time.sleep(0.2)
                        while(GPIO.input(ROW[i]) == 1):
                            pass
                        if(a == '#'):
                            print('\n')
                            y = len(xmap)
                            del xmap[y-1]
                            z = (''.join(str(m) for m in xmap))
                           # print(z)
                            return(z)
                            raise StopIteration

                GPIO.output(COL[j], GPIO.LOW)
    except StopIteration:
        GPIO.cleanup()



def keypad_take_inp():
    input_correct = False
    #check if take inp can be converted to int
    while(input_correct == False):
        take_inp = keypad()
        try:
            take_inp = int(take_inp)
            input_correct = True
        except:
            print("Input is not a number. Pls input again\n")
            input_correct = False
    return take_inp
