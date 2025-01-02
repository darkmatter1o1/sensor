cmake_minimum_required(VERSION 3.5)

project(sensor)


find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)

# Add your Python node executable
install(PROGRAMS
  src/sensor_node.py
  DESTINATION lib/${PROJECT_NAME}
)
