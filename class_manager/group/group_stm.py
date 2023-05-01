import paho.mqtt.client as mqtt
import stmpy
import logging
import json
import time
from class_manager.class_manager.db import Database
from class_manager.config import MQTT_BASE_TOPIC, MQTT_BROKER, MQTT_PORT


class GroupLogic:
    def __init__(self, name: str, class_manager):
        # Internal states
        self.name = name
        self.current_task = 0
        self.task_times = {}  # task nbr -> time
        self.class_manager = class_manager
        self.current_task_start_time = time.time()
        self.members = []
        self.ta = ""

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print("logging under name {}.".format(__name__))
        self._logger.info("Starting Component")

        # create a new MQTT client
        self._logger.debug(
            "Connecting to MQTT broker {} at port {}".format(MQTT_BROKER, MQTT_PORT)
        )
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
        self.internal_topic = f"{MQTT_BASE_TOPIC}/progress/internal"

        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(self.group_topic)
        self.mqtt_client.subscribe(self.help_topic)

        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self._logger.debug("Component initialization finished")

        self.setup_stm()

    def add_member(self, name: str):
        if not name in self.members:
            self.members.append(name)

    def start_new_task(self):
        # calculate diff from last
        duration = time.time() - self.current_task_start_time
        if self.current_task in self.task_times:
            self.task_times[self.current_task] += duration
        else:
            self.task_times[self.current_task] = duration

        self.current_task_start_time = time.time()
        self.update_class_manager()

    def send(self, topic: str, message: object):
        self.mqtt_client.publish(topic, json.dumps(message))

    def on_message(self, client, userdata, msg):
        """
        Receiving messages on MQTT
        """
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error(
                "Message sent to topic {} had no valid JSON. Message ignored. {}".format(
                    msg.topic, err
                )
            )
            return

        try:
            if msg.topic == self.group_topic:
                command = payload.get("type")
                if command == "next_task":
                    self.stm.send("next_task")

                elif command == "prev_task":
                    self.stm.send("prev_task")
                elif command == "request":
                    self.send_current_task()
                elif command == "status":
                    self.send_status()

            if msg.topic == self.help_topic:
                group = payload.get("group")
                command = payload.get("type")
                if group == self.name:
                    if command == "request_help":
                        self.stm.send("ask_for_help")
                    if command == "offer_help":
                        self.ta = payload.get("ta")
                        self.stm.send("offer_help")
                    if command == "help_complete":
                        self.ta = ""
                        self.stm.send("help_complete")
        except Exception as err:
            print(err)

    def get_task(self):
        """
        Returns the task with the given task number
        """
        db = Database()
        total_tasks = db.nbr_questions()
        if self.current_task == total_tasks:
            self.current_task = 0
        elif self.current_task < 0:
            self.current_task = total_tasks - 1

        return db.get_question(self.current_task)

    def on_connect(self, client, userdata, flags, rc):
        self._logger.info("Connected")

    def setup_stm(self):
        t0 = {"source": "initial", "target": "working", "effect": "group_working"}
        t1 = {
            "source": "working",
            "target": "needs_help",
            "trigger": "ask_for_help",
            "effect": "update_class_manager",
        }
        t2 = {
            "source": "needs_help",
            "target": "getting_help",
            "trigger": "offer_help",
            "effect": "got_help;update_class_manager",
        }
        t3 = {
            "source": "getting_help",
            "target": "working",
            "trigger": "help_complete",
            "effect": "update_class_manager",
        }

        t4 = {
            "source": "working",
            "target": "working",
            "trigger": "next_task",
            "effect": "next_task",
        }

        t5 = {
            "source": "working",
            "target": "working",
            "trigger": "prev_task",
            "effect": "prev_task",
        }

        t6 = {"source": "needs_help", "target": "working", "trigger": "help_complete"}

        self.stm = stmpy.Machine(
            name=self.name, transitions=[t0, t1, t2, t3, t4, t5, t6], obj=self
        )

    def send_status(self):
        message = {
            "type": "status_response",
            "data": {
                "group": self.name,
                "current_task": self.current_task,
                "state": self.stm.state,
                "ta": self.ta,
            },
        }

        self.send(self.group_topic, message)

    def got_help(self):
        message = {"type": "got_help", "group": self.name, "ta": self.ta}
        self.send(self.help_topic, message)

    def update_class_manager(self):
        self.send(self.internal_topic, {"type": "progress_update"})

    def group_working(self):
        message = f"Group {self.name} is working"
        self._logger.debug(message)

    def help_offered(self):
        message = f"Group {self.name} is getting help"
        self._logger.debug(message)

    def send_current_task(self):
        task = self.get_task()
        payload = {"current_task": task}
        self.send(self.group_task_topic, payload)
        self.update_class_manager()

    def next_task(self):
        self.start_new_task()
        self.current_task += 1
        self.send_current_task()

    def prev_task(self):
        self.start_new_task()
        self.current_task -= 1
        self.send_current_task()
