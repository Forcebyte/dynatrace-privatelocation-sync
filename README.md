<h4 align="center">
  <img alt="header pic" src="src/dynatrace_logo.png">
</h4>

# Dynatrace Private Synthetic Locations Sync


At the moment, Dynatrace does not support any sembience of linking a private synthetics agent to a 'location' at runtime - this is a huge problem in a majority of cases (including where you run these sort of agents in a scaled manner, each Private instance you scale out to must be manually registered to a location, which is both annoying and problematic at scale)

this script was made to attempt to combat that, and allows for Private Synthetics Locations to be automatically updated and definedbased on specific metadata that the node reports in the [**Synthetic Node API**](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/synthetic/synthetic-nodes/get-node/) - Today this includes

- IP Block type (E.g. IP Prefix)
- Synthetic Node Name

## Quickstart

By default, the script expects the following
- Environment Variables `dynatracetoken` and `dynatracetenant` are set
- Proper metadata provided in the `locations` folder exists

a easy quickstart would be to define these locally, and run the example script

```bash
export dynatracetoken='mycooltoken'
export dynatracetenant='isa2131'
python3 locationsManager.py
```

## Adding/Removing Definitions

Definitions of a Private Synthetic Location group are managed within the 'locations' folder of this repository - when parsing through this folder the script will
- Fetch all files within the folder
- Dynamically pull 'SyntheticData' configuration from each folder

Definitions can be grouped in whatever way you wish, ideally i'd recommend grouping them based on 'environment' (so eng, nonp, and prod respectively)

```yaml
metadata:
  # Dictates whether we parse over the file
  Active: True
  Name: "Production Location Metadata"
  Type: ipBlock

syntheticData:
  # Address we look for
  - '172.16':
    # Custom prefix name (only used in logging)
    prefixName: 'Private 172 Address space'
    # This is the Synthetic Location ID as it appears in the API
    syntheticLocation: 'SYNTHETIC_LOCATION-AAAA'
```
