# For more info: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html
#from PIL import Image, ExifTags
import cv2
import numpy as np
import os

# def getMeta(img2):
#     filename = "a.jpg"
#     im = Image.open(filename)
#     exif = { ExifTags.TAGS[k]: v for k, v in im._getexif().items() if k in ExifTags.TAGS}
#     # for (tag,value) in Image.open("a.jpg")._getexif().iteritems():
#     #     print ('%s = %s' % (TAGS.get(tag), value))

# def printInfo(cap):
#     # Get current width of frame
#     width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
#     print("Video width ="+str(width))
#     # Get current height of frame
#     height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
#     print("Video height ="+str(height))
#     pos = cap.get(cv2.CAP_PROP_POS_MSEC)
#     print("Video POS_MSEC ="+str(pos))
#     frm = cap.get(cv2.CAP_PROP_POS_FRAMES)
#     print("Video frames ="+str(frm))
#     rtio = cap.get(cv2.CAP_PROP_POS_AVI_RATIO)
#     print("Video ratio ="+str(rtio))
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     print("Video FPS ="+str(fps))
#     print("----------------------------------------------")

FILE_OUTPUT = 'output.avi'

# Checks and deletes the output file
# You cant have a existing file or it will through an error
if os.path.isfile(FILE_OUTPUT):
    os.remove(FILE_OUTPUT)

# Playing video from file:
# cap = cv2.VideoCapture('vtest.avi')
# Capturing video from webcam:
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('http://129.94.175.139:5000/video_feed')

currentFrame = 0

# Get current width of frame
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
print("Video width ="+str(width))
# Get current height of frame
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
print("Video height ="+str(height))
# pos = cap.get(cv2.CAP_PROP_POS_MSEC)
# print("Video POS_MSEC ="+str(pos))
# frm = cap.get(cv2.CAP_PROP_POS_FRAMES)
# print("Video frames ="+str(frm))
# rtio = cap.get(cv2.CAP_PROP_POS_AVI_RATIO)
# print("Video ratio ="+str(rtio))
# fps = cap.get(cv2.CAP_PROP_FPS)
# print("Video FPS ="+str(fps))

# Define the codec and create VideoWriter object
#fourcc = cv2.cv.CV_FOURCC(*'X264')
#fourcc = cv2.FOURCC(*'X264')
fourcc=cv2.VideoWriter_fourcc(*'XVID')
print("a")
#fourcc=cv2.VideoWriter_fourcc('X264') 
out = cv2.VideoWriter(FILE_OUTPUT,fourcc, 20.0, (int(width),int(height)))
#out = cv2.VideoWriter(FILE_OUTPUT,fourcc, 20.0, (int(640),int(480)))
print("b")

while(True):
#while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    #printInfo(cap)
    if ret == True:
        # Handles the mirroring of the current frame
        #frame = cv2.flip(frame,1)

        # Saves for video
        out.write(frame)

        # Display the resulting frame
        cv2.imshow('frame',frame)
    else:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # To stop duplicate images
    currentFrame += 1

# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()

# Potential Error:
# OpenCV: Cannot Use FaceTime HD Kamera
# OpenCV: camera failed to properly initialize!
# Segmentation fault: 11
#
# Solution:
# I solved this by restarting my computer.
# http://stackoverflow.com/questions/40719136/opencv-cannot-use-facetime/42678644#42678644
