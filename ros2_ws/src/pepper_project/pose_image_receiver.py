import struct
import socket
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from fer import FER
import mediapipe as mp

ROS_IP = "0.0.0.0"   # Indirizzo locale (0.0.0.0 per accettare connessioni da qualsiasi IP)
ROS_PORT = 5001        # Porta su cui ci si aspetta la connessione dal mittente

class PepperImageReceiver(Node):
    def __init__(self):
        super().__init__('pepper_image_receiver')
        # Publisher ROS2 per l'immagine e per i dati di emozione/postura
        self.image_pub = self.create_publisher(Image, 'pepper_camera/image_raw', 10)
        self.emotion_pub = self.create_publisher(String, 'pepper_camera/emotion', 10)
        self.posture_pub = self.create_publisher(String, 'pepper_camera/posture', 10)
        self.bridge = CvBridge()
        
        # Inizializza FER per il riconoscimento delle emozioni
        self.detector = FER()

        # Inizializza MediaPipe per il riconoscimento della postura
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose()

        # Avvio server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ROS_IP, ROS_PORT))
        self.server_socket.listen(1)
        self.get_logger().info(f"Ricevitore in ascolto su porta {ROS_PORT}...")

    def start_listening(self):
        # Accetta una singola connessione (Pepper sender)
        conn, addr = self.server_socket.accept()
        self.get_logger().info(f"Connessione accettata da {addr}")
        # Ciclo di ricezione dati
        try:
            # Ricevi la lunghezza dell'immagine
            data = conn.recv(4)
            if not data:
                self.get_logger().warn("Socket chiuso dal mittente")
                return
            img_len = struct.unpack('!I', data)[0]
            self.get_logger().info(f"Lunghezza immagine: {img_len}")

            # Ricevi i pacchetti e invia un ACK per ogni pacchetto ricevuto
            img_data = b''

            while len(img_data) < img_len:
                packet = conn.recv(1024)  # Riceve pacchetti di 1024 byte
                if not packet:
                    break
                img_data += packet
                # Invia un ACK dopo aver ricevuto ogni pacchetto
                conn.sendall(b'ACK')

            # Se i dati ricevuti sono completi, decodifica l'immagine
            if len(img_data) == img_len:
                np_arr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is None:
                    self.get_logger().error("Errore nella decodifica dell'immagine")
                    return

                self.get_logger().info("Immagine ricevuta e decodificata con successo")

                # Visualizza l'immagine ricevuta (opzionale)
                cv2.imshow("Pepper Camera", frame)
                cv2.waitKey(1)  # necessario per refresh GUI

                # Pubblica su ROS
                img_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
                img_msg.header.stamp = self.get_clock().now().to_msg()
                self.image_pub.publish(img_msg)

                # Ora rileviamo l'emozione e la postura
                emotion, emotion_score = self.detect_emotion(frame)
                if emotion is None:
                    emotion = "Unknown"
                    emotion_score = 0.0
                self.get_logger().info(f"Emotion detected: {emotion} with score: {emotion_score}")

                posture_landmarks = self.detect_posture_landmarks(frame)
                posture_type = self.classify_posture(posture_landmarks)

                # Stampa sulla postura rilevata
                self.get_logger().info(f"Posture detected: {posture_type}")

                # Calcoliamo il punteggio finale dell'emozione con la logica di fusione
                final_emotion_score = self.adjust_emotion_based_on_posture(emotion, emotion_score, posture_type)
                self.get_logger().info(f"Emotion: {emotion}, Final Score: {final_emotion_score}")

                # Pubblica emozione e postura sui topic ROS
                self.emotion_pub.publish(String(data=f"{emotion} {final_emotion_score}"))
                self.posture_pub.publish(String(data=posture_type))

                # Rilevamento del sentiment nel testo (dummy in questo esempio)
                sentiment_score = self.analyze_sentiment(emotion)  # Analizza il sentiment dell'emozione
                self.get_logger().info(f"Sentiment analysis result: {sentiment_score}")

                # Applica il sentiment al punteggio finale
                final_emotion_score = self.apply_sentiment_to_emotion(final_emotion_score, sentiment_score)

                # Pubblica il punteggio finale dopo l'analisi del sentiment
                self.emotion_pub.publish(String(data=f"Final Emotion Score with Sentiment: {final_emotion_score}"))

        except Exception as e:
            self.get_logger().error(f"Errore nel ricevimento dell'immagine: {e}")
        finally:
            conn.close()
            self.server_socket.close()
            cv2.destroyAllWindows()
            self.get_logger().info("Socket chiuso, receiver terminato.")

    def detect_emotion(self, frame):
        # Riconoscimento emozionale usando FER
        emotion, score = self.detector.top_emotion(frame)
        return emotion, score

    def detect_posture_landmarks(self, frame):
        # Usa MediaPipe per rilevare i landmarks della postura
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose_detector.process(frame_rgb)
        return results.pose_landmarks

    def classify_posture(self, landmarks):
        # Classificazione della postura
        if landmarks:
            return "open"  # Sostituisci con logica personalizzata per classificare la postura
        return "neutral"

    def adjust_emotion_based_on_posture(self, emotion, emotion_score, posture_type):
        # Logica di fusione dell'emozione basata sulla postura
        if emotion == "happy" and posture_type == "open":
            emotion_score *= 1.1
        elif emotion == "sad" and posture_type == "closed":
            emotion_score *= 1.1
        elif emotion == "sad" and posture_type == "open":
            emotion_score *= 0.7
        elif emotion == "neutral" and posture_type == "closed":
            emotion_score *= 1.2
        return emotion_score

    def analyze_sentiment(self, emotion):
        # Dummy sentiment analysis
        if emotion == "happy":
            sentiment_score = 0.9  # Positivo
        elif emotion == "sad":
            sentiment_score = -0.7  # Negativo
        else:
            sentiment_score = 0.0  # Neutrale
        return sentiment_score

    def apply_sentiment_to_emotion(self, final_emotion_score, sentiment_score):
        # Applica il punteggio di sentiment all'emozione finale
        return final_emotion_score + sentiment_score

def main(args=None):
    rclpy.init(args=args)
    node = PepperImageReceiver()
    try:
        node.start_listening()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
