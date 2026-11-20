#!/usr/bin/env python3

import rospy
import actionlib
import kinova_msgs.msg
import std_msgs.msg
import geometry_msgs.msg

rospy.init_node("go_to_initial_pose")


client = actionlib.SimpleActionClient(
    '/j2n6s200_driver/pose_action/tool_pose', # "/j2n6s200/effort_joint_trajectory_controller/follow_joint_trajectory",
    kinova_msgs.msg.ArmPoseAction # FollowJointTrajectoryAction
)

client.wait_for_server()

rospy.loginfo("Waiting for the joint trajectory controller...")

"""
if not client.wait_for_server(rospy.Duration(60.0)):
    rospy.logerr("Joint trajectory controller not available.")
    raise rospy.ROSInterruptException()
"""

rospy.loginfo("Joint trajectory controller is ready.")

goal = kinova_msgs.msg.ArmPoseGoal()
goal.pose.header = std_msgs.msg.Header(frame_id=('j2n6s200_link_base'))

goal.pose.pose.position = geometry_msgs.msg.Point(
    x=0.21158096194267273,
    y=-0.25617432594299316,
    z=0.5044417381286621
)

goal.pose.pose.orientation = geometry_msgs.msg.Quaternion(
    x=0.6493631601333618,
    y=0.31814005970954895,
    z=0.42637085914611816,
    w=0.5434357523918152
)

client.send_goal(goal)

if client.wait_for_result(rospy.Duration(10.0)):
    client.get_result()
    print('Cartesian pose sent!')
else:
    client.cancel_all_goals()
    print('        the cartesian action timed-out.')
