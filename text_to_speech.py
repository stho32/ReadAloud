import sys
import os
import traceback
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QTextEdit, QPushButton, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt
from openai import OpenAI
import pygame
import tempfile
from dotenv import load_dotenv

class TextToSpeechApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_openai()
        self.init_audio()

    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setWindowTitle("Text Vorlesen")
        self.setGeometry(100, 100, 800, 600)

        # Hauptwidget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Splitter für Text und Log
        splitter = QSplitter(Qt.Vertical)
        
        # Oberer Bereich: Textfeld
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Bitte Text zum Vorlesen hier einfügen...")
        splitter.addWidget(self.text_edit)

        # Unterer Bereich: Log-Ausgabe
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText("Log-Ausgaben erscheinen hier...")
        splitter.addWidget(self.log_edit)

        # Größenverhältnis zwischen Text und Log setzen
        splitter.setSizes([400, 200])
        
        layout.addWidget(splitter)

        # Vorlesen-Button
        self.read_button = QPushButton("Vorlesen")
        self.read_button.clicked.connect(self.read_text)
        layout.addWidget(self.read_button)

    def log(self, message):
        """Fügt eine Nachricht zum Log hinzu"""
        self.log_edit.append(message)
        # Scrolle automatisch nach unten
        self.log_edit.verticalScrollBar().setValue(
            self.log_edit.verticalScrollBar().maximum()
        )
        # Aktualisiere die GUI
        QApplication.processEvents()

    def init_openai(self):
        """Initialisiert den OpenAI Client"""
        try:
            self.log("Initialisiere OpenAI Client...")
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                self.log("FEHLER: Kein OpenAI API-Key gefunden!")
                QMessageBox.critical(
                    self,
                    "Fehler",
                    "Kein OpenAI API-Key gefunden! Bitte setzen Sie die OPENAI_API_KEY Umgebungsvariable."
                )
                sys.exit(1)
                
            self.client = OpenAI(api_key=api_key)
            self.log("OpenAI Client erfolgreich initialisiert.")
        except Exception as e:
            self.log(f"FEHLER bei OpenAI Initialisierung: {str(e)}")
            self.show_error("OpenAI Initialisierungsfehler", e)

    def init_audio(self):
        """Initialisiert das Audio-System"""
        try:
            self.log("Initialisiere Audio-System...")
            pygame.mixer.init()
            self.log("Audio-System erfolgreich initialisiert.")
        except Exception as e:
            self.log(f"FEHLER bei Audio-Initialisierung: {str(e)}")
            self.show_error("Audio-Initialisierungsfehler", e)

    def show_error(self, title, error):
        """Zeigt einen Fehlerdialog und loggt den kompletten Traceback"""
        self.log("========================")
        self.log(f"FEHLER: {title}")
        self.log(f"Details: {str(error)}")
        self.log("Traceback:")
        self.log(traceback.format_exc())
        self.log("========================")
        
        QMessageBox.critical(self, title, f"{str(error)}")

    def read_text(self):
        """Liest den eingegebenen Text vor"""
        text = self.text_edit.toPlainText().strip()
        
        if not text:
            self.log("WARNUNG: Kein Text zum Vorlesen eingegeben.")
            QMessageBox.warning(self, "Warnung", "Bitte geben Sie erst einen Text ein.")
            return

        self.read_button.setEnabled(False)
        self.read_button.setText("Lese vor...")
        self.log("\nStarte Vorlesevorgang...")
        
        try:
            # Text in Abschnitte aufteilen
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            self.log(f"Text in {len(chunks)} Abschnitte aufgeteilt.")
            
            # Wähle zufällige Stimme
            voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            selected_voice = random.choice(voices)
            self.log(f"Gewählte Stimme: {selected_voice}")
            
            for i, chunk in enumerate(chunks, 1):
                self.log(f"\nVerarbeite Abschnitt {i} von {len(chunks)}...")
                
                # TTS-Anfrage an OpenAI
                self.log("Sende Anfrage an OpenAI TTS API...")
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=selected_voice,
                    input=chunk
                )
                self.log("Audio-Antwort von OpenAI erhalten.")
                
                # Temporäre Datei für Audio erstellen
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, f"readaloud_temp_{i}.mp3")
                
                try:
                    self.log(f"Schreibe Audio in temporäre Datei: {temp_file_path}")
                    response.stream_to_file(temp_file_path)
                    
                    # Warte kurz und prüfe, ob die Datei existiert
                    if not os.path.exists(temp_file_path):
                        raise FileNotFoundError(f"Temporäre Datei wurde nicht erstellt: {temp_file_path}")
                    
                    # Prüfe die Dateigröße
                    file_size = os.path.getsize(temp_file_path)
                    self.log(f"Temporäre Datei erstellt, Größe: {file_size} Bytes")
                    
                    if file_size == 0:
                        raise ValueError("Temporäre Audiodatei ist leer")
                    
                    # Audio abspielen
                    self.log("Lade Audiodatei...")
                    pygame.mixer.music.load(temp_file_path)
                    self.log("Starte Wiedergabe...")
                    pygame.mixer.music.play()
                    
                    # Warten bis die Wiedergabe beendet ist
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                        QApplication.processEvents()  # Halte GUI reaktionsfähig
                    
                finally:
                    # Aufräumen
                    pygame.mixer.music.unload()
                    self.log("Lösche temporäre Audiodatei...")
                    try:
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                            self.log("Temporäre Audiodatei gelöscht.")
                        else:
                            self.log("Temporäre Datei existiert nicht mehr.")
                    except Exception as e:
                        self.log(f"WARNUNG: Konnte temporäre Datei nicht löschen: {str(e)}")

            self.log("\nVorlesevorgang abgeschlossen.")

        except Exception as e:
            self.show_error("Fehler beim Vorlesen", e)
        finally:
            self.read_button.setEnabled(True)
            self.read_button.setText("Vorlesen")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextToSpeechApp()
    window.show()
    sys.exit(app.exec_())
