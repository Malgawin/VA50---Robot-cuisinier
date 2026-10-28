
export QT_X11_NO_MITSHM=1
export VISP_INPUT_IMAGE_PATH=${HOME}/visp-ws/visp-images

source /opt/ros/${ROS_DISTRO}/setup.bash

if [ -f ${ROS_WORKSPACE}/devel/setup.bash ]; then
  source ${ROS_WORKSPACE}/devel/setup.bash
fi

export DISABLE_ROS1_EOL_WARNINGS=1


export ROS_IP=127.0.0.1;
export ROS_MASTER_URI="http://localhost:11311/"

export GAZEBO_MODEL_PATH=/home/ros/ros_ws/src/robot_cuisto/models/objects_gazebo:/home/ros/ros_ws/src/robot_cuisto/models/objects_gazebo/kit:/home/ros/ros_ws/src/robot_cuisto/models/objects_gazebo/ycb:/home/ros/ros_ws/src/robot_cuisto/models/objects_gazebo/bigbird:$GAZEBO_MODEL_PATH

