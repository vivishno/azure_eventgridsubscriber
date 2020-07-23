import os
import json
import time
from json import JSONDecodeError
from utils import AMLConfigurationException, ActionDeploymentError, CredentialsVerificationError, ResourceManagementError, mask_parameter, required_parameters_provided, get_events_list
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from azure.mgmt.resource.resources.models import Deployment
from azure.mgmt.resource.resources.models import DeploymentProperties
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.eventgrid.models import Topic, EventSubscriptionFilter, EventSubscription, WebHookEventSubscriptionDestination

def main():
    # # Loading input values
    # print("::debug::Loading input values")
    azure_credentials = os.environ.get("INPUT_AZURE_CREDENTIALS", default='{}')
    resource_group = os.environ.get("INPUT_RESOURCE_GROUP", default="")
    pattoken = os.environ.get("INPUT_PATTOKEN",default="")
    provider_type = os.environ.get("INPUT_PROVIDER_TYPE",default="")
    events_to_subscribe= os.environ.get("INPUT_EVENTS_TO_SUBSCRIBE",default="")
    
    try:
        azure_credentials = json.loads(azure_credentials)
    except JSONDecodeError:
        print("::error::Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS")
        raise AMLConfigurationException(f"Incorrect or poorly formed output from azure credentials saved in AZURE_CREDENTIALS secret. See setup in https://github.com/Azure/aml-workspace/blob/master/README.md")

    if not resource_group:
        raise AMLConfigurationException(f"A resource group must be provided")
    
    # Checking provided parameters
    print("::debug::Checking provided parameters")
    required_parameters_provided(
        parameters=azure_credentials,
        keys=["tenantId", "clientId", "clientSecret"],
        message="Required parameter(s) not found in your azure credentials saved in AZURE_CREDENTIALS secret for logging in to the workspace. Please provide a value for the following key(s): "
    )

    # # Loading parameters file
    # print("::debug::Loading parameters file")

    template_file_file_path = os.path.join("/code", "func_deploy.json")

    # Mask values
    print("::debug::Masking parameters")
    mask_parameter(parameter=azure_credentials.get("tenantId", ""))
    mask_parameter(parameter=azure_credentials.get("clientId", ""))
    mask_parameter(parameter=azure_credentials.get("clientSecret", ""))
    mask_parameter(parameter=azure_credentials.get("subscriptionId", ""))
    
    # Login User on CLI
    tenant_id=azure_credentials.get("tenantId", "")
    service_principal_id=azure_credentials.get("clientId", "")
    service_principal_password=azure_credentials.get("clientSecret", "")
    subscriptionId=azure_credentials.get("subscriptionId", "") 
    
    credentials=None
    try:
        credentials = ServicePrincipalCredentials(
             client_id=service_principal_id,
             secret=service_principal_password,
             tenant=tenant_id
          )
    except Exception as ex:
       raise CredentialsVerificationError(ex)
    
    ####################### Authentication Done ###################################   

    # repository name
    repository_name = os.environ.get("GITHUB_REPOSITORY", "azureeventgridsample")
    functionAppName=repository_name.replace("/","") # create a unique function-AppName
    functionAppName=functionAppName.replace("_","")
    functionFolder='fappdeploy'
    functionGitHubURL="https://github.com/vivishno/function_app.git"
    functionGitHubBranch="master"
    functionName = "generic_triggers"
    patToken = pattoken
    parameters = {
            'functionAppName': functionAppName,
            'functionFolder': functionFolder,
            'functionGitHubURL': functionGitHubURL,
            'functionGitHubBranch': functionGitHubBranch,
            'patToken': patToken,
            'ownerName': functionAppName
        }

    parameters = {k: {'value': v} for k, v in parameters.items()}

    client=None
    try:    
        client = ResourceManagementClient(credentials, subscriptionId)
    except Exception as ex:
        raise ResourceManagementError(ex)  
        
    template=None
    with open(template_file_file_path, 'r') as template_file_fd:
        template = json.load(template_file_fd)

    deployment_properties = {
        'properties':{
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }
     }
    
    try:
        validate=client.deployments.validate(resource_group,"azure-sample",deployment_properties)
        validate.wait()
        
    except Exception as ex:
        raise ActionDeploymentError(ex)    
    try:
        deployment_async_operation = client.deployments.create_or_update(
                resource_group,
                'azure-sample',
                deployment_properties
            )
        deployment_async_operation.wait()
    except Exception as ex:
        raise ActionDeploymentError(ex)
    
    deploymemnt_result = deployment_async_operation.result();

    # parameters
    code = deploymemnt_result.properties.outputs['hostKey']['value']
    functionAppName = deploymemnt_result.properties.outputs['functionAppName']['value']

    function_url = "https://{}.azurewebsites.net/api/{}?code={}&repoName={}".format(functionAppName, functionName,code,repository_name)
    resource_id = "/subscriptions/{}/resourceGroups/{}/providers/{}".format(subscriptionId,resource_group,provider_type)

    event_grid_client = EventGridManagementClient(credentials, subscriptionId)
    event_subscription_name = 'EventSubscription1'

    destination = WebHookEventSubscriptionDestination(
        endpoint_url = function_url
    )
    
    included_events=get_events_list(events_to_subscribe)
    filter = EventSubscriptionFilter(
        # By default, "All" event types are included
        included_event_types = included_events,
        is_subject_case_sensitive=False,
        subject_begins_with='',
        subject_ends_with=''
    )

    event_subscription_info = EventSubscription(
        destination=destination, filter=filter)

    event_subscription_async_poller = event_grid_client.event_subscriptions.create_or_update(
        resource_id,
        event_subscription_name,
        event_subscription_info,
    )

    event_subscription = event_subscription_async_poller.result()  # type: EventSubscription
    print(f"::set-output name=destination_url::{event_subscription.destination.endpoint_base_url}")


if __name__ == "__main__":
    main()
