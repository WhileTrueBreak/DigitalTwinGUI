#!/usr/bin/env python
import rospy
import sys
from std_msgs.msg import String

class simple_class:

    def __init__(self):
        self.sub = rospy.Subscriber("chatter",String,self.callback)

    def callback(self,data):
        print(data.data)



def main(args):
    print('..')
    obc = simple_class()
    print('..')
    rospy.init_node('simple_class', anonymous=True)
    print('..')
    while not rospy.core.is_shutdown():
        rospy.rostime.wallsleep(0.5)
    print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)