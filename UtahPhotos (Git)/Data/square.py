import cv2

image = cv2.imread('center_demo.png')

#pixels for square
x1=510
y1=483
x2=763
y2=736

pt1 = (x1, y1)
pt2 = (x2, y2)

#Color is BGR (Blue, Green, Red)
#Thickness = -1 allows filled in shape
cv2.rectangle(image, pt1, pt2, color=(255, 0, 0), thickness=1)

center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
cv2.circle(image, center, radius=5, color=(255, 0, 0), thickness=-1)

cv2.imwrite('center_demoSQUARED.jpg', image)