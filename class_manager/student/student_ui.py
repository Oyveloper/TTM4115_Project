import paho.mqtt.client as mqtt
import logging
from threading import Thread
import stmpy
import json
from appJar import gui
from class_manager.config import MQTT_BROKER, MQTT_PORT


GROUP_TOPIC_BASE = 'ttm4115/team3'
MQTT_TOPIC_OUTPUT = 'ttm4115/team3'


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
        self.mqtt_client.subscribe(MQTT_TOPIC_OUTPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.group_name = ""

        self.setup_stm()

        


    def setup_gui(self):
        self.app = gui()
        with self.app.frameStack("frames"):
            for loop in range(2):
                with self.app.frame():
                    if loop == 1:
                        self.setup_attendance_gui()
                    else:
                        self.setup_task_gui()
        self.app.go()


    def show_task(self):
        print("entered task!")
    

    def register_attendance(self):
        print("attendance")

    def setup_stm(self):

        task = {
            'name': 'task',
            'entry': 'task_gui',
        }
        register_attendance = {
            'name': 'register_attendance',
            'entry': 'attendance_gui',
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


    def register_attendance(self):
        print("trying to send")
        self.stm.send("tasks")

    def update_task(self, task: str):
        self.app.setLabel("Task", task)


    def setup_attendance_gui(self):
        def task():
            self.stm.send("task_view")
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "task_view"}))

        self.app.addEntry("Name")
        self.app.addEntry("Group")
        self.app.addButton('Attendance', self.register_attendance)

    def setup_task_gui(self):
        def next_task():
            self.stm.send("next_task")
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "next_task"}))

        def previous_task():
            self.stm.send("previous_task")
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "previous_task"}))

        def request_help():
            self.stm.send("request_help")
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "request_help"}))

        def current_task():
            self.stm.send("current_task")
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "current_task"}))
        
        def go_back():
            self.stm.send("return")
        self.app.addLabel("Task", "noe greier")
        self.app.addButton('Next', next_task)
        self.app.addButton('Previous', previous_task)
        self.app.addButton('Help', request_help)
        self.app.addButton('Current', current_task)

        self.app.addButton('back', go_back)


    def attendance_gui(self):
        self.app.selectFrame("frames", 1)

    def task_gui(self):
        self.app.selectFrame("frames", 0)



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