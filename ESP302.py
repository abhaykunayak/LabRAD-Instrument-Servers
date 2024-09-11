import labrad
from labrad.server import setting, LabradServer
import socket
import time
import logging
from queue import Queue
from threading import Thread

logging.basicConfig(level=logging.DEBUG)

class ESP302Server(LabradServer):
    """
    LabRAD server for controlling the Newport ESP 302 motion controller over Ethernet (TCP/IP).
    """
    name = 'ESP302Server'

    def initServer(self):
        """
        Initialize the server and open a TCP connection to the ESP 302 controller.
        """
        self.esp_ip = '192.168.123.90'
        self.esp_port = 5001
        self.timeout = 1  # Default timeout for socket operations in seconds
        self.command_queue = Queue()  # Command queue
        self.sock = None
        self.reconnect()

        # # Start a thread for command processing
        # self.command_thread = Thread(target=self.process_commands)
        # self.command_thread.daemon = True
        # self.command_thread.start()

    def reconnect(self):
        """
        Attempt to reconnect if the connection is lost.
        """
        try:
            if self.sock:
                self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.esp_ip, self.esp_port))
            logging.info(f"Connected to ESP 302 at {self.esp_ip}:{self.esp_port}")
        except socket.error as e:
            logging.error(f"Error connecting to ESP 302: {e}")
            time.sleep(5)
            self.reconnect()  # Retry after a short delay

    def send_command(self, command):
        """
        Send a command to the ESP 302 and return its response.
        """
        try:
            command_with_termination = command + '\r\n'
            self.sock.sendall(command_with_termination.encode())
            time.sleep(0.1)
        except socket.error as e:
            logging.error(f"Error sending command: {e}")
            self.reconnect()  # Attempt to reconnect if an error occurs
            return None
        
    def query_command(self, command):
        """
        Send a command to the ESP 302 and return its response.
        """
        try:
            command_with_termination = command + '\r\n'
            self.sock.sendall(command_with_termination.encode())
            time.sleep(0.1)
            response = self.sock.recv(1024).decode().strip()
            logging.info(f"Sent: {command}, Received: {response}")
            return response
        except socket.error as e:
            # Check for specific disconnection errors
            if e.errno in (socket.errno.ECONNRESET, socket.errno.EPIPE):
                logging.error(f"Disconnection error: {e}")
                self.reconnect()  # Attempt to reconnect if a disconnection error occurs
            else:
                logging.error(f"Error sending command: {e}")
            return "fail"

    # def process_commands(self):
    #     """
    #     Continuously process commands from the queue.
    #     """
    #     while True:
    #         command, callback = self.command_queue.get()
    #         response = self.send_command(command)
    #         if callback:
    #             callback(response)
    #         self.command_queue.task_done()

    # def queue_command(self, command, callback=None):
    #     """
    #     Add a command to the command queue for processing.
    #     """
    #     self.command_queue.put((command, callback))

    # ========== New/Improved Functions ========== #

    def validate_axis(self, axis):
        """
        Validate that the axis number is within valid range.
        """
        if axis not in [1, 2]:
            raise ValueError(f"Invalid axis number: {axis}. Only 1 or 2 are valid.")

    def validate_velocity(self, velocity):
        """
        Validate that the velocity is within a reasonable range.
        """
        if not (0 <= velocity <= 100):
            raise ValueError(f"Invalid velocity: {velocity}. It must be between 0 and 100.")

    def validate_dio_bit(self, bit):
        """
        Validate that the DIO bit is between 0 and 15.
        """
        if not (0 <= bit <= 15):
            raise ValueError(f"Invalid DIO bit: {bit}. It must be between 0 and 15.")

    # @setting(9, 'tcp_query',message ='s', returns='s')
    # def tcp_query(self, c, message):
    #     command = f'{message}'
    #     response = self.send_command(command)
    #     return response
    
    # @setting(9, 'tcp_write',message ='s', returns='')
    # def tcp_write(self, c, message):
    #     command = f'{message}'
    #     response = self.send_command(command)
    
    # @setting(9, 'tcp_read', returns='s')
    # def tcp_read(self, c):
    #     command = f''
    #     response = self.send_command(command)
    #     return response

    @setting(10, 'Move Axis', axis='i', position='v', returns='')
    def move_axis(self, c, axis, position):
        """
        Move a specific axis to the given position.

        Parameters:
        axis: int - The axis to move (1 or 2 for two axes).
        position: float - The position to move the axis to.
        """
        command = f'{axis}PA{position}'
        self.send_command(command)


    @setting(20, 'Get Position', axis='i', returns='v')
    def get_position(self, c, axis):
        """
        Get the current position of a specific axis.

        Parameters:
        axis: int - The axis number (1 or 2).

        Returns:
        float - The current position of the axis.
        """
        command = f'{axis}TP'
        response = self.query_command(command)
        try:
            position = float(response)
        except TypeError:
            position = -20000 #error code
        return position

    @setting(30, 'Home Axis', axis='i', returns='')
    def home_axis(self, c, axis):
        """
        Home a specific axis.

        Parameters:
        axis: int - The axis to home (1 or 2).
        """
        command = f'{axis}OR'
        response = self.send_command(command)

    @setting(40, 'Stop All Motion', returns='')
    def stop_all_motion(self, c):
        """
        Stop all motion on all axes.
        """
        command = 'ST'
        response = self.send_command(command)
        self.send_command(command)


    # # Move to Relative Position (PR)
    # @setting(100, 'Move Relative', axis='i', distance='v', returns='')
    # def move_relative(self, c, axis, distance):
    #     self.validate_axis(axis)
    #     command = f'{axis}PR{distance}'
    #     self.send_command(command)

    # Stop Motion (ST)
    @setting(110, 'Stop Motion', returns='')
    def stop_motion(self, c):
        command = 'ST'
        self.send_command(command)

    # # Read Error Code (TE)
    # @setting(120, 'Get Error Code', returns='s')
    # def get_error_code(self, c):
    #     command = 'TE'
    #     response = self.query_command(command)
    #     return f'Error message: {response}'

    # # Read Error Message (TB)
    # @setting(130, 'Get Error Message', returns='s')
    # def get_error_message(self, c):
    #     command = 'TB'
    #     response = self.query_command(command)
    #     return f'Error message: {response}'

    # #Wait Stop
    @setting(140, 'Wait Stop', axis='i', milliseconds='v', returns='')
    def wait_stop(self, c, axis, milliseconds):
        self.validate_axis(axis)
        command = f'{axis}WS{milliseconds}'
        self.send_command(command)


    # Set Velocity (VA)
    @setting(150, 'Set Velocity', axis='i', velocity='v', returns='')
    def set_velocity(self, c, axis, velocity):
        # self.validate_axis(axis)
        # self.validate_velocity(velocity)
        command = f'{axis}VA{velocity}'
        self.send_command(command)

    # Set Acceleration (AC)
    @setting(160, 'Set Acceleration', axis='i', acceleration='v', returns='')
    def set_acceleration(self, c, axis, acceleration):
        self.validate_axis(axis)
        command = f'{axis}AC{acceleration}'
        self.send_command(command)

    # Motor On (MO)
    @setting(170, 'Motor On', axis='i', returns='')
    def motor_on(self, c, axis):
        self.validate_axis(axis)
        command = f'{axis}MO'
        self.send_command(command)

    # Set Deceleration (AG)
    @setting(180, 'Set Deceleration', axis='i', deceleration='v', returns='')
    def set_deceleration(self, c, axis, deceleration):
        self.validate_axis(axis)
        command = f'{axis}AG{deceleration}'
        self.send_command(command)

    # Assign DIO Bits for Motion Status (BM)
    @setting(190, 'Assign DIO Bits Motion Status', axis='i', bit_num='i', bit_level='i', returns='')
    def assign_dio_motion_status(self, c, axis, bit_num, bit_level):
        self.validate_axis(axis)
        self.validate_dio_bit(bit_num)
        command = f'{axis}BM{bit_num},{bit_level}'
        self.send_command(command)

    # Enable DIO Bits for Motion Status (BN)
    @setting(200, 'Enable DIO Bits Motion Status', axis='i', enable='b', returns='')
    def enable_dio_motion_status(self, c, axis, enable):
        self.validate_axis(axis)
        command = f'{axis}BN{1 if enable else 0}'
        self.send_command(command)

    # Set DIO Port Direction (BO)
    @setting(210, 'Set DIO Port Direction', direction='s', returns='')
    def set_dio_port_direction(self, c, direction):
        command = f'BO{direction}'
        self.send_command(command)

    def stopServer(self):
        """
        Close the TCP connection when the server is stopped.
        """
        try:
            self.sock.close()
            logging.info("Closed connection to ESP 302")
        except socket.error as e:
            logging.error(f"Error closing connection: {e}")

if __name__ == "__main__":
    from labrad import util
    util.runServer(ESP302Server())
