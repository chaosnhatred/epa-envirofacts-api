# -*- coding: utf-8 -*-

import re
from EPA.Utilities import *

__api_url = 'https://iaspub.epa.gov/enviro/efservice'

state = 'DE'

result_format = 'json'

@public
def get_api_url():
    return __api_url