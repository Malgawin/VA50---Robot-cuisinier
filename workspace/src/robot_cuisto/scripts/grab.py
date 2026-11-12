#!/usr/bin/env python3

import rospy
import actionlib
import sys
import moveit_commander

from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from trajectory_msgs.msg import JointTrajectoryPoint
from std_msgs.msg import Float64
from geometry_msgs.msg import Pose
from coordonnee import YoloGazeboNode
from changement_repere import changement_repere_generique,recuperer_matrice_camera_a_robot

def set_finger_positions(tip_1_position, tip_2_position):
    """
    Function to adjust the positions of the fingers via the publishers.
    """
    tip_1_pub.publish(Float64(tip_1_position))
    tip_2_pub.publish(Float64(tip_2_position))
    rospy.sleep(2.0)  

def open_pliers():
    """
    Function to open the gripper fingers.
    """
    client.wait_for_server()

    # Create the goal
    goal = FollowJointTrajectoryGoal()

    goal.trajectory.joint_names = [
        "j2n6s200_joint_finger_1",
        "j2n6s200_joint_finger_2"
    ]

    point = JointTrajectoryPoint()
    point.positions = [0.2, 0.2] # 1.51 = Close ; 0.0 = Open
    point.velocities = [0.0, 0.0]
    point.time_from_start = rospy.Duration(2.0)

    goal.trajectory.points = [point]

    # Open the gripper fingers
    set_finger_positions(1.0, 1.0)


    client.send_goal_and_wait(goal)
    state = client.get_state()
    rospy.loginfo("Final action state: %s", state)

def close_pliers():
    """
    Function to close the gripper fingers.
    """
    client.wait_for_server()


    # Create the goal
    goal = FollowJointTrajectoryGoal()

    goal.trajectory.joint_names = [
        "j2n6s200_joint_finger_1",
        "j2n6s200_joint_finger_2"
    ]

    point = JointTrajectoryPoint()
    point.positions = [0.6, 0.6] # 1.51 = Close ; 0.0 = Open
    point.velocities = [0.0, 0.0]
    point.time_from_start = rospy.Duration(2.0)

    goal.trajectory.points = [point]

    # Close the gripper fingers
    set_finger_positions(1.0, 1.0)

    client.send_goal_and_wait(goal)
    state = client.get_state()
    rospy.loginfo("Final action state: %s", state)


def go_to(x, y, z):
    """
    Function to move the robot arm to a specific position (x, y, z) in space.
    """
    arm = moveit_commander.MoveGroupCommander("arm")

    # Create a target pose for the gripper
    target = Pose()

    target.position.x = x
    target.position.y = y
    target.position.z = z

    target.orientation.x = 0.99950884776002
    target.orientation.y = -0.030123683616033747
    target.orientation.z = 0.0068792436275408025
    target.orientation.w = 0.005225221713102918

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

    



if __name__ == "__main__":
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node("finger_gripper_control")

    # Create an action client for the gripper's joint trajectory controller
    client = actionlib.SimpleActionClient(
    "/j2n6s200/effort_finger_trajectory_controller/follow_joint_trajectory",
    FollowJointTrajectoryAction
    )

    # Publishers for controlling the finger positions
    tip_1_pub = rospy.Publisher(
        "/j2n6s200/finger_tip_1_position_controller/command",
        Float64,
        queue_size=1
    )

    tip_2_pub = rospy.Publisher(
        "/j2n6s200/finger_tip_2_position_controller/command",
        Float64,
        queue_size=1
    )
    
    matrice_camera_robot = recuperer_matrice_camera_a_robot() # parameter target_frame = "j2n6s200_link_base",source_frame = "rgbd_camera_color_optical_frame" change for the real test
    
    node = YoloGazeboNode()
    objet = node.objet_reperer()
    obj=[]
    if len(objet)==0:
        print("aucun objet")
    else:
        print(objet[0])       
        obj=node.obtenir_coordonnees_objet(objet[0]) # give the object name (in English)
        print(obj)
    
    coord =  changement_repere_generique(obj,matrice_camera_robot)
    print(coord)

    position = coord # x and y are coordinates of the object, z is the height of the object
    
    go_to(position[0], position[1], 0.3) 

    open_pliers()

    go_to(position[0], position[1], position[2] / 2) 

    close_pliers()

    go_to(position[0], position[1], 0.3)

    moveit_commander.roscpp_shutdown()

