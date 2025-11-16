# main.py - Android APK
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import threading
import os

class NinjaApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        btn1 = Button(text='INJECT PAYLOAD', background_color=(0,1,0,1))
        btn2 = Button(text='INSTALL CFW', background_color=(0,1,0,1))
        btn3 = Button(text='ENABLE PROXY', background_color=(0,1,0,1))
        layout.add_widget(btn1); layout.add_widget(btn2); layout.add_widget(btn3)
        btn1.bind(on_press=lambda x: os.system("python server.py &"))
        return layout

if __name__ == '__main__':
    NinjaApp().run()
