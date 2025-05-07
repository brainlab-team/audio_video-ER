PREMESSA:
I CODICI USATI SONO IN QUESTO PATH:
.\ros2_ws\src

Descrizione del Progetto
Questo progetto integra il robot Pepper con un sistema che registra l'audio, analizza le emozioni facciali e la postura, e invia i dati a un sistema ROS2. Il progetto è suddiviso in moduli, alcuni dei quali sono eseguiti esternamente a WSL e altri internamente a WSL (in particolare dove abbiamo avuto necessità di usare Python2.7 abbiamo lavorato esterni a WSL, mentre per tutto ciò che riguarda l'esecuzione concreta delle attività di elaborazione del flusso, usando python3.12 abbiamo lavorato in WSL(con ROS2).


Moduli del progetto, Moduli Esterni a WSL:

pepper_audio_server.py

Questo script è eseguito all'esterno di WSL, direttamente sul sistema operativo Windows.

La funzione di questo modulo è quella di registrare l'audio tramite il microfono di Pepper, utilizzando il servizio ALAudioRecorder di Pepper. L'audio registrato viene salvato in un file .wav sulla macchina locale di Windows.

Il file audio registrato viene successivamente trasferito dal robot al PC usando SSH e SCP.

pose_image_sender.py

Questo script è anche eseguito all'esterno di WSL, sulla macchina Windows.

La funzione di questo modulo è quella di acquisire immagini dalla fotocamera di Pepper e di inviarle a un server in esecuzione all'interno di WSL. Viene utilizzato il servizio di video streaming di Pepper.

Le immagini vengono inviate via socket a un server ROS2 che si trova dentro WSL per essere elaborate.

Moduli Interni a WSL
pose_image_receiver.py

Questo script è eseguito all'interno di WSL.

La funzione di questo modulo è quella di ricevere le immagini inviate dal modulo "pose_image_sender.py". Le immagini vengono ricevute tramite socket e decodificate utilizzando OpenCV.

Una volta ricevute e decodificate, le immagini vengono pubblicate su un topic ROS2 per l'elaborazione futura.

sentiment_analysis.py

Questo script è eseguito internamente a WSL.

La funzione di questo modulo è quella di analizzare le emozioni rilevate dalle immagini acquisite. L'analisi del sentimento si basa sul testo estratto dalle emozioni facciali di Pepper e l'output viene pubblicato su un topic ROS2.

Passaggi per l'Esecuzione
1. Preparazione dell'Ambiente
Assicurarsi che WSL (Windows Subsystem for Linux) sia installato e configurato con una distribuzione Ubuntu (consigliata la versione 22.04 o superiore).

Installare le dipendenze necessarie:

ROS2 (versione Noetic o compatibile).

Python 3 e Python 2.7.

Paramiko e altre librerie necessarie (es. cv_bridge, OpenCV).

Le librerie di Machine Learning necessarie per l'analisi delle emozioni facciali (es. MediaPipe, FER).

2. Configurazione del Sistema
Avviare i moduli esterni:

pepper_audio_server.py per la registrazione audio.

pose_image_sender.py per l'acquisizione e invio delle immagini da Pepper (NOTA BENE: PRIMA DI LANCIARE IL SENDER, ASSICURARSI DI LANCIARE IL RECEIVER!!!!! SE NON C'è PRIMA IL RECEIVER IN ASCOLTO, IL SENDER OVVIAMENTE NON INVIA!!!!! )

Avviare i moduli interni a WSL:

pose_image_receiver.py per ricevere le immagini e gestirle su ROS2.

sentiment_analysis.py per l'analisi delle emozioni facciali.

3. Esecuzione del Flusso
Dopo aver configurato l'ambiente, puoi avviare tutto il flusso :
registra audio!
avvia Receiver,
avvia sender,


La registrazione audio (salvando e trasferendo il file audio da Pepper al PC).

Il rilevamento della postura e il flusso di immagini.

L'elaborazione dell'emozione facciale e l'analisi del sentiment.

