# -*- coding: utf-8 -*- 

import qi
import paramiko
from naoqi import ALProxy
import time
import os

# ✅ Password SSH di default (usa con attenzione in ambienti di produzione)
DEFAULT_SSH_PASSWORD = "cais"

def registra_audio_pepper(session, durata=10, destinazione_locale=r"C:\Users\rossi\Desktop\Pepper_Restart_Python2.7\test.wav"):
    """
    Funzione per registrare audio da Pepper utilizzando il servizio ALAudioRecorder
    e salvarlo direttamente sul PC locale.
    """
    try:
        print("Avvio registrazione audio da Pepper...")

        # Connessione al servizio ALAudioRecorder di Pepper
        AR = ALProxy("ALAudioRecorder", "pepper.local", 9559)

        # Percorso del file sul robot (remoto)
        percorso_remoto = "/data/home/nao/recordings/microphones/temp_test.wav"

        try:
            AR.stopMicrophonesRecording()
            print("Registrazione precedente fermata.")
        except Exception:
            print("Nessuna registrazione in corso. Procedo con la registrazione...")

        AR.startMicrophonesRecording(percorso_remoto, "wav", 16000, [0, 0, 1, 0])
        print("Registrazione in corso per {} secondi...".format(durata))
        time.sleep(durata)
        AR.stopMicrophonesRecording()
        print("Registrazione completata!")

        salva_file_locale(percorso_remoto, destinazione_locale)
        rimuovi_file_da_pepper(percorso_remoto)

        if os.path.exists(destinazione_locale):
            print("[✔] File audio salvato in locale: {}".format(destinazione_locale))
        else:
            print("[✘] ATTENZIONE: File non trovato dopo il trasferimento!")

    except Exception as e:
        print("Errore nella registrazione audio: {}".format(e))

def salva_file_locale(percorso_remoto, destinazione_locale):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("172.16.53.202", username="nao", password=DEFAULT_SSH_PASSWORD)

        scp = paramiko.SFTPClient.from_transport(ssh.get_transport())
        scp.get(percorso_remoto, destinazione_locale)
        scp.close()
        print("File trasferito da {} a {}".format(percorso_remoto, destinazione_locale))
    except Exception as e:
        print("Errore nel salvataggio del file: {}".format(e))

def rimuovi_file_da_pepper(percorso_remoto):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("172.16.53.202", username="nao", password=DEFAULT_SSH_PASSWORD)
        ssh.exec_command("rm {}".format(percorso_remoto))
        ssh.close()
        print("File {} rimosso da Pepper.".format(percorso_remoto))
    except Exception as e:
        print("Errore nella rimozione del file: {}".format(e))

if __name__ == "__main__":
    try:
        ip_pepper = "172.16.53.202"
        port_pepper = 9559

        app = qi.Application(["Test", "--qi-url=tcp://{}:{}".format(ip_pepper, port_pepper)])
        app.start()
        session = app.session

        print("Connesso a Pepper!")
        registra_audio_pepper(session)

    except Exception as e:
        print("Errore di connessione: {}".format(e))