import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json
from class_manager.config import MQTT_BROKER, MQTT_PORT


MQTT_TOPIC_INPUT = 'ttm4115/team3/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team3/answer'

class InstructorSTM:
    """
    State Machine for a named timer.

    This is the support object for a state machine that models a single timer.
    """
    def __init__(self, name, duration, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.duration = duration
        self.component = component

        t0 = {'source': 'initial',
              'target': 'available'}
        t1 = {
            'source': 'available',
            'target': 'unavailable',
            'trigger': 'help_student',
            }
        t2 = {
            'source': 'unavailable',
            'target': 'available',
            'trigger': 'help_finished'}
        self.stm = stmpy.Machine(name=name, transitions=[t0, t1, t2], obj=self)
