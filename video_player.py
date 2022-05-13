# -*- coding: utf-8 -*-
"""
Created on Mon May  9 12:00:25 2022

@author: harmonyl
"""
import random, threading, time, cv2

class buffer:
    def __init__ (self, size = 10):
        self.buffer = [None] * size
        self.beg = None
        self.end = None
        self.size = size
        self.lock = threading.Lock ()
        self.empty = threading.BoundedSemaphore (size)
        self.full = threading.Semaphore (0)

    def push (self, *args):
        for arg in args:
            if self.end == None:
                self.end = 0
                self.beg = 0

            if (self.end) == self.size:
                self.end = 0

            if (type (self.buffer [self.end]) != type (None)):
                raise IndexError ('Queue full!')

            self.buffer [self.end] = arg
            self.end += 1

    def put (self, arg):
        self.empty.acquire ()
        self.lock.acquire ()
        self.push (arg)
        self.lock.release ()
        self.full.release ()

    def pop (self):
        if (type (self.beg) == type (None)):
            raise IndexError ('Queue empty!')

        res = self.buffer [self.beg]
        self.buffer [self.beg] = None
        if (self.beg + 1) == self.size:
            self.beg = -1

        self.beg += 1
        if (type (self.buffer [self.beg]) == type (None)):
            self.beg = None
            self.end = None

        return res

    def take (self):
        self.full.acquire ()
        self.lock.acquire ()
        res = self.pop ()
        self.lock.release ()
        self.empty.release ()
        return res

    def print (self):
        res = []
        count = self.beg
        if self.end:
            while (len (res) < self.size and self.buffer [count] != None):       #  [0, 1, 2]
                res.append (self.buffer [count])
                count += 1
                if count == self.size:
                    count = 0

        print (res)
        return res

    def empty (self):
        return type (self.beg) == type (None)

    def tprint (self):
        print ("True: ", self.buffer)


def main () -> int:
    video_player ('clip.mp4')
    test = buffer ()
    test.push (1)
    return 0



def video_player (filename: str):
    def _extract_frames (fileName, outBuff, maxFramesToLoad=9999):
        # Initialize frame count
        count = 0

        # open video file
        vidcap = cv2.VideoCapture(fileName)

        # read first image
        success, image = vidcap.read ()

        print(f'Reading frame {count} {success}')
        while success and count < maxFramesToLoad:
            # get a jpg encoded frame
            success, jpgImage = cv2.imencode('.jpg', image)

            # add the frame to the buffer
            outBuff.put (image)

            success,image = vidcap.read()
            print(f'Reading frame {count} {success}')
            count += 1

        print('Frame extraction complete')

    def _conv_to_gray (inBuff, outBuff, maxFramesToLoad=9999):
        count = 0
        while (count < maxFramesToLoad):
            print(f'Converting frame {count}')
            gray_frame = cv2.cvtColor(inBuff.take (), cv2.COLOR_BGR2GRAY)

            outBuff.put (gray_frame)
            count += 1

        print('Frame conversion complete')

        '''
        # globals
        outputDir    = 'frames'

        # initialize frame count
        count = 0

        # get the next frame file name
        inFileName = f'{outputDir}/frame_{count:04d}.bmp'


        # load the next file
        inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

        while inputFrame is not None and count < 72:
            print(f'Converting frame {count}')

            # convert the image to grayscale
            grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)

            # generate output file name
            outFileName = f'{outputDir}/grayscale_{count:04d}.bmp'

            # write output file
            cv2.imwrite(outFileName, grayscaleFrame)

            count += 1

            # generate input file name for the next frame
            inFileName = f'{outputDir}/frame_{count:04d}.bmp'

            # load the next frame
            inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
            '''

    def _display_frames (inputBuffer, maxFramesToLoad=9999):
        # initialize frame count
        count = 0

        # go through each frame in the buffer until the buffer is empty
        while (count < maxFramesToLoad):
            # get the next frame
            frame = inputBuffer.take ()

            print(f'Displaying frame {count}')

            # display the image in a window called "video" and wait 42ms
            # before displaying the next frame
            cv2.imshow('Video', frame)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break

            count += 1

        print('Finished displaying all frames')
        # cleanup the windows
        cv2.destroyAllWindows()

    extract_buff = buffer (10)
    gray_buff = buffer (10)



    extract = threading.Thread (target=_extract_frames, args = ('clip.mp4', extract_buff, 200))
    gray = threading.Thread (target=_conv_to_gray, args = (extract_buff, gray_buff, 200))
    display = threading.Thread (target=_display_frames, args = (gray_buff, 200))

    extract.start ()
    gray.start ()
    display.start ()
    display.join ()

    # _extract_frames(filename, extract_buff, 72)
    return 0



def producer_consumer ():
    def _p ():
        nonlocal buff
        while 1:
            buff.empty.acquire ()
            frame = random.random () * 100
            buff.qlock.acquire ()
            buff.push (frame)
            buff.qlock.release ()
            buff.full.release ()
            time.sleep (.25)

    def _c ():
        nonlocal buff
        while 1:
            buff.full.acquire ()
            buff.qlock.acquire ()
            print ("Consumed: ", buff.pop ())
            buff.qlock.release ()
            buff.empty.release ()
            time.sleep (.5)

    buff = buffer ()

    produce = threading.Thread (target=_p)
    consume = threading.Thread (target=_c)
    produce.start ()
    consume.start ()

    while 1:
        buff.print ()
        time.sleep (1)
    return 0






















if __name__ == '__main__':
    main ()