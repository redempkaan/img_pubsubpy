import rclpy
from rclpy.node import Node

from std_msgs.msg import String
import socket
import requests
import time

SIGNAL_SERVER = "ip address"

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        self.port = 6000
        self.i = 0

        requests.post(f"{SIGNAL_SERVER}/register", json={
            "name": "sender",
            "port": self.port
        })
        self.get_logger().info("Sender has been registered")

        # Wait for receiver ip & port
        receiver_ip, receiver_port = self.wait_for_receiver()
        self.get_logger().info(f"Receiver found: {receiver_ip}:{receiver_port}")

        # Establish TCP connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((receiver_ip, receiver_port))
        self.get_logger().info("Connection established with receiver")

        # Message frequency
        self.timer = self.create_timer(1.0, self.timer_callback_send_msg)
    
    def wait_for_receiver(self):
        while True:
            try:
                info = requests.get(f"{SIGNAL_SERVER}/get/receiver").json()
                if "ip" in info:
                    return info["ip"], info["port"]
            except:
                pass
            self.get_logger().info("Waiting for receiver")
            time.sleep(1)

    def timer_callback_send_msg(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
