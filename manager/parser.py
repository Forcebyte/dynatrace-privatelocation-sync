import os
import logging
import sys
import yaml

# Fetch StreamHandler from root

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

def is_local():
    # Small function to determine if we're running locally
    if os.environ.get('local'):
        return True
    else:
        return False

class LocationArguments():
    """ Primary Location Argument Definitions

    Parses all YAML files within a specific directory, along with local arguments, and returns a classful definition of all arguments

    """
    def __init__(self):
        self.is_local = is_local()
        self.__parse_dir_arguments()
        self.__parse_meta_config()
        self.dynatrace_credentials = {
            'token': os.environ.get('dynatracetoken', '')
        }
        self.dyantrace_tenant = os.environ.get('dynatracetenant', 'replaceme')

        # Warn about any missing vars
        requiredVars = ['dynatracetoken', 'dynatracetenant']
        for var in requiredVars:
            if os.environ.get(var) is None:
                logger.warning(f"Environment variable {var} appears to be missing - attempting to use default value")

    def __parse_dir_arguments(self):
        # Static DIR arguments, determines the location that we parse YAML files upon
        self.metapath = './locations'

    def __parse_meta_config(self):
        """
        __parse_meta_config - Generates a large 'meta' dict in response to parsing each of the metadata files

        """
        metadata_files = []
        try:
            for dirName, subdirList, fileList in os.walk(self.metapath):
                for file in fileList:
                    if file.endswith('.yaml'):
                        logger.info(f"Found MetaData File: {file}")
                        metadata_files.append(file)
        except Exception as err:
            if self.is_local:
                logger.error(err)
                raise ValueError(f"Unable to parse directory {self.metapath} - raising error")
            else:
                logger.error(err)
                logger.warning(f"Unable to parse {self.metapath} - skipping...")

        # Now that we have a generic listing of each metadata path, parse each of those files into a single config dict
        config = []
        for file in metadata_files:
            with open(f"{self.metapath}/{file}", 'r') as stream:
                try:
                    localconfig = yaml.safe_load(stream)
                    if localconfig['metadata']['Active']:
                        config.extend(localconfig.pop('syntheticData'))
                    else:
                        logger.info(f"Locations file {file} is not marked as 'active' under metadata -> Active, ignoring")
                except yaml.YAMLError as err:
                    logger.error(err)
                    logger.warning(f"Unable to parse {self.metapath}/{file} - skipping...")
        self.metadict = config