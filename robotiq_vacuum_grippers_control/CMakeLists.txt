# http://ros.org/doc/groovy/api/catkin/html/user_guide/supposed.html
cmake_minimum_required(VERSION 2.8.3)
project(robotiq_vacuum_grippers_control)
find_package(catkin REQUIRED COMPONENTS robotiq_ethercat robotiq_modbus_rtu roscpp rospy message_generation)


#set the default path for built executables to the "bin" directory
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
#set the default path for built libraries to the "lib" directory
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)

###################################
## catkin message generation     ##
###################################
add_message_files(
  FILES
  RobotiqVacuumGrippers_robot_input.msg
  RobotiqVacuumGrippers_robot_output.msg
)

catkin_python_setup()

generate_messages()

###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
    CATKIN_DEPENDS rospy message_runtime roscpp robotiq_ethercat robotiq_modbus_rtu
    INCLUDE_DIRS include
)

include_directories(include)
include_directories(
  ${catkin_INCLUDE_DIRS}
  ${robotiq_ethercat_INCLUDE_DIRS}
)

add_executable(robotiq_vacuum_grippers_ethercat_node
  src/robotiq_vacuum_grippers_control/robotiq_vacuum_grippers_ethercat_node.cpp
  src/robotiq_vacuum_grippers_control/robotiq_vacuum_grippers_ethercat_client.cpp
)

target_link_libraries(robotiq_vacuum_grippers_ethercat_node
   ${robotiq_ethercat_LIBRARIES}
   ${catkin_LIBRARIES}
  
)

add_dependencies(robotiq_vacuum_grippers_ethercat_node robotiq_vacuum_grippers_control_generate_messages_cpp)

#############
## Install ##
#############

# all install targets should use catkin DESTINATION variables
# See http://ros.org/doc/groovy/api/catkin/html/adv_user_guide/variables.html

install(PROGRAMS nodes/RobotiqVacuumGrippersSimpleController.py nodes/RobotiqVacuumGrippersStatusListener.py
    nodes/RobotiqVacuumGrippersTcpNode.py nodes/RobotiqVacuumGrippersRtuNode.py DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

