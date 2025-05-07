import speech_recognition as sr
from transformers import pipeline

# Carica il modello di analisi del sentiment
sentiment_pipeline = pipeline("sentiment-analysis")

# Funzione di analisi sentiment
def analyze_sentiment(audio_file):
    # Trascrizione dell'audio in testo
    transcript = transcribe_audio(audio_file)  # Funzione che converte l'audio in testo
    
    # Analisi sentimentale
    sentiment = sentiment_pipeline(transcript)
    return sentiment

def transcribe_audio(audio_file):
    # Crea un oggetto Recognizer
    recognizer = sr.Recognizer()
    
    # Carica il file audio
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)  # Legge tutto l'audio del file
    
    try:
        # Usa Google Web Speech API per trascrivere l'audio, specificando la lingua italiana
        print("Inizio trascrizione...")
        transcription = recognizer.recognize_google(audio, language="it-IT")  # Specifica lingua italiana
        print("Trascrizione completata: ", transcription)
        return transcription
    
    except sr.UnknownValueError:
        print("Google Speech Recognition non ha capito l'audio")
        return ""
    except sr.RequestError as e:
        print("Errore nel servizio di Google Speech Recognition; {0}".format(e))
        return ""

if __name__ == "__main__":
    # Usa il percorso completo del file audio su Windows accessibile da WSL
    audio_file_path = "/mnt/c/Users/rossi/Desktop/Pepper_Restart_Python2.7/test.wav"  # Percorso accessibile da WSL
    
    sentiment = analyze_sentiment(audio_file_path)  # Usa il file audio che desideri trascrivere
    print(f"Sentiment Analysis: {sentiment}")
