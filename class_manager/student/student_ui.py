import paho.mqtt.client as mqtt
import logging
from threading import Thread
import stmpy
import json
from appJar import gui
from class_manager.config import MQTT_BROKER, MQTT_PORT, MQTT_BASE_TOPIC




class StudentUISTM:
    """
    The component to send voice commands.
    """

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        #command = payload.get("command")
        try:
            if msg.topic == self.attendance_status_topic:
                data = payload.get("data")
                name = data.get("name")
                success = data.get("success")
                print("got status back")
                print(success)
                if name == self.name and success:
                    # go to task
                    self.subscribe_to_group()
                    self.stm.send("tasks")
            print(self.task_topic)
            if msg.topic == self.task_topic:
                print("got new task")
                self.current_task_text = payload.get("current_task")
                self.stm.send("current_task")


            if msg.topic == self.help_topic:
                group = payload.get("data").get("group")
                if group != self.group_name:
                    return 
                t = payload.get("type")
                if t == "request_help":
                    # Update help text
                    self.help_request()
                    
                elif t == "got_help":
                    self.app.setLabel("Help", "TA is on their way")
                elif t == "help_complete":
                    self.help_complete()
            print(msg.payload)
        except Exception as e:
            print(e)

    def __init__(self):
        self.app = None
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

        self.attendance_topic = f"{MQTT_BASE_TOPIC}/attendance"
        self.attendance_status_topic = f"{MQTT_BASE_TOPIC}/attendance/status"
        self.team_topic = ""
        self.task_topic = ""
        self.help_topic = f"{MQTT_BASE_TOPIC}/help"


        self.mqtt_client.subscribe(self.attendance_status_topic)
        self.mqtt_client.subscribe(self.help_topic)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.group_name = ""
        self.name = ""
        self.code = ""


        self.current_task_text = "Loading ..."
        self.setup_stm()

        
    def send(self, topic: str, message: object):
        self.mqtt_client.publish(topic, json.dumps(message))

    def subscribe_to_group(self):
        self.team_topic = f"{MQTT_BASE_TOPIC}/{self.group_name}"
        self.task_topic = f"{self.team_topic}/students"
        self.mqtt_client.subscribe(self.team_topic)
        self.mqtt_client.subscribe(self.task_topic)

        self.request_group_task()

    def request_group_task(self):
        self.send(self.team_topic, {"type": "request"})

    def setup_gui(self):
        print("GUI time")
        self.app = gui()
        with self.app.frameStack("frames"):
            for loop in range(3):
                with self.app.frame():
                    if loop == 2:
                        self.setup_help_gui()
                    elif loop == 1:
                        self.setup_attendance_gui()
                    elif loop == 0:
                        self.setup_task_gui()
        self.attendance_gui()
        self.app.go()
        


    def show_task(self):
        print("entered task!")
        

    def register_attendance(self):
        print("attendance")
    
    def help(self):
        print("help")

    def setup_stm(self):

        task = {
            'name': 'task',
            'entry': 'task_gui',
        }
        register_attendance = {
            'name': 'register_attendance',
            'entry': 'attendance_gui',
        }
        help = {
            'name' : 'help',
            'entry' : 'help_gui',
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

        t7 = {
            'source': 'task',
            'target': 'help',
            'trigger': 'help'
        }

        t8 = {
            'source': 'help',
            'target': 'task',
            'trigger': 'return'
        }



        self.stm = stmpy.Machine(name='student_ui', transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8], states=[register_attendance, task, help], obj=self)


    def help_request(self):
        self.app.disableButton("Request help")
        self.app.setLabel("Help", "Waiting for TA to help you")
    def help_complete(self):
        print("enableing button again")
        self.app.enableButton("Request help")

    def register_attendance(self):
        print("trying to send")
        self.name = self.app.getEntry("Name")
        self.group_name = self.app.getEntry("Group")
        self.code = self.app.getEntry("Code")

        print(self.name)
        print(self.group_name)
        print(self.code)
        message = {
            "type": "register",
            "data": {
                "name": self.name,
                "group": self.group_name,
                "code": self.code,
            }
            
        }
        self.mqtt_client.publish(self.attendance_topic, json.dumps(message))

    def setup_attendance_gui(self):
        def task():
            self.stm.send("task_view")
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "task_view"}))

        self.app.addLabel("Name")
        self.app.addEntry("Name")

        self.app.addLabel("Group")
        self.app.addEntry("Group")

        self.app.addLabel("Code")
        self.app.addEntry("Code")

        self.app.addButton('Attendance', self.register_attendance)

    def setup_task_gui(self):
        def next_task():
            self.send(self.team_topic, {"type": "next_task"})
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "next_task"}))

        def previous_task():
            self.send(self.team_topic, {"type": "prev_task"})
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "previous_task"}))

        """ def request_help():
            self.send(self.help, {"type": "request_help", "group_name": self.group_name})
            #self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "request_help"})) """

        
        def go_back():
            self.stm.send("return")

        def help():
            self.stm.send("help")
        
        self.app.addLabel("Task", self.current_task_text)
        self.app.addButton('Next', next_task)
        self.app.addButton('Previous', previous_task)
        self.app.addButton('Help', help)
        self.app.addButton('back', go_back)
    
    def request_help(self):
        print("Help is on the way")
        message = {
            "type" : "request_help",
            "data": {
                "group" : self.group_name,
                "task" : self.current_task_text,
                }
        }
        self.send(self.help_topic, message)
        


    def setup_help_gui(self):
        def go_back_help():
            self.send(self.help_topic, {"type": "help_complete", "group_name": self.group_name})
            self.stm.send("return")
        
        self.app.addLabel("Help", "...")
        self.app.addButton('Go back', go_back_help)
        self.app.addButton('Request help', self.request_help)

    def help_gui(self):
        if self.app is not None:
            self.app.selectFrame("frames", 2)
            #self.app.setLabel("Help", "Help is on the way")

    def attendance_gui(self):
        if self.app is not None:
            self.app.selectFrame("frames", 1)

    def task_gui(self):
        if self.app is not None:
            self.app.selectFrame("frames", 0)
            self.app.setLabel("Task", self.current_task_text)



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