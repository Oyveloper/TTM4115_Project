import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team3/task'
MQTT_TOPIC_OUTPUT = 'ttm4115/team3/help'

class GroupLogic:
    def __init__(self, name, duration, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.duration = duration
        self.component = component

        t0 = {'source': 'initial',
              'target': 'working'}
        t1 = {
            'source': 'working',
            'target': 'needs_help',
            'trigger': 'request_help'}
        t2 = {
            'source': 'needs_help',
            'trigger': 'offer_help',
            'target': 'getting_help'}
        t3 = {
            'source': 'getting_help',
            'trigger': 'help_complete',
            'target': 'working'}

        self.stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t3], obj=self)
