#!/usr/bin/env python3

import sys
import rospy
import moveit_commander
from geometry_msgs.msg import Pose

moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node("move_to_gripper_pose")

# Groupe MoveIt correspondant au bras
arm = moveit_commander.MoveGroupCommander("arm")

current = arm.get_current_pose().pose

print(current)

# Pose cible du gripper
target = Pose()

target.position.x = -0.2
target.position.y = -0.45
target.position.z = 0.1

target.orientation.x = 0.99950884776002
target.orientation.y = -0.030123683616033747
target.orientation.z = 0.0068792436275408025
target.orientation.w = 0.005225221713102918

# Définir la cible cartésienne
arm.set_pose_target(target)

# Planification
success, trajectory, planning_time, error_code = arm.plan()

if success:
    rospy.loginfo("Planning successful")
    arm.execute(trajectory, wait=True)
    rospy.loginfo("Motion completed")
else:
    rospy.logerr("Planning failed")

arm.clear_pose_targets()

moveit_commander.roscpp_shutdown()
