from EPA.Utilities import *

__api_url = 'https://iaspub.epa.gov/enviro/efservice'

__state_abbr = 'DE'

@public
def get_api_url():
    return __api_url

@public
def set_state(state):
    if not state:
        print('state cannot be empty or null')
        return

    __state_abbr = state

@public
def get_state():
    return __state_abbr