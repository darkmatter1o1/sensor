# sensor
problem 1 and 2

tcp_sensor fake sensor and client for ros2 foxy 


the code has 2 parts sensor client and fake sensor part
fake sensor sends sensor data to the ip 127.0.0.1 at port 2000
the interval can be set in code and in launch also as ros args

launching nodes will automaticlly establish connection and start the topic publishing initially with the given interval

ros run sensor fake_sensor #starts the dummy sensor

ros run sensor sensor --ros-args -p interval:=100 # starts the ros client node the ros2 node makes the connection with sensor and upon receiving sensor data publishes topics 


/sensor/env_temperature
/sensor/pitch
/sensor/roll
/sensor/supply_voltage
/sensor/yaw
these topics publishes the fake sesnor data

problem 3

a custom service package is made to start the sensor by a user using the custum service that is the other package rosidl_tutorial_msgs 
this service can be called to start the sensor and set an inteval according to the user 

ros2 service call /start_sensor rosidl_tutorials_msgs/srv/StartSensor "{interval: 500}"

and also standerd service is used to stop the sensor by running the command 

ros2 service call /stop_sensor std_srvs/srv/Trigger "{}"
this command will stop the data publishing to the topic
