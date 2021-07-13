import asyncio
import zmq
from zmq.asyncio import Context
import xdrlib
import numpy as np
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
import threading
import signal
import sys

ctx = Context.instance()
data_packer = xdrlib.Packer()
data_unpacker = xdrlib.Unpacker(b'')

DTYPES = {
    1: np.int64,
    2: np.float64,
}

class PyQtMainWindow(QMainWindow):
    def __init__(self):
        self.resolutionX = 1920
        self.resolutionY = 1080
        QMainWindow.__init__(self)
        self.resize(self.resolutionX, self.resolutionY)
        self.showFullScreen()
        self.setStyleSheet("""
            color:white; 
            background:black;
        """) 

        vBox = QWidget(self)
        self.setCentralWidget(vBox);
        vBoxLayout = QVBoxLayout(self)
        vBox.setLayout(vBoxLayout)
        vBoxLayout.setAlignment(QtCore.Qt.AlignCenter)

        vBoxLayout.addStretch()
        self.maskStateLabel = QLabel()
        self.maskStateLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.maskStateLabel.setText("No information from ML module")
        self.maskStateLabel.setFont(QFont("Monaco", 50))
        self.maskStateLabel.setStyleSheet("""
            border-bottom: 3px solid white;
        """)
        self.maskStateLabel.setFixedWidth(int(self.resolutionX/2))
        vBoxLayout.addWidget(self.maskStateLabel)

        self.maskPercentageLabel = QLabel()
        self.maskPercentageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.maskPercentageLabel.setText("")
        self.maskPercentageLabel.setFont(QFont("Monaco", 30))
        vBoxLayout.addWidget(self.maskPercentageLabel)

        vBoxLayout.addStretch()
        self.show()

        self.startThread()


    def startThread(self):
        self.thread = connectionThread()
        self.thread.receivedDistance.connect(self.updateMaskData)
        self.thread.start()

    def updateMaskData(self, certainty, state):
        if True: # todo: check if mask is on
            self.maskStateLabel.setText("Mask detected!")
        elif False:
            self.maskStateLabel.setText("No mask detected!")
        
        self.maskPercentageLabel.setText(f"Certainty: {certainty}%")


class connectionThread(QThread):
    receivedDistance = pyqtSignal(int)
    receivedMaskCertainty = pyqtSignal(int, float)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        asyncio.run(self.listen())

    async def listen(self):
        consumer_socket = ctx.socket(zmq.SUB)
        topic_filter = 10001
        data_packer.pack_uint(topic_filter)
        consumer_socket.setsockopt(zmq.SUBSCRIBE, data_packer.get_buffer())
        consumer_socket.connect('tcp://127.0.0.1:5556')
        while True:
            msg = await consumer_socket.recv()
            data_unpacker.reset(msg)
            topic = data_unpacker.unpack_uint()
            if topic == 10001:
                array_shape = data_unpacker.unpack_array(data_unpacker.unpack_uint)
                array_data_type = data_unpacker.unpack_uint()
                data = data_unpacker.unpack_bytes()
                arr = np.frombuffer(
                    data,
                    dtype=DTYPES[array_data_type]
                ).reshape(array_shape)
                print('received')
                print(topic)
                print(arr)
                self.receivedMaskCertainty.emit(arr[0], arr[1])
        consumer_socket.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWin = PyQtMainWindow()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit( app.exec_() )

if __name__ == "__main__":
    main()
