# ReadAloud - Text-to-Speech Anwendung

Eine einfache Desktop-Anwendung, die Text mithilfe der OpenAI Text-to-Speech API vorliest.

## Features

- Benutzerfreundliche grafische Oberfläche
- Unterstützung für lange Texte durch automatische Aufteilung
- Hochqualitative Sprachsynthese durch OpenAI's TTS-API
- Sichere API-Key-Verwaltung über Umgebungsvariablen

## Voraussetzungen

- Python 3.8 oder höher
- OpenAI API-Key
- Windows-Betriebssystem

## Installation

1. Repository klonen oder Dateien herunterladen

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

3. Umgebungsvariablen konfigurieren:
   - Kopieren Sie `.env.example` zu `.env`
   - Öffnen Sie `.env` und fügen Sie Ihren OpenAI API-Key ein:
```
OPENAI_API_KEY=Ihr-API-Key-hier
```

## Verwendung

1. Starten Sie die Anwendung:
```bash
python text_to_speech.py
```

2. Fügen Sie Text in das Textfeld ein

3. Klicken Sie auf "Vorlesen", um den Text vorlesen zu lassen

## Technische Details

Die Anwendung verwendet:
- PyQt6 für die Benutzeroberfläche
- OpenAI API (tts-1 Modell) für Text-to-Speech
- pygame für die Audio-Wiedergabe
- python-dotenv für die Verwaltung von Umgebungsvariablen

## Fehlerbehebung

### Häufige Probleme

1. **"Kein OpenAI API-Key gefunden"**
   - Stellen Sie sicher, dass die `.env` Datei existiert
   - Überprüfen Sie, ob der API-Key korrekt eingetragen ist

2. **Audio-Wiedergabe funktioniert nicht**
   - Stellen Sie sicher, dass Ihre Audiogeräte korrekt funktionieren
   - Überprüfen Sie die Systemlautstärke

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## Hinweise

- Die OpenAI API ist kostenpflichtig. Informieren Sie sich über die aktuellen Preise auf der OpenAI-Website.
- Die Anwendung benötigt eine aktive Internetverbindung.
- Große Texte werden automatisch in kleinere Abschnitte aufgeteilt.
