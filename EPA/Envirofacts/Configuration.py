# -*- coding: utf-8 -*-

import sys, json, os.path
from ..__Utilities.__utilities import RestApiResultType

class __Configuration(object):   
    __api_url = 'https://iaspub.epa.gov/enviro/efservice'

    __state = 'DE'

    # If you are planning on getting over 900+ results, please use CSV or XML return formats.
    # There is an issue with the Envirofacts API, where after 1000 results if returns an empty
    # array if using the JSON formatting.
    __result_format = RestApiResultType.CSV

    @property
    def api_url(self):
        """Envirofacts API Url"""
        return self.__api_url

    @property
    def state(self):
        """The state which to run the Envirofacts API against. Must be state's two letter abbreviation (ie. DE, PA, CO, TX)"""
        return self.__state

    @state.setter
    def state(self, value):
        if not value or type(value) is not str:
            raise ValueError('state must not be null and a string')

        if not self.state_hash[value]:
            raise ValueError('state does not exist')

        self.__state = value.upper()
    
    @property
    def state_fullname(self):
        """The states full name"""
        return self.state_hash[self.__state] 

    @property
    def api_result_format(self):
        """ The raw return format of the Envirofacts API.
        If you are planning on getting over 900+ results, please use CSV or XML return formats.
        There is an issue with the Envirofacts API, where after 1000 results it returns an empty
        array if using the JSON formatting."""
        return self.__result_format

    @api_result_format.setter
    def api_result_format(self, value):
        self.__result_format = value

    def __init__(self, **kwargs):
        basepath = os.path.dirname(__file__)
        states_filepath = os.path.abspath(os.path.join(basepath, "..", "__Utilities", "states_hash.json"))
        with open(states_filepath) as states:    
            self.state_hash = json.load(states)

        return super().__init__(**kwargs)

sys.modules[__name__] = __Configuration()