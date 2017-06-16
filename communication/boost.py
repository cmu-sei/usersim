""" Handle communication over a Boost message queue in order to communicate using the XGA.

May not successfully import if boostmq could not be imported.
"""
import base64
from io import BytesIO
import threading
import time
import traceback
import xml.etree.ElementTree as ET

import api
import boostmq
import config


class BoostCommunication(object):
    def __init__(self, feedback_queue):
        self._feedback_queue = feedback_queue
        self._config_mq = boostmq.MQ('config', 10, 50000)
        self._feedback_mq = boostmq.MQ('feedback', 10000, 10000)

        thread = threading.Thread(target=self._handle_communication)
        thread.daemon = True
        thread.start()

    def _receive(self):
        """ Check if there are any messages available. If an invalid message is received, sends a feedback message
        indicating the error and the portion of the message that was received.

        Returns:
            None: If no (valid) messages are available.
            list of dicts: See config.string_to_python
        """
        message = str()
        last_error = str()

        while True:
            # Need to stitch messages together if a config is too large for the message queue.
            more = self._config_mq.receivequeue_noblock()

            if message and not more:
                # TODO: Make sure 0 is an appropriate task ID for non-task feedback.
                self._feedback_queue.put((0, last_error + '\n\n' + message))
            if not more:
                # If there's nothing else, go to sleep for a while.
                break

            message += more

            try:
                new_config = config.string_to_python(message)
            except ValueError:
                last_error = traceback.format_exc()
                # Message may need to be stitched together. Give plenty of time for the next part to be
                # added to the shared message queue.
                time.sleep(.5)
                continue
            else:
                return new_config

    def _send(self):
        """ If any feedback messages are queued, construct feedback messages in the format the XGA is expecting and
        send them.
        """
        while not self._feedback_queue.empty():
            task_id, exception = self._feedback_queue.get()

            if task_id > 0:
                task_status = api.status_task(task_id)
            else:
                task_status = {'type': 'core', 'state': api.States.UNKNOWN, 'status': str()}

            fm = FeedbackMessage(task_id, task_type=task_status['type'], status=task_status['state'],
                                 emsblob=task_status['status'], exception=exception)
            self._feedback_mq.sendqueue(str(fm), 0)

    def _handle_communication(self):
        """ Periodically check if there are any new config files available or if there is any feedback that should be
        forwarded.
        """
        new_config = self._receive()
        if new_config:
            for task in new_config:
                try:
                    api.new_task(task)
                except KeyError as e:
                    task_status = {'id': 0, 'type': 'core', 'state': api.States.UNKNOWN, 'status': str()}
                    self._feedback_queue.put((task_status, 'task ' + task['type'] + 'missing required key %s '
                        'from its configuration' % e.message))
                except ValueError as e:
                    task_status = {'id': 0, 'type': 'core', 'state': api.States.UNKNOWN, 'status': str()}
                    self._feedback_queue.put((task_status, 'task ' + task['type'] + 'has at least one bad value for a '
                        'config option:\n%s' % e.message))

        self._send()

        # So the CPU isn't running at 100%.
        time.sleep(5)

class FeedbackMessage(object):
    """Feedback message constructor class.  All inputs should be strings except for the Task ID, which is allowed to be
    an int.

    Keyword arguments are generally preferred for object construction, as not all are likely to be used for every
    feedback message.
    It is possible to create custom parameter or result tags with the respective method calls and those tags will be in
    order of assignment.

    Note that setting an exception will default to encoding the input as base64.  See the set_exception method for
    details.
    """
    def __init__(self, tid, task_type = "", source = "", target = "", sbase = "", rbase = "", status = "",
                 exception = "", emsblob = ""):
        self.set_task_type(task_type)

        self.source = ET.Element("Source")
        self.set_source(source)

        self.target = ET.Element("Target")
        self.set_target(target)

        self.tid = ET.Element("TID")
        self.set_tid(tid)

        self.sbase = ET.Element("SBase")
        self.set_sbase(sbase)

        self.rbase = ET.Element("RBase")
        self.set_rbase(rbase)

        self.status = ET.Element("Status")
        self.set_status(status)

        self.exception = ET.Element("Exception")
        self.set_exception(exception)

        self.emsblob = emsblob

        self.custom_param_list = []
        self.custom_result_list = []

    def set_task_type(self, task_type = ""):
        self.task_type = task_type

    def set_source(self, source = ""):
        self.source.text = source

    def set_target(self, target = ""):
        self.target.text = target

    def set_tid(self, tid):
        self.tid.text = repr(tid)

    def set_sbase(self, sbase = ""):
        self.sbase.text = sbase

    def set_rbase(self, rbase = ""):
        self.rbase.text = rbase

    def set_status(self, status = ""):
        self.status.text = status

    def set_exception(self, exception = "", encode = True):
        if encode:
            self.exception.text = base64.b64encode(exception)
        else:
            self.exception.text = exception

    def set_emsblob(self, emsblob = ""):
        self.emsblob = emsblob

    def set_custom_param_tag(self, tag_name, tag_text):
        tag_el = ET.Element(tag_name)
        tag_el.text = tag_text
        self.custom_param_list.append(tag_el)

    def set_custom_result_tag(self, tag_name, tag_text):
        tag_el = ET.Element(tag_name)
        tag_el.text = tag_text
        self.custom_result_list.append(tag_el)

    def get_feedback_str(self):
        xml_tree = self._construct_xml_tree()

        #tostring doesn't have xml_declaration as of writing, using workaround
        f = BytesIO()
        # 'html' for method in order to get open/close tags for empty elements, instead of self-closing.
        xml_tree.write(f, encoding="utf-8", xml_declaration=True, method='html')
        return f.getvalue()

    def __str__(self):
        return self.get_feedback_str()

    def _construct_xml_tree(self):
        root = ET.Element("Message")
        ET.SubElement(root, "Type").text = "Feedback"
        ET.SubElement(root, "Sender")
        ET.SubElement(root, "Recipient").text = "ref_system"
        ET.SubElement(root, "Task").text = self.task_type
        params = ET.SubElement(root, "Params")
        params.append(self.source)
        params.append(self.target)
        params.append(self.tid)
        params.append(self.sbase)
        params.append(self.rbase)
        params.extend(self.custom_param_list)
        result = ET.SubElement(root, "Result")
        result.append(self.status)
        if self.exception.text:
            result.append(self.exception)
        result.extend(self.custom_result_list)
        dispatcher = ET.SubElement(root, "Dispatcher")
        ET.SubElement(dispatcher, "TestedBase")
        ET.SubElement(dispatcher, "ReportingBase")
        ET.SubElement(dispatcher, "ReportingUser")
        ET.SubElement(dispatcher, "ReportingVM")

        return ET.ElementTree(root)
