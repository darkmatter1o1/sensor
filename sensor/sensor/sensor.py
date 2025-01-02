import rclpy
from rclpy.node import Node
import socket
import struct
from std_msgs.msg import Float32
from std_srvs.srv import Trigger
from rosidl_tutorials_msgs.srv import StartSensor  

class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')
        
        # Parameters
        self.declare_parameter('sensor_ip', '127.0.0.1')
        self.declare_parameter('sensor_port', 2000)
        self.declare_parameter('interval', 1000)  
        
        # Get parameters
        self.sensor_ip = self.get_parameter('sensor_ip').get_parameter_value().string_value
        self.sensor_port = self.get_parameter('sensor_port').get_parameter_value().integer_value
        self.interval = self.get_parameter('interval').get_parameter_value().integer_value

        # Publishers
        self.pub_voltage = self.create_publisher(Float32, '/sensor/supply_voltage', 10)
        self.pub_temperature = self.create_publisher(Float32, '/sensor/env_temperature', 10)
        self.pub_yaw = self.create_publisher(Float32, '/sensor/yaw', 10)
        self.pub_pitch = self.create_publisher(Float32, '/sensor/pitch', 10)
        self.pub_roll = self.create_publisher(Float32, '/sensor/roll', 10)

        # Services
        self.start_service = self.create_service(StartSensor, '/start_sensor', self.start_sensor_callback)
        self.stop_service = self.create_service(Trigger, '/stop_sensor', self.stop_sensor_callback)

        # TCP Connection
        self.socket = None
        self.connect_to_sensor()

        # Initial flag to control publishing
        self.is_publishing = True

        # Send Start Command on launch
        self.send_start_command(self.interval)

    def connect_to_sensor(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.sensor_ip, self.sensor_port))
            self.get_logger().info(f"Connected to sensor at {self.sensor_ip}:{self.sensor_port}")
        except Exception as e:
            self.get_logger().error(f"Failed to connect to sensor: {e}")
            self.socket = None

    def send_start_command(self, interval):
        if not self.socket:
            self.get_logger().error("No connection to sensor.")
            return

        interval_hex = struct.pack('<H', interval).hex().upper()
        message = f"#03{interval_hex}\r\n"
        self.socket.sendall(message.encode())
        self.get_logger().info(f"Sent Start Command: {message.strip()}")

    def send_stop_command(self):
        if not self.socket:
            self.get_logger().error("No connection to sensor.")
            return

        message = "#09\r\n"
        self.socket.sendall(message.encode())
        self.get_logger().info("Sent Stop Command.")

    def receive_data(self):
        if not self.is_publishing:
            return

        try:
            response = self.socket.recv(1024).decode()
            if response.startswith("$11"):
                self.decode_status_message(response)
        except Exception as e:
            self.get_logger().error(f"Error receiving data: {e}")

    def decode_status_message(self, message):
        try:
            payload_hex = message[3:-2]  
            payload = bytes.fromhex(payload_hex)
            supply_voltage, env_temp, yaw, pitch, roll = struct.unpack('<Hhhhh', payload)

            # Publish data
            self.pub_voltage.publish(Float32(data=supply_voltage / 1000.0))  
            self.pub_temperature.publish(Float32(data=env_temp / 10.0))      
            self.pub_yaw.publish(Float32(data=yaw / 10.0))                   
            self.pub_pitch.publish(Float32(data=pitch / 10.0))
            self.pub_roll.publish(Float32(data=roll / 10.0))

            self.get_logger().info(f"Decoded Status Message: Voltage={supply_voltage}mV, Temp={env_temp}dC, "
                                   f"Yaw={yaw}d, Pitch={pitch}d, Roll={roll}d")
        except Exception as e:
            self.get_logger().error(f"Error decoding status message: {e}")

    def start_sensor_callback(self, request, response):
        self.is_publishing = True  
        self.send_start_command(request.interval)
        response.success = True
        response.message = "Sensor started."
        return response

    def stop_sensor_callback(self, request, response):
        self.is_publishing = False  
        self.send_stop_command()
        response.success = True
        response.message = "Sensor stopped."
        return response


def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()

    try:
        while rclpy.ok():
            node.receive_data()
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if node.socket:
            node.socket.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
