#!/usr/bin/env python3

import rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import actionlib
from control_msgs.msg import FollowJointTrajectoryAction

rospy.init_node("go_to_initial_pose")


client = actionlib.SimpleActionClient(
    "/j2n6s200/effort_joint_trajectory_controller/follow_joint_trajectory",
    FollowJointTrajectoryAction
)

rospy.loginfo("Waiting for the joint trajectory controller...")

if not client.wait_for_server(rospy.Duration(60.0)):
    rospy.logerr("Joint trajectory controller not available.")
    raise rospy.ROSInterruptException()

rospy.loginfo("Joint trajectory controller is ready.")

pub = rospy.Publisher(
    "/j2n6s200/effort_joint_trajectory_controller/command",
    JointTrajectory,
    queue_size=1
)

rospy.sleep(1.0)

msg = JointTrajectory()

msg.joint_names = [
    "j2n6s200_joint_1",
    "j2n6s200_joint_2",
    "j2n6s200_joint_3",
    "j2n6s200_joint_4",
    "j2n6s200_joint_5",
    "j2n6s200_joint_6"
]

point = JointTrajectoryPoint()

point.positions = [
    -1.7231837854771288,
     3.489169447041279,
     1.4346895909114297,
    -0.35784450960177616,
     1.2566786331836335,
    -0.5542613463793103
]

point.velocities = [0, 0, 0, 0, 0, 0]

point.time_from_start = rospy.Duration(5.0)

msg.points.append(point)

pub.publish(msg)

rospy.loginfo("Initial pose sent.")
