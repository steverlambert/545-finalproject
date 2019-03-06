#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, PoseArray
from planning_utils.srv import *

source_updated = False
target_updated = False

source_pose = None
target_pose = None

def source_cb(msg):
  global source_pose, source_updated
  print '[Service Test] Got new source'
  source_pose = PoseStamped()
  source_pose.header = msg.header
  source_pose.pose = msg.pose.pose
  source_updated = True
  
def target_cb(msg):  
  global target_pose, target_updated
  print '[Service Test] Got new target'
  target_pose = msg
  target_updated = True
  

if __name__ == '__main__':
  rospy.init_node('service_test', anonymous=True)
  
  # Service proxy for getting motion plan
  get_plan = rospy.ServiceProxy('/planner_node/get_car_plan', GetPlan)  
  
  plan_pub = rospy.Publisher('service_test/plan', PoseArray, queue_size=1)  
  
  source_sub = rospy.Subscriber("/initialpose", 
                                PoseWithCovarianceStamped, 
                                source_cb,
                                queue_size=1)
  target_sub = rospy.Subscriber("/move_base_simple/goal", 
                                PoseStamped, 
                                target_cb,
                                queue_size=1) 
  cur_plan = None
      
  print 'Ready to request plans'
  while not rospy.is_shutdown():
    if target_updated and source_updated:
      target_updated = False
      source_updated = False
      gpr = GetPlanRequest()
      gpr.source = source_pose
      gpr.target = target_pose
      try:
        print 'Going to request plan'
        plan_resp = get_plan(gpr)
      except rospy.ServiceException, e:
          print "Service call failed: %s"%e    
          continue
      print 'Plan received'
      cur_plan = plan_resp.plan
      
    if cur_plan is not None:
      plan_pub.publish(cur_plan)
          
    rospy.sleep(1)  
    
