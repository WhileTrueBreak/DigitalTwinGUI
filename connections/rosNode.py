class RosSubscriber:

  def __init__(self, topic, ttype):
    self.sub = rospy.Subscriber("chatter",ttype,self.callback)

  def callback(self,data):
    print(data.data)