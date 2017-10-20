# Ali Kidwai
# July 20, 2017
# Adapted from code written by Rotem Guttman and Joe Vessella

import os
import platform
import random
import time

try:
    import pythoncom
    import win32com.client
except ImportError:
    # All tasks should be importable and then checked on initialization.
    pass

from tasks import task


class Word(task.Task):
    """ Creates a Word document and 'types' text from a source file into it. May require registry edits on guest OS to
    make sure Word does not give warnings. This module will edit and possibly delete existing Word files in the user's
    'Documents' folder if the 'new_doc' parameter is set to False (it is set to True by default). Windows-only.
    """
    def __init__(self, config):
        if not platform.system() == 'Windows':
            raise OSError('This task is only compatible with Windows.')
        self._config = config
        self._converter = {} # Cannot be populated until Word is launched; see self._start_word()
        self._filename_bank = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel', 'india',
                               'juliett', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa', 'quebec', 'romeo',
                               'sierra', 'tango', 'uniform', 'victor', 'whiskey', 'xray', 'yankee', 'zulu']
        self._doc_path = self._get_doc_path()

    def __call__(self):
        """ Launches word and creates/modifies a document as specified in the config dictionary.
        """
        self._word = self._start_word()
        self.change_doc(self._config['new_doc'], self._config['text_source'], random.choice(self._config['file_types']))

    def cleanup(self):
        """ Deletes the file that was created/modified by this instance of Word. Will only perform cleanup if
        self._config['cleanup'] is set to True.
        """
        if self._config['cleanup']:
            try:
                os.remove(os.path.join(self._doc_path, self._filename))
            except Exception: # File has already been deleted or is still in use
                pass

    def stop(self):
        """ This task should be stopped after running once.

        Returns:
            True
        """
        return True

    def status(self):
        """ Called when status is polled for this task.

        Returns:
            str: An arbitrary string giving more detailed, task-specific status for the given task.
        """
        return ''

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        params = {'required': {},
                  'optional': {'text_source': 'str| Name of the file to source text from. Defaults to '
                                           'aliceinwonderland.txt',
                               'file_types': '[str]| A list of strings representing different filetypes to save the '
                                            'document as, e.g. ["docx", "dotm"]. Defaults to ["docx"].',
                               'new_doc': 'bool| Create a new document if True, otherwise modify an existing doc, if '
                                          'there is one. Defaults to True.',
                               'cleanup': 'bool| If True, delete the file created by this task on completion. Defaults'
                                          ' to False.'}}
        return params

    @classmethod
    def validate(cls, config):
        """ Validates the given configuration dictionary. Makes sure that config['text_source'] is a string, but does
        not actually check if it is a valid filename. Also makes sure the each filetype in config['file_types'] is valid

        Args:
            config (dict): The dictionary to validate. See parameters() for required format.

        Raises:
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement

        Returns:
            dict: The dict given as the config argument with missing optional parameters added with default values.
        """
        if 'text_source' not in config or not config['text_source']:
            config['text_source'] = 'aliceinwonderland.txt'
        elif not isinstance(config['text_source'], str):
            raise ValueError('text_source: {} Must be a string'.format(str(config['text_source'])))

        if 'file_types' not in config:
            config['file_types'] = ['docx']
        elif not isinstance(config['file_types'], list):
            raise ValueError('file_types: {} Must be a list of strings'.format(str(config['file_types'])))
        if not config['file_types']:
            raise ValueError('file_types: {} Must be non-empty'.format(str(config['file_types'])))
        for filetype in config['file_types']:
            if not isinstance(filetype, str):
                raise ValueError('file_types: {} Must be a list of strings'.format(str(config['file_types'])))
            if filetype not in {'docx', 'docm', 'doc', 'dotx', 'dotm', 'dot', 'rtf', 'txt', 'xml'}:
                raise ValueError('file_types: {} Contains invalid filetype '.format(str(config['file_types'])) +
                                 filetype)

        if 'new_doc' not in config:
            config['new_doc'] = True
        if not isinstance(config['new_doc'], bool):
            raise ValueError('new_doc: {} Must be a bool'.format(str(config['new_doc'])))

        if 'cleanup' not in config:
            config['cleanup'] = False
        if not isinstance(config['cleanup'], bool):
            raise ValueError('cleanup: {} Must be a bool'.format(str(config['cleanup'])))

        return config

    @staticmethod
    def _simulate_typing(doc, text):
        """ Writes text into the document with extra delays to simulate a person typing on a keyboard.

        Args:
            doc (Document): The Document to write text into.
            text (str): The text to write into the document.
        """
        # While normal Python convention would suggest iterating through the new string and appending letters to do this
        # simulation, Word seems to insert \r characters when doing it that way.
        old_text = doc.Range().Text
        for i in range(len(text)):
            # Update letters one at a time using a slice of the new text concatenated with the original text.
            doc.Range().Text = old_text + text[0:i]
            time.sleep(0.02) # A reasonable interval between keystrokes.
        doc.Range().Text = doc.Range().Text + '\n'

    @staticmethod
    def _get_text(text_source, line_count=5):
        """ Get a random concatenation of lines from the specified file.

        Args:
            text_source (str): Properly-escaped path to the text source.
            line_count (int): Number of lines to fetch.

        Returns:
            str: A concatenation of the lines pulled from the file.
        """
        try:
            with open(text_source) as f:
                lines = f.readlines()
        except IOError:
            lines = ['Text source invalid!']
        text_list = [random.choice(lines) for i in range(line_count)]
        return ' '.join(text_list)

    def _start_word(self):
        """ Launch Word through the COM system. Also populates the self._converter dictionary.

        Returns:
            Word.Application connection: Uses the MSDN specification for its API:
                https://msdn.microsoft.com/en-us/library/office/ff841711(v=office.14).aspx
        """
        pythoncom.CoInitialize()
        word = win32com.client.gencache.EnsureDispatch('Word.Application')
        word.Visible = True
        word.DisplayAlerts = win32com.client.constants.wdAlertsNone
        self._converter = {'docx': win32com.client.constants.wdFormatXMLDocument,
                           'docm': win32com.client.constants.wdFormatXMLDocumentMacroEnabled,
                           'doc': win32com.client.constants.wdFormatDocument,
                           'dotx': win32com.client.constants.wdFormatXMLTemplate,
                           'dotm': win32com.client.constants.wdFormatXMLTemplateMacroEnabled,
                           'dot': win32com.client.constants.wdFormatTemplate,
                           'rtf': win32com.client.constants.wdFormatRTF,
                           'txt': win32com.client.constants.wdFormatText,
                           'xml': win32com.client.constants.wdFormatXML}
        return word

    @staticmethod
    def _get_doc_path():
        """ Get the path to the default Documents folder depending on which Windows version is used.

        Returns:
            str: A path to the logged-in user's Documents (Win Vista onward) or My Documents directory (otherwise).
        """
        # Windows Vista, 7, or later.
        doc_path = os.path.expanduser('~\\Documents\\')
        if not os.path.exists(doc_path):
            # Windows XP or earlier.
            doc_path = os.path.expanduser('~\\My Documents\\')
            assert os.path.exists(doc_path)
        return doc_path

    def change_doc(self, new_doc, text_source, filetype):
        """ Simulate modifying a Word document. If self._config['new_doc'] is False, opens and modifies an existing
        document, if there is one. Otherwise, creates a new file and modifies it.

        Args:
            new_doc (bool): Whether to create a new document (True) or use an existing one (False).
            text_source (str): Path to a file to source text from.
            file_type (str): One of the Word-compatible file extensions.
        """
        # Search for files with the same extension as specified, but filter temporary backup versions
        file_list = os.listdir(self._doc_path)
        doc_list = [f for f in file_list if f[-len(filetype):] == filetype and f[0] != '~']

        if new_doc or not doc_list:
            doc = self._word.Documents.Add()
            # Generate a unique filename for the document
            filename = random.choice(self._filename_bank) + str(random.randint(0, 100))
            # If filename is already taken, keep generating names until we get a unique one
            while filename in doc_list:
                filename = random.choice(self._filename_bank) + str(random.randint(0, 100))
            # Only allow removal if the doc was new.
            self._filename = filename
        else:
            filename = random.choice(doc_list)
            doc = self._word.Documents.Open(os.path.join(self._doc_path, filename))

        time.sleep(1) # Wait for the document to open

        text = self._get_text(text_source)
        self._simulate_typing(doc, text)

        if new_doc or not doc_list:
            doc.SaveAs2(FileName=os.path.join(self._doc_path, filename), FileFormat=self._converter[filetype])
        else:
            doc.Save()
        doc.Close()
        self._word.Quit()
