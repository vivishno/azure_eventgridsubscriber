import os
import sys
import importlib
import json
from json import JSONDecodeError

class ActionDeploymentError(Exception):
    pass

class AMLConfigurationException(Exception):
    pass

class ResourceManagementError(Exception):
    pass

class CredentialsVerificationError(Exception):
    pass

class TemplateParameterException(Exception):
    pass

def required_parameters_provided(parameters, keys, message="Required parameter not found in your parameters file. Please provide a value for the following key(s): "):
    missing_keys = []
    for key in keys:
        if key not in parameters:
            err_msg = f"{message} {key}"
            print(f"::error::{err_msg}")
            missing_keys.append(key)
    if len(missing_keys) > 0:
        raise AMLConfigurationException(f"{message} {missing_keys}")

def mask_parameter(parameter):
    print(f"::add-mask::{parameter}")
    
def get_events_list(events_to_subscribe):
    events_to_subscribe=events_to_subscribe.split('\n')
    events_list=[]
    for i in events_to_subscribe:
        if len(i)>0:
            if i.lower()=='all':
                return None
            events_list.append(i)
    if len(events_list)==0:
        return None
    return events_list;        

