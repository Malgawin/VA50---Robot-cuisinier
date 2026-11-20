#!/usr/bin/env python3

import rospy
import actionlib
import sys
import moveit_commander
import kinova_msgs.msg
import std_msgs.msg
import geometry_msgs.msg

def open_pliers(client):
    """
    Function to open the gripper fingers.
    """

    # Create the goal
    goal = kinova_msgs.msg.SetFingersPositionGoal()
    goal.fingers.finger1 = 0.0
    goal.fingers.finger2 = 0.0
    
    # The MICO arm has only two fingers, but the same action definition is used
    goal.fingers.finger3 = 0.0
    client.send_goal(goal)

    if client.wait_for_result(rospy.Duration(10.0)):
        print('Gripper opened successfully!')
        return client.get_result()
    else:
        client.cancel_all_goals()
        rospy.logwarn('        the gripper action failed with state %s', client.get_state())
        return None


def close_pliers(client):
    """
    Function to close the gripper fingers.
    """

    # Create the goal
    goal = kinova_msgs.msg.SetFingersPositionGoal()
    goal.fingers.finger1 = 6800.0
    goal.fingers.finger2 = 6800.0
    
    # The MICO arm has only two fingers, but the same action definition is used
    goal.fingers.finger3 = 0.0
    client.send_goal(goal)

    if client.wait_for_result(rospy.Duration(10.0)):
        print('Gripper closed successfully!')
        return client.get_result()
    else:
        client.cancel_all_goals()
        rospy.logwarn('        the gripper action failed with state %s', client.get_state())
        return None


def go_to(client, position):
    """
    Function to move the robot arm to a specific position (x, y, z) in space.
    """
    goal = kinova_msgs.msg.ArmPoseGoal()
    goal.pose.header = std_msgs.msg.Header(frame_id=('j2n6s200_link_base'))

    goal.pose.pose.position = geometry_msgs.msg.Point(
        x=position[0],
        y=position[1],
        z=position[2]
    )

    goal.pose.pose.orientation = geometry_msgs.msg.Quaternion(
        x=-0.6575503945350647,
        y=-0.752606987953186,
        z=-0.034623369574546814,
        w=-0.0034104399383068085
    )

    client.send_goal(goal)

    if client.wait_for_result(rospy.Duration(10.0)):
        client.get_result()
        print('Cartesian pose sent!')
    else:
        client.cancel_all_goals()
        print('        the cartesian action timed-out.')


if __name__ == "__main__":
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node("finger_gripper_control")

    client_pose = actionlib.SimpleActionClient(
    '/j2n6s200_driver/pose_action/tool_pose',
    kinova_msgs.msg.ArmPoseAction 
    )

    client_pose.wait_for_server()

    client_fingers = actionlib.SimpleActionClient('/j2n6s200_driver/fingers_action/finger_positions',
                                              kinova_msgs.msg.SetFingersPositionAction)
    client_fingers.wait_for_server()
    
    position = [0.2440173625946045, -0.540213942527771, 0.050] #coord # x and y are coordinates of the object, z is the height of the object

    pre_grasp_position = [position[0], position[1], position[2] + 0.1] # pre-grasp position is above the object
    go_to(client_pose, pre_grasp_position) 

    rospy.sleep(0.5)

    open_pliers(client_fingers)

    rospy.sleep(0.5)

    grasp_position = [position[0], position[1], position[2] / 2] # grasp position is slightly above the object
    go_to(client_pose, grasp_position) 

    rospy.sleep(0.5)

    close_pliers(client_fingers)

    rospy.sleep(0.5)

    go_to(client_pose, pre_grasp_position) # move back to pre-grasp position

    moveit_commander.roscpp_shutdown()
