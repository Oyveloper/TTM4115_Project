import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json
from class_manager.config import MQTT_BASE_TOPIC, MQTT_BROKER, MQTT_PORT

class GroupLogic:
    def __init__(self, name: str, class_manager):
        self.name = name
        self.current_task = 0
        self.class_manager = class_manager()

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

        # Topics
        self.group_topic = f"{MQTT_BASE_TOPIC}/{self.name}"
        self.group_task_topic = f"{self.group_topic}/students"
        self.help_topic = f"{MQTT_BASE_TOPIC}/help"

        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(group_topic)
        self.mqtt_client.subscribe(self.help_topic)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self._logger.debug('Component initialization finished')


        
        self.setup_stm()

    def on_message(self, message):

        """
        Receiving messages on MQTT
        """
        print(message.payload)


    def on_connect(self):
        self._logger.info("Connected")

        # example
        self.stm.send("offer_help")
        
    def setup_stm(self):
        t0 = {'source': 'initial',
              'target': 'working'}
        t1 = {
            'source': 'working',
            'target': 'needs_help',
            'trigger': 'ask_for_help',
            'effect': 'group_working'}
        t2 = {
            'source': 'needs_help',
            'trigger': 'offer_help',
            'target': 'getting_help',
            'effect': 'request_help'}
        t3 = {
            'source': 'getting_help',
            'trigger': 'help_complete',
            'target': 'working',
            'effect': 'help_offered'}

        t4 = {
            'source': 'working',
            'target': 'working',
            'trigger': 'next_task',
            'effect': 'next_task'
        }

        t5 = {
            'source': 'working',
            'target': 'working',
            'trigger': 'prev_task',
            'effect': 'prev_task'
        }

        self.stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t3, t4, t5], obj=self)

    def group_working(self):
        message = f"Group {self.name} is working"
        self._logger.debug(message)

    def request_help(self):
        message = f"​​​​​​​​​​type: request_help, group: {self.name}​​​​​​​​​"
        self._logger.debug(message)
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, message)

    def help_offered(self):
        message = f"Group {self.name} is getting help"
        self._logger.debug(message)

    def help_complete(self):
        message = f"​​​​​​​​​​type: help_complete, group: {self.name}​​​​​​​​​"
        self._logger.debug(message)
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, message)

    def send_current_task(self):
        payload = {
            "team": self.name,
            "current_task": self.current_task
        }
        self.mqtt_client.publish('ttm4115/team3/students', json.dumps(payload))

    def next_task(self):
        send_current_task()
        self.current_task += 1
        self.class_manager.send_next_task(self.name)

    def prev_task(self):
        send_current_task()
        self.current_task -= 1
        self.class_manager.send_prev_task(self.name)
