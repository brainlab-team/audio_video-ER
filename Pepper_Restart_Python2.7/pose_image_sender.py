# -*- coding: utf-8 -*-
import sys
import struct
import socket
import numpy as np
import cv2
from naoqi import ALProxy
import time

PEPPER_IP = "172.16.53.202"    # IP di Pepper
PEPPER_PORT = 9559             # Porta NAOqi di Pepper
ROS_IP = "172.31.241.133"  # IP del PC ROS2 destinatario
ROS_PORT  = 5001               # Porta socket in ascolto sul PC ROS2

# Connessione al servizio video di Pepper
try:
    videoDevice = ALProxy("ALVideoDevice", PEPPER_IP, PEPPER_PORT)
except Exception as e:
    print("Errore di connessione a Pepper:", e)
    sys.exit(1)

# Parametri videocamera Pepper
AL_kTopCamera     = 0   # Camera superiore (0) di Pepper
AL_kQVGA          = 1   # Risoluzione 320x240 pixels
AL_kBGRColorSpace = 13  # Colori BGR (necessario per compatibilità OpenCV)

# Iscrizione alla camera
captureDevice = None
try:
    captureDevice = videoDevice.subscribeCamera("pepper_stream", AL_kTopCamera,
                                               AL_kQVGA, AL_kBGRColorSpace, 10)
except Exception as e:
    print("Impossibile iscriversi alla camera:", e)
    sys.exit(1)

# Connessione socket al server ROS2
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((ROS_IP, ROS_PORT))
    print("Connesso al receiver ROS2 su {}:{}".format(ROS_IP, ROS_PORT))
except Exception as e:
    print("Errore di connessione socket verso ROS2:", e)
    videoDevice.unsubscribe(captureDevice)
    sys.exit(1)

def capture_image():
    result = videoDevice.getImageRemote(captureDevice)
    if result is None:
        print("Nessuna immagine ricevuta da Pepper")
        return None
    width, height = result[0], result[1]
    image_data = result[6]
    if image_data is None:
        print("Dato immagine vuoto")
        return None

    # Converte i byte grezzi in un array NumPy BGR
    frame = np.frombuffer(image_data, dtype=np.uint8)
    try:
        frame = frame.reshape((height, width, 3))
    except Exception as e:
        print("Errore nel reshape dell'immagine:", e)
        return None

    return frame

def send_image(image):
    try:
        if image is None:
            print("Errore: nessuna immagine acquisita.")
            return
        
        # Codifica l'immagine in JPEG
        success, encoded_image = cv2.imencode('.jpg', image)
        if not success or encoded_image is None:
            print("Errore nella codifica JPEG del frame")
            return
        img_bytes = encoded_image.tobytes()  # Ottiene bytes

        # Invia prima la lunghezza dell'immagine (4 byte, network order)
        length = len(img_bytes)
        print("Invio immagine di lunghezza: {} bytes".format(len(img_bytes)))

        # Suddividi in pacchetti
        packet_size = 1024  # Dimensione del pacchetto
        num_packets = (length // packet_size) + 1
        print("Lunghezza totale immagine: {}, numero di pacchetti: {}".format(length, num_packets))

        # Invia la lunghezza totale dell'immagine
        sock.sendall(struct.pack('!I', length))

        # Invia i pacchetti uno per uno
        for i in range(num_packets):
            start = i * packet_size
            end = start + packet_size
            packet = img_bytes[start:end]

            sock.sendall(packet)
            print("Inviato pacchetto {} di {}".format(i + 1, num_packets))

            # Attendere conferma di ricezione per ogni pacchetto
            ack = sock.recv(4)  # Riceve 4 byte di conferma
            if ack != b'ACK':
                print("Errore: pacchetto {} non ricevuto correttamente".format(i + 1))
                break

        print("Immagine inviata con successo!")

    except Exception as e:
        print("Errore nell'invio dell'immagine: {}".format(e))

# Funzione per scattare automaticamente 4 frame ogni secondo, salvarli e inviarli
def capture_and_send_frames(num_frames=1, interval=1):
    time.sleep(6)
    for i in range(num_frames):
        image = capture_image()  # Acquisisci l'immagine
        if image is not None:
            # Salva ogni frame con un nome diverso
            frame_filename = "frame_{}.jpg".format(i + 1)  # Usa .format invece di f-string
            cv2.imwrite(frame_filename, image)
            print("Immagine salvata come {}".format(frame_filename))
            send_image(image)  # Invia immagine
        time.sleep(interval)  # Aspetta 1 secondo prima di scattare il prossimo frame

if __name__ == "__main__":
    capture_and_send_frames()  # Scatta 4 frame e inviali
