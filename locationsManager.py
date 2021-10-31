import logging

# Initialize Logger
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
logger.propagate = False

from manager import parser, dynatrace_utils

if __name__ == '__main__':
    args = parser.LocationArguments()
    location_management = dynatrace_utils.locationsManager(args)
    location_management.parse_metadata()