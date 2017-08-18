This Python Package is for getting information from the EPA's envirofacts api.

portion of the api implemented:
	-SDWIS
	--Violations

[Envirofacts api documentation](https://www.epa.gov/enviro/envirofacts-data-service-api)

The included script gets all water safety violations for a state and outputs them into a file in csv format

the script can take the following parameters:
-q, --quite - disables console output
-f, --filename - filename to output results (default: output.csv)
-s, -state - state to get violations for (default: DE)