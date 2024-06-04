import socket
import threading
import cv2
import mediapipe as mp
import numpy as np
import pygame
from pygame.locals import *
from pythonosc import udp_client
import logging
import time
import configparser

# Load configuration (if using config.ini)
config = configparser.ConfigParser()
config.read('config.ini')
CAMERA_IP = config.get('Settings', 'camera_ip', fallback="http://192.168.1.11:9999/video")
OSC_ADDRESS = config.get('Settings', 'osc_address', fallback="127.0.0.1")
OSC_PORT = config.getint('Settings', 'osc_port', fallback=9000)
PINCH_THRESHOLD = config.getfloat('Settings', 'pinch_threshold', fallback=0.05)
SCREEN_WIDTH = config.getint('Settings', 'camera_width', fallback=640)
SCREEN_HEIGHT = config.getint('Settings', 'camera_height', fallback=480)
FLIP_CAMERA = config.getboolean('Settings', 'flip_camera', fallback=False)
CAMERA_POS_X = config.getint('Settings', 'camera_position_x', fallback=0)
CAMERA_POS_Y = config.getint('Settings', 'camera_position_y', fallback=0)
STATUS_PORT = config.getint('Settings', 'status_port', fallback=5000)
GESTURE_TO_BUTTON_MAP = {  # Map hand gestures to VR button names (optional)
    "pinch": "/vr/input/left/button1",
    "fist": "/vr/input/right/button2"
}

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_status_update(message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode(), ("127.0.0.1", STATUS_PORT))


def convert_to_pose_matrix(landmarks):
    if landmarks:
        positions = [(landmark.x, landmark.y, landmark.z) for landmark in landmarks.landmark]
        pos = np.mean(positions, axis=0)
        return ((1, 0, 0, pos[0]), (0, 1, 0, pos[1]), (0, 0, 1, pos[2]), (0, 0, 0, 1))
    return None


def detect_gestures(landmarks):
    gestures = []
    if landmarks:
        # Implement logic to detect specific gestures (pinch, fist, etc.)
        # Example: Pinch detection based on landmark distance
        thumb_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        distance = np.linalg.norm(np.array)(thumb_tip.x, thumb_tip)
