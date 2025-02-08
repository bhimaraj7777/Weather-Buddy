import sys
import requests
import speech_recognition as sr
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from googletrans import Translator
from gtts import gTTS
import os
import pygame
import time  # Add this import

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name:", self)
        self.city_input = QLineEdit(self)
        self.language_label = QLabel("Select language:", self)
        self.language_combo = QComboBox(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.speak_button = QPushButton("Repeat Instructions", self)
        self.mic_button = QPushButton("🎤", self)
        self.teamperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.initUI()

        self.translator = Translator()
        self.recognizer = sr.Recognizer()

        self.initialize_mixer()

        self.speak("Welcome to the Weather buddy! Please enter a city name and select your language.")

    def initialize_mixer(self):
        """Initialize the pygame mixer."""
        try:
            pygame.mixer.init()
            if not pygame.mixer.get_init():
                raise Exception("Failed to initialize pygame.mixer")
        except Exception as e:
            print(f"Error initializing pygame.mixer: {e}")
            self.display_error("Audio playback is not available. Please check your audio settings.")

    def initUI(self):
        self.setWindowTitle("Weather buddy")

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.mic_button)
        vbox.addWidget(self.language_label)
        vbox.addWidget(self.language_combo)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.speak_button)
        vbox.addWidget(self.teamperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.language_combo.addItems(["English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese"])
        self.language_combo.setCurrentText("English")

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.teamperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.speak_button.setObjectName("speak_button")
        self.mic_button.setObjectName("mic_button")
        self.teamperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
            QLabel, QPushButton {
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#city_label {
                font-size: 40px;
                font-style: italic;
                font-weight: bold;
                color: #2c3e50;
            }
            QLineEdit#city_input {
                font-size: 40px;
                font-family: 'Segoe UI', sans-serif;
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
            QPushButton#get_weather_button {
                font-size: 40px;
                font-weight: bold;
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton#speak_button {
                font-size: 30px;
                font-weight: bold;
                background-color: lightblue;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton#mic_button {
                font-size: 60px;  /* Larger font size for the emoji */
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff7e5f, stop:1 #feb47b);  /* Gradient background */
                color: white;
                padding: 20px;
                border-radius: 50px;  /* Circular button */
                border: 3px solid #ff6f61;  /* Border */
            }
            QPushButton#mic_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #feb47b, stop:1 #ff7e5f);  /* Gradient on hover */
                border: 3px solid #ff3b2f;  /* Border color on hover */
            }
            QLabel#temperature_label {
                font-size: 75px;
                color: #e74c3c;
            }
            QLabel#emoji_label {
                font-size: 100px;
                font-family: 'Segoe UI Emoji';
            }
            QLabel#description_label {
                font-size: 50px;
                color: #27ae60;
            }
        """)
        self.get_weather_button.clicked.connect(self.get_weather)
        self.speak_button.clicked.connect(self.speak_instructions)
        self.mic_button.clicked.connect(self.use_mic)

    def speak(self, text):
        """Speak the given text using gTTS."""
        try:
            
            if not pygame.mixer.get_init():
                self.initialize_mixer()

            selected_language = self.language_combo.currentText()
            language_code = self.get_language_code(selected_language)
            tts = gTTS(text=text, lang=language_code)
            tts.save("temp.mp3")

            
            pygame.mixer.music.load("temp.mp3")
            pygame.mixer.music.play()

            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  
            
            pygame.mixer.music.stop()
            pygame.mixer.quit()

            
            time.sleep(0.1)  

            if os.path.exists("temp.mp3"):
                os.remove("temp.mp3")
        except Exception as e:
            print(f"Error in speak method: {e}")

    def speak_instructions(self):
        """Speak the initial instructions."""
        self.speak("Welcome to the Weather buddy! Please enter a city name and select your language.")

    def use_mic(self):
        """Capture audio input and set it as the city name."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                self.speak("Please say the city name.")
                audio = self.recognizer.listen(source)
                city = self.recognizer.recognize_google(audio)
                self.city_input.setText(city)
                self.speak(f"You said: {city}")
        except sr.UnknownValueError:
            self.display_error("Sorry, I could not understand the audio.")
        except sr.RequestError:
            self.display_error("Sorry, there was an issue with the speech recognition service.")
        except Exception as e:
            self.display_error(f"An error occurred: {e}")

    def get_weather(self):
        api_key = "7497f5bd3a3bed0f5ea540f5b87c1c49"
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)
                self.speak_weather(data)
            else:
                self.display_error(f"Error: {data.get('message', 'Unknown error')}")

        except requests.exceptions.HTTPError as http_error:
            self.display_error(f"HTTP error occurred: {http_error}")
        except Exception as e:
            self.display_error(f"An error occurred: {e}")

    def display_weather(self, data):
        self.teamperature_label.setStyleSheet("font-size: 75px;")
        temperature_k = data["main"]["temp"]
        temperature_f = (temperature_k * 9 / 5) - 459.67
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]

        self.teamperature_label.setText(f"{temperature_f:.0f}°F")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description)

    def speak_weather(self, data):
        temperature_k = data["main"]["temp"]
        temperature_f = (temperature_k * 9 / 5) - 459.67
        weather_description = data["weather"][0]["description"]

        selected_language = self.language_combo.currentText()
        language_code = self.get_language_code(selected_language)
        translated_description = self.translate_text(weather_description, language_code)

        speech_text = f"The temperature in {self.city_input.text()} is {temperature_f:.0f} degrees Fahrenheit with {translated_description}."

        self.speak(speech_text)

    def translate_text(self, text, dest_language):
        """Translate text to the selected language."""
        try:
            translated = self.translator.translate(text, dest=dest_language)
            return translated.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def get_language_code(self, language):
        """Map language names to language codes."""
        language_map = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Hindi": "hi",
            "Chinese": "zh-cn",
            "Japanese": "ja",
            "kannada": "kn"
        }
        return language_map.get(language, "en")

    def display_error(self, message):
        """Display an error message in a QMessageBox."""
        QMessageBox.critical(self, "Error", message)

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "☃️"
        elif 701 <= weather_id <= 781:
            return "༄"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🍃"
        elif weather_id == 800:
            return "🌞"
        elif weather_id == 801:
            return "🌤️"
        else:
            return ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())