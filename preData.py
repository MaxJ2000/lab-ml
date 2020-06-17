import os, re, time
import threading, queue
import random
from PIL import Image


def process(label, path):
    testDir='./data/TEST'
    trainDir='./data/TRAIN'
    newTestDir='{}/{}'.format(testDir,label)
    newTrainDir='{}/{}'.format(trainDir,label)
    newTestPath='{}/{}'.format(newTestDir,os.path.basename(path[0]).split('.')[0]+'.jpg')
    os.mkdir(newTrainDir)
    os.mkdir(newTestDir)
    img=Image.open(path[0])
    img.save(newTestPath)
    for f in path[1:]:
        newTrainPath='{}/{}'.format(newTrainDir,os.path.basename(f).split('.')[0]+'.jpg')
        img=Image.open(f)
        img.save(newTrainPath)


lock = threading.Lock()
flag = False


class Worker(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q

    def run(self):
        while 1:
            if not self.q.empty():
                lock.acquire()
                label, path = self.q.get()
                lock.release()
                process(label, path)
            else:
                time.sleep(1)
            if flag:
                break


def pre_data():
    trainDir = './data/TRAIN'
    testDir = './data/TEST'
    if not os.path.exists(trainDir):
        os.makedirs(trainDir)
        os.makedirs(testDir)
    else:
        print('pre data exists!')
        return
    dataDir = './64_CASIA-FaceV5'
    data = list()
    for classDir in  os.listdir(dataDir):
        label=classDir
        classDir=os.path.join(dataDir,classDir)
        if not os.path.isdir(classDir):
            continue
        imgPaths=list()
        for imgPath in [os.path.join(classDir, f) for f in os.listdir(classDir) if
                         re.match(r'.*\.(jpg|jpeg|png|bmp)', f, flags=re.I)]:
            imgPaths.append(imgPath)
        random.shuffle(imgPaths)
        data.append([label,imgPaths])
    Q = queue.Queue()
    for label, path in data:
        Q.put([label, path])
    ws = list()
    for j in range(100):
        w = Worker(Q)
        w.start()
        ws.append(w)
    while not Q.empty():
        pass
    print('empty queue!')
    for w in ws:
        w.join()
    global flag
    flag = True
    print('work over!!!')


if __name__ == "__main__":
    pre_data()
