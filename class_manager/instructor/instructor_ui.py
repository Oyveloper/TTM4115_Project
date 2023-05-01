import paho.mqtt.client as mqtt
import logging
from threading import Thread
import stmpy
import json
import tkinter
from appJar import gui
from class_manager.config import MQTT_BASE_TOPIC, MQTT_BROKER, MQTT_PORT

# self.mqtt_client.send(f"{GROUP_TOPIC_BASE}/{self.group_name}", json.dumps({"type": "task_view"}))

class InstructorUISTM:
    """
    The component to send commands.
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
        
        if msg.topic == self.group_update_topic:
            if payload.get("type") == "progress":
                data = payload.get("data")
                self.groups_list = data
                
                        
                self.stm.send("new_group_data")

        if msg.topic == self.statistics_update_topic:
            if payload.get("type") == "stats":
                data = payload.get("data")
                self.statistics_list = ""
                for task, time in data.items():
                    self.statistics_list += f"Task: {task}: Time: {time}\n"
                self.stm.send("new_statistics_data")

        if msg.topic == self.attendance_update_topic:
            if payload.get("type") == "list":
                data = payload.get("data")
                self.attendance_list = ""
                for student in data:
                    self.attendance_list += f"{student.get('group')}: Name: {student.get('name')}\n"
                self.stm.send("new_attendance_data")
                print("got attendance")
        print(msg.payload)
        

    def __init__(self):
        self.instructor_name = ""
        self.groups_list = ""
        self.statistics_list = ""
        self.attendance_list = ""

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

        self.group_update_topic = f"{MQTT_BASE_TOPIC}/progress"
        self.statistics_update_topic = f"{MQTT_BASE_TOPIC}/statistics"
        self.attendance_update_topic = f"{MQTT_BASE_TOPIC}/attendance"
        self.help_topic = f"{MQTT_BASE_TOPIC}/help"

        self.mqtt_client.subscribe(self.group_update_topic)
        self.mqtt_client.subscribe(self.statistics_update_topic)
        self.mqtt_client.subscribe(f"{self.attendance_update_topic}")
        self.mqtt_client.subscribe(self.help_topic)

        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()


        self.setup_stm()


    def setup_stm(self):

        login = {
            'name': 'login',
            'entry' : 'login_gui',
        }

        menu = {
            'name': 'menu',
            'entry': 'menu_gui',
        }

        display_attendance = {
            'name': 'display_attendance',
            'entry': 'attendance_gui',
        }

        statistics = {
            'name': 'statistics',
            'entry': 'statistics_gui',
        }

        group_overview = {
            'name': 'group_overview',
            'entry': 'group_overview_gui',
        }

        t0 = {
            'source': 'initial',
            'target': 'login',
        }

        t_attendance = {
            'source': 'menu',
            'target': 'display_attendance',
            'trigger': 'display_attendance',
            'effect' : 'request_attendance_update',
        }

        t_return1 = {
            'source': 'display_attendance',
            'target': 'menu',
            'trigger': 'menu'
            }

        t_groups = {
            'source': 'menu',
            'target': 'group_overview',
            'trigger': 'group_overview',
            'effect': 'request_group_update',
        }

        t_return2 = {
            'source': 'group_overview',
            'target': 'menu',
            'trigger': 'menu',
        }

        t_statistics = {
            'source': 'menu',
            'target': 'statistics',
            'trigger': 'statistics',
            'effect': 'request_statistics_update',
        }

        t_return3 = {
            'source': 'statistics',
            'target': 'menu',
            'trigger': 'menu'
        }

        t_login_menu = {
            'source' : 'login',
            'target' : 'menu',
            'trigger': 'menu'
        }
        t_group_group = {
            'source': 'group_overview',
            'target': 'group_overview',
            'trigger': 'new_group_data'
        }

        t_statistics_statistics = {
            'source': 'statistics',
            'target' : 'statistics',
            'trigger' : 'new_statistics_data',
        }

        t_attendance_attendance = {
            'source' : 'display_attendance',
            'target' : 'display_attendance',
            'trigger' : 'new_attendance_data',
        }

        self.stm = stmpy.Machine(name='instructor_ui', transitions=[t0, t_login_menu, t_attendance, t_return1, t_groups, t_return2, t_statistics, t_return3, t_group_group, t_statistics_statistics, t_attendance_attendance], states=[login, menu, display_attendance, statistics, group_overview], obj=self)


    def create_gui(self):
        self.app = gui("Instructor", "500x500")
        with self.app.frameStack("frames"):
            for loop in range(5):
                with self.app.frame():
                    if loop == 1:
                        self.setup_statistics_gui()
                    elif loop == 2:
                        self.setup_group_overview_gui()
                    elif loop == 3:
                        self.setup_menu_gui()
                    elif loop == 4:
                        self.setup_login_gui()
                    else:
                        self.setup_attendance_gui()
        self.app.go()

    # div functions
    def send(self, topic: str, message: object):
        self.mqtt_client.publish(topic, json.dumps(message))

    def request_group_update(self):
        self.send(self.group_update_topic, {
            "type": "request"
        })

    def request_statistics_update(self):
        self.send(self.statistics_update_topic, {
            "type": "request"
        })

    def request_attendance_update(self):
        self.send(self.attendance_update_topic, {
            "type": "get"
        })

    def send_help_group(self, group):
        self.send(self.help_topic, {
            "type" : "offer_help", "ta" : self.instructor_name, "group" : group
        })

    # View functions

    def login_to_menu_view(self):

        self.instructor_name = self.app.getEntry("name")
        print(self.instructor_name)
        self.stm.send("menu")

    def menu_view(self):
        print("menu view")
        self.stm.send("menu")

    def attendance_view(self):
        print("attendance view")
        self.stm.send("display_attendance")

    def group_overview_view(self):
        print("group view")
        self.stm.send("group_overview")

    def statistics_view(self):
        print("statistics view")
        self.stm.send("statistics")


    # GUIs

    def setup_attendance_gui(self):
        self.app.addLabel("Attendance")
        self.app.addLabel("attendance_label", "...")
        self.app.addButton('Back ', self.menu_view)

    def setup_statistics_gui(self):
        self.app.addLabel("Statistics")
        self.app.addLabel("statistics_label", "...")
        self.app.addButton('Back   ', self.menu_view)

    def setup_group_overview_gui(self):
        self.app.addLabel("Group overview")
        self.app.startFrame("GROUP_LIST")
        self.app.stopFrame()
        self.app.addButton('Back  ', self.menu_view)

    def setup_menu_gui(self):
        self.app.addButton('Attendance', self.attendance_view)
        self.app.addButton('Group overview', self.group_overview_view)
        self.app.addButton('Statistics', self.statistics_view)

    def setup_login_gui(self):
        self.app.addLabel("Instructor's name")
        self.app.addEntry("name")
        self.app.addButton("Login", self.login_to_menu_view)

    # Framestack

    def login_gui(self):
        if self.app is not None:
            self.app.selectFrame("frames", 4)

    def menu_gui(self):
        if self.app is not None:
            self.app.selectFrame("frames", 3)

    def group_overview_gui(self):
        if self.app is not None:
            
            self.app.selectFrame("frames", 2)
            with self.app.frame("GROUP_LIST"):
                self.app.emptyCurrentContainer()
                row = 1
                for i, group in enumerate(self.groups_list):
                    ta_text = f"({group.get('ta')})" if group.get('state') == "getting_help" else ""
                    self.app.addLabel(f"Description_{group.get('group')}", f"{group.get('group')}, Task: {group.get('task')}, state: {group.get('state')} {ta_text}", row+i, 0)
                    def press(btn_title: str):
                        group_parts = btn_title.split(" ")[1:]
                        group = " ".join(group_parts)
                        print(f"Helping {group}")
                        self.send_help_group(group)
                    if group.get('state') == "needs_help":
                        self.app.addButton(f"Help {group.get('group')}", press, row+i, 1)

    def statistics_gui(self):
        if self.app is not None:
            self.app.selectFrame("frames", 1)
            self.app.setLabel("statistics_label", self.statistics_list)

    def attendance_gui(self):
        if self.app is not None:
            self.app.selectFrame("frames", 0)
            self.app.setLabel("attendance_label", self.attendance_list)


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
