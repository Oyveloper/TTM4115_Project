import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json

MQTT_BROKER = "mqtt20.iik.ntnu.no"
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = "ttm4115/team3/command"
MQTT_TOPIC_OUTPUT = "ttm4115/team3/answer"


class TimerLogic:
    """
    State Machine for a named timer.

    This is the support object for a state machine that models a single timer.
    """

    def __init__(self, name, duration, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.duration = duration
        self.component = component

        t0 = {"source": "initial", "target": "active", "effect": "started"}
        t1 = {
            "source": "active",
            "target": "completed",
            "trigger": "t",
            "effect": "timer_completed",
        }
        t2 = {
            "source": "active",
            "trigger": "report",
            "target": "active",
            "effect": "report_status",
        }
        t3 = {
            "source": "active",
            "trigger": "cancel",
            "target": "canceled",
            "effect": "cancel",
        }
        self.stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t3], obj=self)

    def started(self):
        self.stm.start_timer("t", self.duration * 1000)
        self._logger.debug(
            "New timer {} with duration {} started.".format(self.name, self.duration)
        )
        message = f"New timer {self.name} with duration {self.duration} started."
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, message)

    def timer_completed(self):
        message = "Timer {} expired.".format(self.name)
        self._logger.debug(message)
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, message)
        self.stm.terminate()

    def report_status(self):
        self._logger.debug("Checking timer status.".format(self.name))
        time = int(self.stm.get_timer("t") / 1000)
        message = "Timer {} has about {} seconds left".format(self.name, time)
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, message)

    def cancel(self):
        self._logger.debug("Timer {} canceled.".format(self.name))
        message = "Timer {} is canceled".format(self.name)
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, message)
        self.stm.terminate()


class TimerManagerComponent:
    """
    The component to manage named timers in a voice assistant.

    This component connects to an MQTT broker and listens to commands.
    To interact with the component, do the following:

    * Connect to the same broker as the component. You find the broker address
    in the value of the variable `MQTT_BROKER`.
    * Subscribe to the topic in variable `MQTT_TOPIC_OUTPUT`. On this topic, the
    component sends its answers.
    * Send the messages listed below to the topic in variable `MQTT_TOPIC_INPUT`.

        {"command": "new_timer", "name": "spaghetti", "duration":50}

        {"command": "status_all_timers"}

        {"command": "status_single_timer", "name": "spaghetti"}

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

        * create a new state machine instance to handle the incoming messages,
        * route the message to an existing state machine session,
        * handle the message right here,
        * throw the message away.

        """
        self._logger.debug("Incoming message to topic {}".format(msg.topic))

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error(
                "Message sent to topic {} had no valid JSON. Message ignored. {}".format(
                    msg.topic, err
                )
            )
            return
        command = payload.get("command")
        self._logger.debug("Command in message is {}".format(command))
        if command == "new_timer":
            try:
                print(type(self))
                timer_name = payload.get("name")
                duration = int(payload.get("duration"))
                # create a new instance of the timer logic state machine
                timer = TimerLogic(timer_name, duration, self)
                timer_stm = timer.stm
                # add the machine to the driver to start it
                self.stm_driver.add_machine(timer_stm)
            except Exception as err:
                self._logger.error("Invalid arguments to command. {}".format(err))
        elif command == "status_all_timers":
            s = "List of all timers"
            # We loop over all state machines in the driver. All of them are a
            # timer that we should include in our list that we present to the
            # user.
            for name, stm in self.stm_driver._stms_by_id.items():
                self.status_timer(name)
            self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, s)
        elif command == "status_single_timer":
            # report the status of a single timer
            self.status_timer(payload.get("name"))
        elif command == "cancel_timer":
            # cancel a timer
            try:
                timer_name = payload.get("name")
                # send a signal to the corresponding timer state machine to
                # trigger cancelling the timer.
                self.stm_driver.send("cancel", timer_name)
            except Exception as err:
                self._logger.error("Invalid arguments to command. {}".format(err))
        else:
            self._logger.error("Unknown command {}. Message ignored.".format(command))

    def status_timer(self, timer_name):
        # report the status of a single timer
        try:
            print(type(self))
            # send a signal to the corresponding timer state machine to
            # trigger reporting the status.
            self.stm_driver.send("report", timer_name)
        except Exception as err:
            self._logger.error("Invalid arguments to command. {}".format(err))

    def __init__(self):
        """
        Start the component.

        ## Start of MQTT
        We subscribe to the topic(s) the component listens to.
        The client is available as variable `self.client` so that subscriptions
        may also be changed over time if necessary.

        The MQTT client reconnects in case of failures.

        ## State Machine driver
        We create a single state machine driver for STMPY. This should fit
        for most components. The driver is available from the variable
        `self.driver`. You can use it to send signals into specific state
        machines, for instance.

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
        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self._logger.debug("Component initialization finished")

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()


# logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.
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

t = TimerManagerComponent()
