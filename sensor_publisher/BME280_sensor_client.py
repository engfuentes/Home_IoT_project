import json, os, logging
import bme280, smbus2
from time import sleep
import paho.mqtt.client as mqtt

def logger_config():
    """Sets the logger config"""
    logging.basicConfig(
        filename="./logs.log",
        encoding="utf-8",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

logger = logging.getLogger('BME280_sensor_client')

class BME280_Sensor():
    def __init__(self, address=0x76):
        # Initialize the BME280 sensor
        self.port = 1
        self.address = address
        self.bus = smbus2.SMBus(self.port)

        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)

    def read_data(self):
        # Read the data from the sensor
        self.sensor = bme280.sample(self.bus, self.address, self.calibration_params)

        timestamp = self.sensor.timestamp.isoformat()
        temperature= round(self.sensor.temperature,2) # Celcius degrees
        pressure = round(self.sensor.pressure,2) # hPa
        humidity = round(self.sensor.humidity,2) # %

        return {
                "timestamp": timestamp,
                "temperature": temperature,
                "pressure": pressure,
                "humidity": humidity
                }

class MQTTPublisher():
    def __init__(self, broker, port, topic, username, password):
        # Define MQTT settings
        self.broker = broker
        self.port = port
        self.topic = topic

        # Create an MQTT client instance
        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.on_connect = self.__on_connect
        self.client.on_publish = self.__on_publish
        self.client.username_pw_set(username, password)

    def connect(self):
        # Connect to the MQTT broker
        self.client.connect(self.broker, self.port, 60, properties=None)

    def publish(self, payload):
        # Publish a message
        logger.debug(f"Publishing: {payload}")
        result = self.client.publish(self.topic, json.dumps(payload), qos=1, properties=None)
        
        if result.rc == mqtt.MQTT_ERR_NO_CONN:
            logger.error("Failed to publish: not connected to broker")

    def __on_connect(self, client, userdata, flags, reason_code, properties=None):
        # Log when connects
        if reason_code == "Success":
            logger.info('Connected successfully')
        else:
            logger.error(f'Connection failed with code {reason_code}')

    def __on_publish(self, client, userdata, mid):
        # Log when publish
        logger.info(f"Message {mid} published")

    def loop_start(self):
        # Start the loop
        self.client.loop_start()

    def loop_stop(self):
        # Stops the loop
        self.client.loop_stop()

def main():
    sensor = BME280_Sensor()
    publisher = MQTTPublisher(broker="mosquitto",
                              port=1883,
                              topic="sensor/bme280",
                              username=os.getenv("MOSQUITTO_USERNAME"),
                              password=os.getenv("MOSQUITTO_PASSWORD"))

    publisher.loop_start()
    publisher.connect()
    
    
    try:
        while True:
            data = sensor.read_data()
            publisher.publish(data)
            sleep(15) 
    except KeyboardInterrupt:
        logger.info("Exiting due to KeyboardInterrupt...")
    finally:
        logger.info("Closing the loop...")
        publisher.loop_stop()

if __name__ == "__main__":
    logger_config()
    main()