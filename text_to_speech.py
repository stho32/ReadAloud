import sys
import os
import traceback
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QTextEdit, QPushButton, QSplitter, QProgressBar,
                            QHBoxLayout, QSlider, QComboBox, QLabel)
from PyQt5.QtCore import Qt, QTimer
import pygame
import tempfile
from dotenv import load_dotenv
from openai import OpenAI
import httpx

class TextToSpeechApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.had_error = False  # Flag für aufgetretene Fehler
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
        
        # Oberer Bereich: Textfeld und Character Count
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Bitte Text zum Vorlesen hier einfügen...")
        self.text_edit.textChanged.connect(self.update_char_count)
        text_layout.addWidget(self.text_edit)
        
        # Character count label
        self.char_count_label = QLabel("Zeichen: 0")
        text_layout.addWidget(self.char_count_label)
        
        splitter.addWidget(text_widget)

        # Unterer Bereich: Log-Ausgabe
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText("Log-Ausgaben erscheinen hier...")
        splitter.addWidget(self.log_edit)

        # Größenverhältnis zwischen Text und Log setzen
        splitter.setSizes([400, 200])
        
        layout.addWidget(splitter)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Controls Layout
        controls_layout = QHBoxLayout()

        # Voice Selection
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
        controls_layout.addWidget(QLabel("Stimme:"))
        controls_layout.addWidget(self.voice_combo)

        # Volume Control
        controls_layout.addWidget(QLabel("Lautstärke:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.update_volume)
        controls_layout.addWidget(self.volume_slider)

        # Buttons
        button_layout = QHBoxLayout()
        self.read_button = QPushButton("Vorlesen")
        self.read_button.clicked.connect(self.read_text)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.read_button)
        button_layout.addWidget(self.stop_button)

        controls_layout.addLayout(button_layout)
        layout.addLayout(controls_layout)

        # Initialize playback state
        self.is_playing = False
        self.temp_files = []

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
                error_msg = "Kein OpenAI API-Key gefunden! Bitte setzen Sie die OPENAI_API_KEY Umgebungsvariable."
                self.log("FEHLER: " + error_msg)
                print("FEHLER: " + error_msg, file=sys.stderr)
                sys.exit(1)
            
            # Client mit HTTP-Client initialisieren
            http_client = httpx.Client()
            self.client = OpenAI(
                api_key=api_key,
                http_client=http_client
            )
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
        """Zeigt einen Fehlermeldung in der Konsole und loggt den kompletten Traceback"""
        self.had_error = True  # Setze Error-Flag
        error_msg = f"FEHLER: {title}\nDetails: {str(error)}"
        self.log("========================")
        self.log(error_msg)
        self.log("Traceback:")
        self.log(traceback.format_exc())
        self.log("========================")
        
        # Ausgabe in stderr
        print(error_msg, file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)

    def update_char_count(self):
        """Aktualisiert die Zeichenanzahl-Anzeige"""
        count = len(self.text_edit.toPlainText())
        self.char_count_label.setText(f"Zeichen: {count}")

    def update_volume(self):
        """Aktualisiert die Lautstärke"""
        volume = self.volume_slider.value() / 100.0
        pygame.mixer.music.set_volume(volume)

    def stop_playback(self):
        """Stoppt die Wiedergabe"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.stop_button.setEnabled(False)
            self.read_button.setEnabled(True)
            self.read_button.setText("Vorlesen")
            self.progress_bar.setVisible(False)
            self.log("Wiedergabe gestoppt.")

    def read_text(self):
        """Liest den eingegebenen Text vor"""
        text = self.text_edit.toPlainText().strip()
        
        if not text:
            warning_msg = "WARNUNG: Kein Text zum Vorlesen eingegeben."
            self.log(warning_msg)
            print(warning_msg, file=sys.stderr)
            return

        self.read_button.setEnabled(False)
        self.read_button.setText("Lese vor...")
        self.stop_button.setEnabled(True)
        self.is_playing = True
        self.log("\nStarte Vorlesevorgang...")
        
        try:
            # Text in Abschnitte aufteilen
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            self.log(f"Text in {len(chunks)} Abschnitte aufgeteilt.")
            
            # Progress Bar einrichten
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(chunks))
            self.progress_bar.setValue(0)
            
            selected_voice = self.voice_combo.currentText().lower()
            
            # Temporäre Dateien für jeden Chunk erstellen und abspielen
            for i, chunk in enumerate(chunks):
                if not self.is_playing:
                    self.log("Vorlesevorgang wurde abgebrochen.")
                    break
                
                # TTS-Anfrage an OpenAI
                self.log("Sende Anfrage an OpenAI TTS API...")
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=selected_voice,
                    input=chunk
                )
                
                temp_file_path = os.path.join(tempfile.gettempdir(), f"tts_chunk_{i}.mp3")
                self.temp_files.append(temp_file_path)
                
                try:
                    self.log(f"Schreibe Audio in temporäre Datei: {temp_file_path}")
                    with open(temp_file_path, 'wb') as f:
                        f.write(response.content)
                    
                    if not os.path.exists(temp_file_path):
                        raise FileNotFoundError(f"Temporäre Datei wurde nicht erstellt: {temp_file_path}")
                    
                    file_size = os.path.getsize(temp_file_path)
                    self.log(f"Temporäre Datei erstellt, Größe: {file_size} Bytes")
                    
                    if file_size == 0:
                        raise ValueError("Temporäre Audiodatei ist leer")
                    
                    if not self.is_playing:
                        break
                        
                    # Audio abspielen
                    self.log("Lade Audiodatei...")
                    pygame.mixer.music.load(temp_file_path)
                    pygame.mixer.music.set_volume(self.volume_slider.value() / 100.0)
                    self.log("Starte Wiedergabe...")
                    pygame.mixer.music.play()
                    
                    # Warten bis die Wiedergabe beendet ist
                    while pygame.mixer.music.get_busy() and self.is_playing:
                        pygame.time.Clock().tick(10)
                        QApplication.processEvents()
                    
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
            self.is_playing = False
            self.read_button.setEnabled(True)
            self.read_button.setText("Vorlesen")
            self.stop_button.setEnabled(False)
            self.progress_bar.setVisible(False)

    def closeEvent(self, event):
        """Wird beim Schließen der Anwendung aufgerufen"""
        if self.had_error:
            sys.exit(1)
        event.accept()

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = TextToSpeechApp()
        window.show()
        exit_code = app.exec_()
        # Wenn ein Fehler aufgetreten ist, beende mit Exit-Code 1
        if window.had_error:
            sys.exit(1)
        sys.exit(exit_code)
    except Exception as e:
        print(f"KRITISCHER FEHLER: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
