from machine import UART, Pin
import ujson as json
import logutils
import time

PROCESS_BUFFER_SIZE = 300

AT_OK = 0
AT_ERROR = -1
AT_ERROR_TIMEOUT = -2
AT_ERROR_CMD = -3
AT_ERROR_UNKNOWN = -4

AT_RSP_OK = "OK"
ATE0 = "ATE0"
AT_RSP_ERROR = "ERROR"
AT_CMD_UMQTT = "AT+UMQTT"
AT_CMD_UMQTTER = "AT+UMQTTER"
AT_CMD_UMQTTC = "AT+UMQTTC"
AT_CMD_CGATT = "AT+CGATT"
AT_CMD_UMQTTNV = "AT+UMQTTNV"
AT_CMD_UMNOPROF = "AT+UMNOPROF"
AT_CMD_CFUN = "AT+CFUN"
AT_CMD_CGDCONT = "AT+CGDCONT"


LTEIOT6_CMD_AT = "AT"


class LTEIOT6_Click():
    uart: UART
    power: Pin
    rx_buffer: bytes
    config: dict

    def __init__(self, uart: UART, power: Pin, config: dict):
        self.uart = uart
        self.power = power
        self.rx_buffer = bytes()
        self.logger = logutils.get_logger("LTEIOT6_Click")
        self.config = config

    def init(self) -> int:
        '''
        LTE IOT 6 Click init
        Baudrate: 115200
        data bits: 8
        parity: None
        stop bits: 1
        '''
        self.uart.init(baudrate=115200, bits=8, parity=None, stop=1)
        self.power.init(Pin.OUT)
        self.restart()

        self._send_command(LTEIOT6_CMD_AT)
        error_flag = self._rsp_check()
        self._error_handler(LTEIOT6_CMD_AT, error_flag, "init")

        if error_flag != AT_OK:
            return False
        
        return True

    def restart(self, timeout=30000) -> bool:
        self.power_off()
        time.sleep_ms(1000)
        self.power_on()
        timeout_cnt = 0
        while not self.is_alive():
            timeout_cnt += 200
            if timeout_cnt > timeout:
                return False
            time.sleep_ms(200)

        return True

    def power_on(self):
        self.power.on()

    def power_off(self):
        self.power.off()

    def attach(self, timeout=180000) -> bool:
        self._send_command(ATE0)
        self._error_handler(ATE0, self._rsp_check(), "attach")

        cmd = self._send_command_with_param(AT_CMD_CGATT, [1])
        error_flag = self._rsp_check(timeout)
        self._error_handler(cmd, error_flag, "attach")
        if error_flag == AT_ERROR_TIMEOUT:
            self.logger.error("Timeout waiting for response", fn="attach")
            connected = self._configure_network()            
        else:
            self._send_command_check(AT_CMD_CGATT)
            self._error_handler(cmd, self._rsp_check(), "attach")
            if f"{AT_CMD_CGATT[2:]}: 1" in self.rx_buffer: # type: ignore
                connected = True
            else:
                connected = False

        if not connected:
            self.logger.error("Failed to connect to the network", fn="attach")
            return connected

        return connected
    
    def send_message(self, message: str, timeout=60000) -> bool:
        mqtt_id = self.config.get("mqtt_id", None)
        mqtt_server_address = self.config.get("mqtt_server_address", None)
        mqtt_sever_port = self.config.get("mqtt_server_port", None)
        mqtt_topic = self.config.get("mqtt_topic", None)
        mqtt_username = self.config.get("mqtt_username", "")
        mqtt_password = self.config.get("mqtt_password", "")
        if mqtt_id is None or mqtt_server_address is None or mqtt_sever_port is None or mqtt_topic is None:
            self.logger.error(f"MQTT configuration missing: id={mqtt_id}, server_address={mqtt_server_address}, server_port={mqtt_sever_port}, topic={mqtt_topic}", fn="send_message")
            return False
        
        success = self.mqtt_publish(mqtt_id, mqtt_sever_port, mqtt_server_address, mqtt_topic, message, mqtt_username, mqtt_password)

        return success

    def mqtt_publish(self, id: str, port: str, server_address: str, topic: str, message: str, username: str="", password: str="") -> bool:
        '''
        Publish a message to a topic on the MQTT broker
        '''
        if not self.is_alive():
            self.logger.error("Module didn't respond.", fn="mqtt_publish")
            return False

        if not self.attach():
            return False

        cmd = self._send_command_with_param(AT_CMD_UMQTTNV, [1])
        self._error_handler(cmd, self._rsp_check(), "mqtt_publish")

        # Check current config
        cmd = self._send_command_check(AT_CMD_UMQTT)
        self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
        current_config = self.rx_buffer

        # Check if current config is not the same as the new config
        if is_valid_mqtt_config(id, port, server_address) and not match_current_config(current_config, id, port, server_address, username):
            self.logger.info(f"Setting new MQTT configuration: id={id}, port={port}, address={server_address}, username={username}", fn="mqtt_publish")

            cmd = self._send_command_with_param(AT_CMD_UMQTTC, [0])
            self._error_handler(cmd, self._rsp_check(), "mqtt_publish")

            cmd = self._send_command_with_param(AT_CMD_UMQTTNV, [0])
            self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
    
            cmd = self._send_command_with_param(AT_CMD_UMQTT, [0,id])
            self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
            
            cmd = self._send_command_with_param(AT_CMD_UMQTT, [1,0])
            self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
    
            cmd = self._send_command_with_param(AT_CMD_UMQTT, [3,server_address,int(port)])
            self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
            if f"{AT_CMD_UMQTT[2:]}: 3,0" in self.rx_buffer:  # type: ignore
                cmd = self._send_command_with_param(AT_CMD_UMQTT, [2,server_address,int(port)])
                self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
                if f"{AT_CMD_UMQTT[2:]}: 2,0" in self.rx_buffer:    # type: ignore
                    self.logger.error(f"Failed to set MQTT server address '{server_address}' and port '{port}'", fn="mqtt_publish")

            if len(username) > 0 and len(password) > 0:
                cmd = self._send_command_with_param(AT_CMD_UMQTT, [4,username,password])
                self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
            
            cmd = self._send_command_with_param(AT_CMD_UMQTTNV, [2])
            self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
        else:
            self.logger.info("MQTT configuration is the same. Publishing message", fn="mqtt_publish")
        
        cmd = self._send_command_with_param(AT_CMD_UMQTTC, [1])
        error_flag = self._rsp_check(120000)
        self._error_handler(cmd, error_flag, "mqtt_publish")
        if error_flag == AT_ERROR_TIMEOUT or f"{AT_CMD_UMQTTC[2:]}: 1,0" in self.rx_buffer:   # type: ignore
            cmd = self._send_command(AT_CMD_UMQTTER)
            self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
            self.logger.error(f"Failed to connect to MQTT broker: {self.rx_buffer}", fn="mqtt_publish")
            return False
        
        cmd = self._send_command_with_param(AT_CMD_UMQTTC, [2,0,0,topic,message])
        self._error_handler(cmd, self._rsp_check(120000), "mqtt_publish")
        if f"{AT_CMD_UMQTTC[2:]}: 2,1" in self.rx_buffer: # type: ignore
            return True
        else:   # type: ignore
            cmd = self._send_command(AT_CMD_UMQTTER)
            self._error_handler(cmd, self._rsp_check(), "mqtt_publish")
            self.logger.error(f"Failed to publish message to MQTT broker: {self.rx_buffer}", fn="mqtt_publish")
        
        return False

    def _configure_network(self) -> bool:
        cmd = self._send_command_with_param(AT_CMD_UMNOPROF, [0])
        self._error_handler(cmd, self._rsp_check(), "_configure_network")

        reset_success = self.reset()
        if not reset_success:
            return False
        
        cmd = self._send_command_with_param(AT_CMD_CGDCONT, [1,"IP",self.config["apn"]])
        self._error_handler(cmd, self._rsp_check(), "_configure_network")
 
        self._send_command_with_param(AT_CMD_CGATT, [1])
        self._error_handler(cmd, self._rsp_check(180000), "_configure_network")

        if f"{AT_CMD_CGATT[2:]}: 1" in self.rx_buffer: # type: ignore
            return True
        return False

    def _send_command_check(self, command: str):
        command += "?"
        return self._send_command(command)

    def _send_command_with_param(self, command: str, params: list):
        command += "="
        for i, param in enumerate(params):
            if type(param) == str:
                params[i] = f'"{param}"'
        command += ",".join(str(param) for param in params)

        return self._send_command(command)

    def _send_command(self, command: str):
        # Check if there is \r\n\0 at the end of the command
        if command[-2:]!= "\r\n":
            command += "\r\n"
    
        self.uart.write(command)
        time.sleep_ms(100)

        return command
        

    def _rsp_check(self, timeout=1000) -> int:
        '''
        Returns:
            int: Error code
        '''
        timeout_cnt = 0

        error_flag = self._process()
        while (AT_RSP_OK not in self.rx_buffer) and (AT_RSP_ERROR not in self.rx_buffer):   # type: ignore
            timeout_cnt += 100

            error_flag = self._process()

            if error_flag != AT_OK and error_flag != AT_ERROR:
                return error_flag
            
            if timeout_cnt > timeout:
                return AT_ERROR_TIMEOUT
            
            time.sleep_ms(100)

        if AT_RSP_OK in self.rx_buffer:  # type: ignore
            return AT_OK
        elif AT_RSP_ERROR in self.rx_buffer:  # type: ignore
            return AT_ERROR_CMD
        else:
            return AT_ERROR_UNKNOWN


    def _process(self) -> int:
        '''
        Returns:
            int: Error code
        '''

        # Read data from the UART to self.rx_buffer
        rx_size = self._read()
        
        if rx_size > 0:
            return AT_OK

        return AT_ERROR

    def _read(self) -> int:
        '''
        This function reads data from the UART to the rx_buffer.  
        
        Returns:
            int: Length of the data read / Error code
        '''
        self.rx_buffer = self.uart.read()
        if self.rx_buffer is None:
            self.rx_buffer = b''
            return AT_ERROR
        
        return len(self.rx_buffer)
    
    def _error_handler(self, at_cmd: str, error_flag: int, fn_name: str):
        if error_flag == AT_OK:
            self.logger.info(f"Command executed successfully: {at_cmd}", fn=fn_name)
        if error_flag == AT_ERROR:
            self.logger.error(f"Error reading data from uart: {at_cmd}", fn=fn_name)
        elif error_flag == AT_ERROR_TIMEOUT:
            self.logger.error(f"Timeout waiting for response: {at_cmd}", fn=fn_name)
        elif error_flag == AT_ERROR_CMD:
            self.logger.error(f"Error executing command: {at_cmd}, {self.rx_buffer}", fn=fn_name)
        elif error_flag == AT_ERROR_UNKNOWN:
            self.logger.error("Unknown error", fn=fn_name)

    def is_alive(self) -> bool:
        cmd = self._send_command(LTEIOT6_CMD_AT)
        error = self._rsp_check(100)
        if error == AT_OK:
            return True
        return False
    
    def reset(self, timeout=180000) -> bool:
        cmd = self._send_command_with_param(AT_CMD_CFUN, [15])
        self._error_handler(cmd, self._rsp_check(), "reset")
        
        timeout_cnt = 0
        while not self.is_alive():
            timeout_cnt += 100
            if timeout_cnt > timeout:
                return False
            time.sleep_ms(100)
        
        return True




def is_valid_mqtt_config(id: str, port: str, server_address: str) -> bool:
    if id is None or port is None or server_address is None:
        return False

    return True

def match_current_config(current_config: bytes, id: str, port: str, server_address: str, username: str) -> bool:
    if current_config is None:
        return False

    if id in current_config and port in current_config and server_address in current_config and username in current_config:  # type: ignore
        return True

    return False