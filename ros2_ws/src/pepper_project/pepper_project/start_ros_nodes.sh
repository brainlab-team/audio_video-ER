#!/bin/bash

echo "[WSL] Avvio dei nodi ROS2..."
cd ~/ros2_ws
source install/setup.bash

# Avvia i nodi ROS 2
ros2 run pepper_project image_processor &
ros2 run pepper_project audio_transcriber &
