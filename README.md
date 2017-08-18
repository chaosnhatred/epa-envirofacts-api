# EPA.Envirofacts package

This Python Package is for getting information from the EPA's Envirofacts api.

[Envirofacts api documentation](https://www.epa.gov/enviro/envirofacts-data-service-api)
portions of the api implemented:
* SDWIS
* * Violations

The included script gets all water safety violations for a state and outputs them into a file in csv format

the script can take the following parameters:
* -q, --quite - disables console output
* -f, --filename - filename to output results (default: output.csv)
* -s, -state - state to get violations for (default: DE)
*  -m, --max - maximum rows to return

### Prerequisites

[Python 3.6.2+](https://www.python.org/downloads/release/python-362/)
[Requests](http://docs.python-requests.org/en/master/)

```bash
$ pip install requests
```

### Installing

```bash
# Clone this repository
$ git clone https://github.com/chaosnhatred/epa-envirofacts-api.git

# Go into the repository
$ cd epa-envirofacts-api

# Run the script to verify functionality
$ python get_sdwis_data.py
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