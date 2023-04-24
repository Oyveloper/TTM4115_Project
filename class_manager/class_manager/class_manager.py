import json
import paho.mqtt.client as mqtt
import logging
import stmpy
from class_manager.class_manager.db import Database

from class_manager.config import MQTT_BASE_TOPIC, MQTT_BROKER, MQTT_PORT
from class_manager.group.group_stm import GroupLogic


class ClassManagerSTM:
    """
    This STM manages all the groups in the class, and handles some system actions and statistics
    """

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug("MQTT connected to {}".format(client))

    def on_message(self, client, userdata, msg):
        """
        Processes incoming MQTT messages.

        We assume the payload of all received MQTT messages is an UTF-8 encoded
        string, which is formatted as a JSON object. The JSON object contains
        a field called `command` which identifies what the message should achieve.

        As a reaction to a received message, we can for example do the following:

        """
        self._logger.info("Incoming message to topic {}".format(msg.topic))

        try:
            payload = json.loads(msg.payload.decode("utf-8"))

            if msg.topic == self.attendance_topic:
                if payload["type"] == "register":
                    data = payload["data"]
                    name = data["name"]
                    code = data["code"]
                    group = data["group"]

                    self.register_attendance(name, group, code)

        except Exception as err:
            self._logger.error(
                "Message sent to topic {} had no valid JSON. Message ignored. {}".format(
                    msg.topic, err
                )
            )
            return

    def __init__(self, code: str):
        """
        Start the component.

        ## Start of MQTT
        We subscribe to the topic(s) the component listens to.
        The client is available as variable `self.client` so that subscriptions
        may also be changed over time if necessary.

        The MQTT client reconnects in case of failures.

        """
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

        # topic
        self.progress_topic = f"{MQTT_BASE_TOPIC}/progress"
        self.progress_internals_topic = f"{self.progress_topic}/internal"

        self.stat_topic = f"{MQTT_BASE_TOPIC}/statistics"
        self.stat_itnernal_topic = f"{self.stat_topic}/internal"

        self.attendance_topic = f"{MQTT_BASE_TOPIC}/attendances"
        self.attendance_status_topic = f"{self.attendance_topic}/status"

        self.mqtt_client.subscribe(self.progress_internals_topic)
        self.mqtt_client.subscribe(self.progress_topic)
        self.mqtt_client.subscribe(self.stat_topic)
        self.mqtt_client.subscribe(self.stat_itnernal_topic)
        self.mqtt_client.subscribe(self.attendance_topic)
        self.mqtt_client.subscribe(self.attendance_status_topic)

        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self._logger.debug("Component initialization finished")

        self.db = Database()

        self.code = code

        self.attendance = {}
        self.groups = {}

    def register_attendance(self, name: str, group: str, code: str):
        """
        Register attendance for a student
        """
        if code != self.code:
            self._logger.error("Wrong code")
            self.mqtt_client.publish(
                self.attendance_status_topic,
                json.dumps(
                    {
                        "type": "status",
                        "data": {
                            "status": "error",
                            "message": "Wrong code",
                            "name": name,
                        },
                    }
                ),
            )

        self.attendance[name] = True

        if not group in self.groups:
            self.groups[group] = {"members": [name]}
            self.setup_group(group)

    def setup_group(self, group_name: str):
        """
        Create a group stm
        """
        group = GroupLogic(group_name, 10, self)
        self.groups[group_name] = group
        self.stm_driver.add_machine(group.stm)

    def get_task(self, task_nbr: int):
        """
        Returns the task with the given task number
        """
        return self.db.get_question(task_nbr)

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()


debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter(
    "%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s"
)
ch.setFormatter(formatter)
logger.addHandler(ch)
