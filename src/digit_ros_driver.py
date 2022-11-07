#!/usr/bin/env python

import rospy
import cv2, cv_bridge
from sensor_msgs.msg import Image
from digit_interface import Digit, DigitHandler





class DigitROSDriver(object):

    def __init__(self):

        self.serial = rospy.get_param('serial', 'D20453')
        self.resolution = rospy.get_param('resolution', 'QVGA') # VGA, QVGA
        self.fps = rospy.get_param('fps', '30fps') # 15fps, 30fps, 60fps
        self.image_pub = rospy.Publisher("/digit/camera/color", Image, queue_size=1)

    def connect(self):

        digit_infos = DigitHandler.list_digits()
        for digit_info in digit_infos:
            if digit_info['serial'] == self.serial:
                self.digit = Digit(self.serial)
                self.digit.connect()
                self.digit.set_resolution(Digit.STREAMS[self.resolution])
                self.digit.set_fps(Digit.STREAMS[self.resolution]["fps"][self.fps])
                rospy.loginfo("Connected to digit {} with resolution {} and fps {}".format(self.serial, self.resolution, self.fps))
                rospy.loginfo("Digit info: {}".format(self.digit.info()))
                return True
        rospy.signal_shutdown('Digit {} not found'.format(self.serial))

    def run(self):
        frame = self.digit.get_frame()
        image = Image()
        image.header.stamp = rospy.Time.now()
        image.height = frame.shape[0]
        image.width = frame.shape[1]
        image.encoding = "bgr8"
        image.is_bigendian = 0
        image.step = frame.strides[0]
        image.data = frame.tostring()
        self.image_pub.publish(image)
        rospy.loginfo_once("Publishing digit image to /digit/camera/color")


if __name__ == '__main__':
    
    rospy.init_node('digit_ros_driver')
    digit_ros_driver = DigitROSDriver()
    digit_ros_driver.connect()
    while not rospy.is_shutdown():
        digit_ros_driver.run()