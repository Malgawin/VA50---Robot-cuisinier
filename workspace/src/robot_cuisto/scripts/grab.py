#!/usr/bin/env python3

import rospy
import actionlib
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Float64
import sys
import moveit_commander
from geometry_msgs.msg import Pose

def set_finger_positions(tip_1_position, tip_2_position):
    """
    Fonction pour ajuster les positions des doigts via les publishers.
    """
    tip_1_pub.publish(Float64(tip_1_position))
    tip_2_pub.publish(Float64(tip_2_position))
    rospy.sleep(2.0)  

def open_pliers():
    # 2) On attend que le contrôleur soit disponible
    rospy.loginfo("Waiting for finger trajectory controller...")
    client.wait_for_server()
    rospy.loginfo("Finger trajectory controller is ready.")

    # 3) On crée le goal
    goal = FollowJointTrajectoryGoal()

    # 4) On donne les noms des joints à commander
    goal.trajectory.joint_names = [
        "j2n6s200_joint_finger_1",
        "j2n6s200_joint_finger_2"
    ]

    # 5) On crée un point de trajectoire
    point = JointTrajectoryPoint()

    # 6) On donne la position cible des doigts
    # Attention : ces valeurs dépendent de ton robot et de la URDF.
    # Il faut les ajuster selon ton gripper.
    point.positions = [0.2, 0.2] # 1.51 = Close ; 0.0 = Open

    # 7) Vitesses nulles pour simplifier
    point.velocities = [0.0, 0.0]

    # 8) Temps d'exécution
    point.time_from_start = rospy.Duration(2.0)

    # 9) On ajoute le point à la trajectoire
    goal.trajectory.points = [point]

    # Ajustement des positions des doigts via les publishers pour les contrôleurs de position
    set_finger_positions(1.0, 1.0)  # Ajuste les positions des doigts pour fermer le gripper

    # 10) On envoie la trajectoire
    client.send_goal_and_wait(goal)

    # 11) On récupère le résultat
    state = client.get_state()
    rospy.loginfo("Final action state: %s", state)

def close_pliers():
    # 2) On attend que le contrôleur soit disponible
    rospy.loginfo("Waiting for finger trajectory controller...")
    client.wait_for_server()
    rospy.loginfo("Finger trajectory controller is ready.")

    # 3) On crée le goal
    goal = FollowJointTrajectoryGoal()

    # 4) On donne les noms des joints à commander
    goal.trajectory.joint_names = [
        "j2n6s200_joint_finger_1",
        "j2n6s200_joint_finger_2"
    ]

    # 5) On crée un point de trajectoire
    point = JointTrajectoryPoint()

    # 6) On donne la position cible des doigts
    # Attention : ces valeurs dépendent de ton robot et de la URDF.
    # Il faut les ajuster selon ton gripper.
    point.positions = [0.6, 0.6] # 1.51 = Close ; 0.0 = Open

    # 7) Vitesses nulles pour simplifier
    point.velocities = [0.0, 0.0]

    # 8) Temps d'exécution
    point.time_from_start = rospy.Duration(2.0)

    # 9) On ajoute le point à la trajectoire
    goal.trajectory.points = [point]

    # Ajustement des positions des doigts via les publishers pour les contrôleurs de position
    set_finger_positions(1.0, 1.0)  # Ajuste les positions des doigts pour fermer le gripper

    # 10) On envoie la trajectoire
    client.send_goal_and_wait(goal)

    # 11) On récupère le résultat
    state = client.get_state()
    rospy.loginfo("Final action state: %s", state)


def go_to(x, y, z):
    # Groupe MoveIt correspondant au bras
    arm = moveit_commander.MoveGroupCommander("arm")

    current = arm.get_current_pose().pose

    print(current)

    # Pose cible du gripper
    target = Pose()

    target.position.x = x
    target.position.y = y
    target.position.z = z

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

    

moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node("finger_gripper_control")

# 1) On crée le client d'action dédié au contrôleur des doigts
client = actionlib.SimpleActionClient(
"/j2n6s200/effort_finger_trajectory_controller/follow_joint_trajectory",
FollowJointTrajectoryAction
)

# Publishers pour les positions des doigts 
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

go_to(0.161606, -0.657037, 0.3) 

open_pliers()

go_to(0.161606, -0.657037, 0.07) 

close_pliers()

go_to(0.161606, -0.657037, 0.3)

moveit_commander.roscpp_shutdown()

