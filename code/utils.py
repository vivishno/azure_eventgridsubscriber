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



def mask_parameter(parameter):
    print(f"::add-mask::{parameter}")
