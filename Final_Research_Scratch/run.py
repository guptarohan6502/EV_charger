import threading

import UI_ev
import sendtoBR
import sendtoArd

import time

# Create a class to store the result
class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        return self._return
        
        
 
 
port = 7002

EV_UI_thread = threading.Thread(target=UI_ev.EV,args=(port,port+1))
sendtoBR_thread = threading.Thread(target= sendtoBR.sendBR,args = (port,))
sendtoArd_thread = threading.Thread(target= sendtoArd.sendArduino,args = (port+1,))


sendtoBR_thread.start()
sendtoArd_thread.start()
time.sleep(2)
EV_UI_thread.start()

