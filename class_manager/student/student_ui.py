import paho.mqtt.client as mqtt
import logging
from threading import Thread
import stmpy
import json
from appJar import gui
from class_manager.config import MQTT_BROKER, MQTT_PORT


MQTT_TOPIC_INPUT = 'ttm4115/team3/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team3/answer'


class StudentUISTM:
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


    def show_task(self):
        print("task")

    def register_attendance(self):
        print("attendance")

    def setup_stm(self):

        task = {
            'name': 'task',
            'entry': 'show_task',
        }
        register_attendance = {
            'name': 'register_attendance',
            'entry': 'attendance_registration',
        }

        t0 = {
            'source': 'initial',
            'target': 'register_attendance',
        }

        t1 = {
            'source': 'register_attendance',
            'target': 'task',
            'trigger': 'tasks',
        }

        t2 = {'source': 'task', 
              'target': 'register_attendance', 
              'trigger': 'return'}

        t3 = {
            'source': 'task',
            'target': 'task',
            'trigger': 'current_task',
        }

        t4 = {
            'source': 'task',
            'target': 'task',
            'trigger': 'click_prev',
        }
        t5 = {
            'source': 'task',
            'target': 'task',
            'trigger': 'click_help',
        }
        t6 = {
            'source': 'task',
            'target': 'task',
            'trigger': 'click_next',
        }


        self.stm = stmpy.Machine(name='student_ui', transitions=[t0, t1, t2, t3, t4, t5, t6], states=[register_attendance, task], obj=self)

    def create_gui(self):
        self.app = gui()
        def test():
            self.stm.send("register_attendance")
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