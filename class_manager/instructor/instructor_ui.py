import paho.mqtt.client as mqtt
import logging
from threading import Thread
import stmpy
import json
from appJar import gui
from class_manager.config import MQTT_BROKER, MQTT_PORT


MQTT_TOPIC_INPUT = 'ttm4115/team3/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team3/answer'


class InstructorUISTM:
    """
    The component to send voice commands.
    """

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):

        print(msg.payload)
        pass

    def __init__(self):
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()



        self.setup_stm()


    def show_menu(self):
        print("menu")

    def show_attendance(self):
        print("attendance")

    def setup_stm(self):

        menu = {
            'name': 'menu',
            'entry': 'show_menu',
        }
        display_attendance = {
            'name': 'display_attendance',
            'entry': 'show_attendance',
        }

        t0 = {
            'source': 'initial',
            'target': 'menu',
        }

        t1 = {
            'source': 'menu',
            'target': 'display_attendance',
            'trigger': 'display_attendance',
        }

        t2 = {'source': 'display_attendance', 'target': 'menu', 'trigger': 'return'}

        t3 = {
            'source': 'menu',
            'target': 'group_overview',
            'trigger': 'group_overview',
        }

        t4 = {
            'source': 'group_overview',
            'target': 'menu',
            'trigger': 'return',
        }


        self.stm = stmpy.Machine(name='faculty_ui', transitions=[t0, t1, t2, t3, t4], states=[menu, display_attendance], obj=self)

    def create_gui(self):
        self.app = gui()
        def test():
            self.stm.send("display_attendance")
        self.app.addButton('Testing', test)

        self.app.go()


    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()


# logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
