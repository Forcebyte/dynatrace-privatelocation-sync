import requests
import logging
import sys
from collections import defaultdict

# Substantiate logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

class locationsManager():
    """
    locationsManager - Primary handler for Deployment of Locations API

    """

    def __init__(self, args):
        self.dynatrace_tenant = args.dyantrace_tenant
        # NOTE: These are based on Dynatrace Cloud, change these URL formats if you are using Managed SaaS
        self.dynatraceURL = {
            'node': f"https://{self.dynatrace_tenant}.live.dynatrace.com/api/v1/synthetic/nodes",
            'location': f"https://{self.dynatrace_tenant}.live.dynatrace.com/api/v1/synthetic/nodes",
            'default': f"https://{self.dynatrace_tenant}.live.dynatrace.com"
        }
        self.dynatracecredentals = args.dynatracecredentials
        self.metadict = args.metadict

    def parse_metadata(self):
        """
        parse_metadata - this function fetches each Private Synthetic Location + Node and returns a list of nodes to update
        """
        nodes_to_update = defaultdict(list)
        node_information = self.__fetch_node_block()
        for node in node_information['nodes']:
            logger.info(f"Finding IpBlock for Synthetic Location to {node['hostname']}")
            for ip_block in node['ips']:
                item = self.__parse_ipblock(ip_block)
                if item:
                    if item.get('syntheticLocation'):
                        logger.info(f"Node IP {ip_block} is in block itme {item['prefixName']}")
                        nodes_to_update[item['syntheticLocation']].append(node['entityId'])
            # Once all the nodes are identified, return the list and patch all synthetic locatiosn
        self.__patch_synthetic_location(nodes_to_update)

    def __parse_ipblock(self, ip_block):
        for block in self.metadict:
            # if we notice the block is part of the IP
            if '.'.join(ip_block.split('.'[0:2])) in block.keys():
                logger.debug(f"IpBlock is in {block['prefixName']} - Adding synthetic agent list to update")
                return(block)
            else:
                logger.debug(f"IpBlock is not in {block['prefixName']} - continuing")

    def __fetch_node_block(self):
        # Static function that fetches all synthetic nodes, and returns them in dict format
        item = requests.get(
            url=self.dynatraceURL['node'],
            headers={ 'Authorization': f"Api-Token {self.dynatracecredentals['token']}", 'Content-Type': 'application/json'}
        )
        return item.json()

    def __fetch_synthetic_location(self, location_name):
        item = requests.get(
            url=f"{self.dynatraceURL['location']}/{location_name}",
            headers={ 'Authorization': f"Api-Token {self.dynatracecredentals['token']}", 'Content-Type': 'application/json'}
        )
        return item.json()

    def __patch_synthetic_location(self, nodes_to_update):
        # adds a PUT to synthetic nodes, returns them in a dict format
        for synthetic_location, nodes in nodes_to_update.items():
            # first, fetch the existing synthetic location ID to get the existing metadata to include in PUT request
            synthetic_location_data = self.__fetch_synthetic_location(synthetic_location)
            logger.info(f"Updating {synthetic_location} with nodes {nodes}")
            synthetic_location_data['nodes'] = nodes
            item = requests.put(
                url=f"{self.dynatraceURL['location']}/{synthetic_location}",
                headers={ 'Authorization': f"Api-Token {self.dynatracecredentals['token']}", "Content-Type": "application/json"},
                json=synthetic_location_data
            )
            item.raise_for_status()