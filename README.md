# EPA.Envirofacts package

This Python Package is for getting information from the EPA's Envirofacts api.

[Envirofacts api documentation](https://www.epa.gov/enviro/envirofacts-data-service-api)

portions of the api implemented:
* [SDWIS (Safe Drinking Water Information System)](https://www.epa.gov/enviro/sdwis-model)
* * Water Systems
* * Violations

The included script gets all water safety violations for a state and outputs them into a file in csv format

the script can take the following parameters:
* -q, --quite - disables console output
* -s, -state - state to get violations for (2 letter abbreviation. ie . de, pa, ca, tx, etc.) Default: DE
*  -m, --max - maximum rows to return

### Prerequisites

[Python 3.6.2+](https://www.python.org/downloads/release/python-362/)

[Requests](http://docs.python-requests.org/en/master/)

```bash
pip install requests
```

### Installing

From Source

```bash
# Clone this repository
git clone https://github.com/chaosnhatred/epa-envirofacts-api.git

# Go into the repository
cd epa-envirofacts-api

# Run the script to verify functionality (only gets all rows for the state of Delaware [Delaware is set as the default state])
python get_sdwis_data.py

# You should see the following output
====== Water safety violations for the state: Delaware ======
---Getting water system count (step 1/8):  [done] [00:00:02.51]
---Getting 1289 water systems (step 2/8):  [done] [00:00:21.68]
---Getting violation count (step 3/8):  [done] [00:00:05.78]
---Getting 2367 violations (step 4/8):  |####################| 100.0% (1289/1289) [done] [01:15:40.93]
---Parsing water system results (step 5/8):  |####################| 100.0% (1289/1289) [done] [00:00:00.50]
---Parsing violation results (step 6/8):  |####################| 100.0% (3598/3598) [done] [00:00:01.25]
---Saving water system results to watersystems.csv(step 7/8):  [done] [00:00:00.25]
---Saving violation results to violations.csv (step 7/8):  [done] [00:00:00.54]
Script completed in: 01:16:13.45
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/chaosnhatred/epa-envirofacts-api/tags). 

## Authors

* **Bryan Longacre** - *Initial work* - [Chaosnhatred](https://github.com/chaosnhatred)

See also the list of [contributors](https://github.com/chaosnhatred/epa-envirofacts-api/contributors) who participated in this project.

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)