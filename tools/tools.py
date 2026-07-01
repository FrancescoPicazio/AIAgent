from tools.categories.general.bookshelf import search_docs
from tools.categories.general.remember import remember_note, recall_notes
from tools.categories.general.datetime_tool import get_current_datetime
from tools.categories.general.calculator import calculator
from tools.categories.general.introspection import list_available_tools
from tools.categories.general.text_to_speech import speak_text
from tools.categories.general.speech_to_text import transcribe_audio_file, listen_from_microphone
from tools.categories.trading.trading import trading, wallet


class ToolRegistry:

    def __init__(self):
        self.tools = {}
        self._register_basic_tools()

    def register(self, tool):
        self.tools[tool.name] = tool

    def remove(self, name):
        if name in self.tools:
            del self.tools[name]

    def get_tools(self):
        return list(self.tools.values())

    def _register_basic_tools(self):
        for t in (
            search_docs,
            remember_note,
            recall_notes,
            list_available_tools,
            get_current_datetime,
            calculator,
            speak_text,
            transcribe_audio_file,
            listen_from_microphone
        ):
            self.register(t)

