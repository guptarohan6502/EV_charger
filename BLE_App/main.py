from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.toast import toast
from jnius import autoclass
from android.permissions import request_permissions, Permission

layout = '''
BoxLayout:
    id: boxlayout
    orientation:'vertical'
    adaptive_size: True

    MDIconButton:
        icon: "bluetooth"
        pos_hint: {'center_x':0.5,'center_y':0.875}
        user_font_size: "40sp"
        on_release: app.android_bluetooth.getAndroidBluetoothSocket('rasp')
'''

class AndroidBluetoothClass:

    def getAndroidBluetoothSocket(self,DeviceName):
        toast("AndroidBluetoothSocket")
        print("AndroidBluetoothSocket")
        paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        socket = None
        for device in paired_devices:
            if device.getName() == DeviceName:
                socket = device.createRfcommSocketToServiceRecord(
                    self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                self.ReceiveData = self.BufferReader(self.InputStream(socket.getInputStream()))
                self.SendData = socket.getOutputStream()
                socket.connect()
                self.ConnectionEstablished = True
                print('Bluetooth Connection successful')
                toast("Bluetooth Connection successful")

        return self.ConnectionEstablished


    def BluetoothSend(self, Message, *args):
        toast("Bluetooth send")
        print("Bluetooth send")
        if self.ConnectionEstablished == True:
            self.SendData.write(Message)
        else:
            print('Bluetooth device not connected')


    def BluetoothReceive(self,*args):
        toast("Bluetooth receive")
        print("Bluetooth receive")
        DataStream = ''
        if self.ConnectionEstablished == True:
            DataStream = str(self.ReceiveData.readline())
        return DataStream

    def __init__(self):
        toast("Bluetooth init")
        print("Bluetooth init")
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')
        self.BufferReader = autoclass('java.io.BufferedReader')
        self.InputStream = autoclass('java.io.InputStreamReader')
        self.ConnectionEstablished = False
        toast("Bluetooth init finish")
        print("Bluetooth init finish")


    def __del__(self):
        toast("Bluetooth del")
        print('class AndroidBluetooth destroyer')

class TestApp(MDApp):

    def build(self):
        request_permissions([Permission.BLUETOOTH_ADMIN,
                             Permission.BLUETOOTH, Permission.BLUETOOTH_ADVERTISE ,  Permission.BLUETOOTH_CONNECT ,  Permission.BLUETOOTH_SCAN ])  # get the permissions needed
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.android_bluetooth = AndroidBluetoothClass()
        return Builder.load_string(layout)

TestApp().run()
