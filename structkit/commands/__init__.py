import logging
from structkit.completers import log_level_completer


# Base command class
class Command:
    def __init__(self, parser):
      self.parser = parser
      self.logger = logging.getLogger(__name__)
      self.add_common_arguments()

    def add_common_arguments(self):
      self.parser.add_argument('-l', '--log', type=str, default='INFO', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)').completer = log_level_completer
      self.parser.add_argument('-c', '--config-file', type=str, help='Path to a configuration file')
      self.parser.add_argument('-i', '--log-file', type=str, help='Path to a log file')

    def execute(self, args):
      raise NotImplementedError("Subclasses should implement this!")
