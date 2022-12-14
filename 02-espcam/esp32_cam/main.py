import math
import sys
import time

import numpy as np
import statistics

import requests

import cv2
import imutils

esp_url = "http://192.168.0.120"
resolution = 7

stream = cv2.VideoCapture(esp_url + ":81/stream")

classifier = cv2.CascadeClassifier("D:\\Documents\\PythonProject\\esp32_cam\\venv\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_alt2.xml")

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

frame_memory = 0

def main():
    print("Startup")
    global stream
    global classifier
    global frame_memory
    set_camera_resolution(7)
    set_camera_quality(10)
    #set_camera_auto_white_balance(1)

    ret, frame_memory = stream.read()
    frame_memory = remove_color_from_image(frame_memory)
    cv2.imshow("video stream", frame_memory)

    last_hot_area = []

    while True:
        if stream.isOpened():
            ret, frame = stream.read()

            if ret:
                processed_frame = remove_color_from_image(frame)

                difference = detect_motion(processed_frame, frame_memory, show_frame=True)
                frame_memory = processed_frame

                hot_area = find_hot_spots(difference)
                if len(hot_area) == 0:
                    hot_area = last_hot_area
                last_hot_area = hot_area

                people = person_detection(processed_frame)
                faces = face_detection(processed_frame)

                frame = mark_rectangles(frame, hot_area, (0, 0, 200))
                frame = mark_rectangles(frame, difference, (200, 0, 0))
                frame = mark_rectangles(frame, faces, (0, 200, 0))
                frame = mark_rectangles(frame, people, (0, 100, 100))

            cv2.imshow("video stream", frame)

            key = cv2.waitKey(1)
            if key == 27:
                print("\n\nExit")
                break

    cv2.destroyAllWindows()
    stream.release()

def mark_rectangles(frame, rectangles_list = [], color = (200, 200, 200)):
    marked_frame = frame
    for (rectangle_x, rectangle_y, rectangle_width, rectangle_height) in rectangles_list:
        marked_frame = cv2.rectangle(frame, (rectangle_x, rectangle_y), (rectangle_x + rectangle_width, rectangle_y + rectangle_height), color, 1)
    return marked_frame

def remove_color_from_image(frame):
    gray_scale_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #gray_scale_img = cv2.equalizeHist(gray_scale_img)
    cv2.imshow("gray", gray_scale_img)
    return gray_scale_img

def detect_motion(current, previous, show_frame = False):
    frame = current.copy()
    cv2.absdiff(previous, current, frame)

    for i in range(3):
        frame = cv2.dilate(frame, None, iterations=1 + i)

    (T, thresh) = cv2.threshold(frame, 63, 255, cv2.THRESH_BINARY)
    frame_differences = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    frame_differences = imutils.grab_contours(frame_differences)

    if show_frame:
        for difference in frame_differences:
            (difference_x, difference_y, difference_width, difference_height) = cv2.boundingRect(difference)
            cv2.rectangle(frame, (difference_x, difference_y), (difference_x + difference_width, difference_y + difference_height), (200, 200, 200), 1)
        cv2.imshow("difference", frame)

    rectangles_list = []
    for difference in frame_differences:
        (difference_x, difference_y, difference_width, difference_height) = cv2.boundingRect(difference)
        rectangles_list.append([difference_x, difference_y, difference_width, difference_height])

    return rectangles_list

def face_detection(frame):
    objects = classifier.detectMultiScale(frame)
    rectangles_list = []
    for object in objects:
        rectangle = []
        for data in object:
            rectangle.append(data)
        rectangles_list.append(rectangle)

    return rectangles_list

def person_detection(frame):
    rectangles_list = []

    detected_object, weights = hog.detectMultiScale(frame, winStride=(4, 4))
    for object in detected_object:
        rectangles_list.append([object[0], object[1], object[2], object[3]])

    return rectangles_list

def find_hot_spots(rectangles_list):
    hot_spots = []
    hot_points = []

    rectangles_center = []
    for (rectangle_x, rectangle_y, rectangle_width, rectangle_height) in rectangles_list:
        rectangles_center.append([rectangle_x + (rectangle_width/2), rectangle_y + (rectangle_height/2)])

    distance_list = []
    for a in range(len(rectangles_center)):
        for b in range(a, len(rectangles_center)):
            distance_list.append(math.sqrt((rectangles_center[a][0] - rectangles_center[b][0])**2 + (rectangles_center[a][1] - rectangles_center[b][1])**2))

    if distance_list:
        distance_median = int(round(statistics.median(distance_list), 0))

        hot_points.append([rectangles_center[0], distance_median/2])

        for points in range(len(hot_points)):
            for a in range(len(rectangles_center)):
                distance = math.sqrt((hot_points[points][0][0] - rectangles_center[a][0])**2 + (hot_points[points][0][1] - rectangles_center[a][1])**2)
                if distance > distance_median:
                    if distance > hot_points[points][1]:
                        hot_points[points][1] = distance
                    hot_points[points][0] = [(hot_points[points][0][0] + rectangles_center[a][0])/2, (hot_points[points][0][1] + rectangles_center[a][1])/2]
                else:
                    hot_points.append([rectangles_center[a], distance_median/2])

        for points in range(len(hot_points)):
            point_x = int(round(hot_points[points][0][0] - hot_points[points][1]*2, 0))
            point_y = int(round(hot_points[points][0][1] - hot_points[points][1]*2, 0))
            point_width = point_height = int(round(hot_points[points][1]*4, 0))
            hot_spots.append([point_x, point_y, point_width, point_height])


    return hot_spots


def set_camera_resolution(index=7):
    global esp_url
    print("Setting resolution ... ", end="")
    requests.get(esp_url + "/control?var=framesize&val={}".format(int(index)))
    print("ok")

def set_camera_quality(value = 60):
    global esp_url
    print("Setting quality ... ", end="")
    requests.get(esp_url + "/control?var=quality&val={}".format(int(value)))
    print("ok")

def set_camera_auto_white_balance(value=1):
    global esp_url
    print("Setting white balance... ", end="")
    requests.get(esp_url + "/control?var=awb&val={}".format(1 if int(value) else 0))
    print("ok")

main()