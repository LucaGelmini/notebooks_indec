import kivy

kivy.require('2.0.0')

# base Class of your App inherits from the App class.
from kivy.app import App
# GridLayout arranges children in a matrix.
from kivy.uix.boxlayout import BoxLayout

class Contenedor_01(BoxLayout):
    None

class MainApp():
    title = "Hola Mundo"
    def build(self):
        return Contenedor_01()

if __name__ == '__main__':
    MainApp().run()