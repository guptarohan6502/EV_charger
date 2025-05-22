import threading
import time

done = False


def worker():
    counter = 0
    while not done:
    	time.sleep(1)
    	counter += 1
    	print("Counter: ", counter)
    


worker_thread = threading.Thread(target=worker).start()


input("Press Enter to Quit")
done = True