import cv2
import numpy as np


class SettingsView:
    def __init__(self):
        cv2.namedWindow("Tracking")
        cv2.createTrackbar("LH", "Tracking", 30, 255, lambda _: ())
        cv2.createTrackbar("LS", "Tracking", 100, 255, lambda _: ())
        cv2.createTrackbar("LV", "Tracking", 100, 255, lambda _: ())
        cv2.createTrackbar("UH", "Tracking", 85, 255, lambda _: ())
        cv2.createTrackbar("US", "Tracking", 255, 255, lambda _: ())
        cv2.createTrackbar("UV", "Tracking", 255, 255, lambda _: ())

    
    def hsv_lower_bound(self):
        l_h = cv2.getTrackbarPos("LH", "Tracking")
        l_s = cv2.getTrackbarPos("LS", "Tracking")
        l_v = cv2.getTrackbarPos("LV", "Tracking")
        return np.array([l_h, l_s, l_v])


    def hsv_upper_bound(self):
        u_h = cv2.getTrackbarPos("UH", "Tracking")
        u_s = cv2.getTrackbarPos("US", "Tracking")
        u_v = cv2.getTrackbarPos("UV", "Tracking")
        return np.array([u_h, u_s, u_v])