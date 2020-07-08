# azure_eventgridsubscriber



# GitHub Action for deploying ARM templates for Azure

## Usage

The AML Configure action deploys your azure resources using [Azure Resource Manager](https://docs.microsoft.com/en-us/azure/azure-resource-manager/) on azure via [ARM Templates](https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/overview).


Get started today with a [free Azure account](https://azure.com/free/open-source)!

This repository contains GitHub Action for deploying ARM templates

## Dependencies on other GitHub Actions
* [Checkout](https://github.com/actions/checkout) Checkout your Git repository content into GitHub Actions agent.



## Use of this GitHub Actions

Using this action user will be able to deploy resources to azure by providing the ARM templates and an ARM templates paramter file.


### Example workflow

```yaml
# Tests Actions to deploy ARM template to Azure
name: arm-template-deploy
on: [push]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
    # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
    - name: Check Out Repository
      id: checkout_repository
      uses: actions/checkout@v2
        
    # Connect or Create the Azure Machine Learning Workspace
    - name: deploy all resources
      id: azure_eventgridsubscriber
      uses: ./
      with:
          azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}
          events_mapfile: "deploy.json"
          resource_group: "ashkuma_functionAppRsGroup"
          pattoken: ${{secrets.PAT_TOKEN}}

```

### Inputs

| Input | Required | Default | Description |
| ----- | -------- | ------- | ----------- |
| azure_credentials | x | - | Output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth`. This should be stored in your secrets |
| events_mapfile | "event_subscriptions.json" | - | We expect a JSON file in the `.cloud/.azure` folder in root of your repository specifying information about the resource to which event has to be subscribed. If you have want to provide these details in a file other than "event_subscriptions.json" you need to provide this input in the action. |
| resource_group |  | x | User needs to specify the azure resource group where the deployment of function app resources needs to be done.| This can be different than the resource group you specify in event file.
| pattoken |  | x | In some cases user can not write the secrets in the parameters file, which might be getting used in the template, we prvide support to enter mapped parameters which will be injected into the parameters during deployment time, so your template will have access to them and you don't need to provide them inside parameters file. |


#### azure_credentials ( Azure Credentials ) 

Azure credentials are required to connect to your Azure Machine Learning Workspace. These may have been created for an action you are already using in your repository, if so, you can skip the steps below.

Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) on your computer or use the Cloud CLI and execute the following command to generate the required credentials:

```sh
# Replace {service-principal-name}, {subscription-id} and {resource-group} with your Azure subscription id and resource group name and any name for your service principle
az ad sp create-for-rbac --name {service-principal-name} \
                         --role contributor \
                         --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
                         --sdk-auth
```

This will generate the following JSON output:

```sh
{
  "clientId": "<GUID>",
  "clientSecret": "<GUID>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>",
  (...)
}
```

Add this JSON output as [a secret](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets#creating-encrypted-secrets) with the name `AZURE_CREDENTIALS` in your GitHub repository.


#### parameters_file (Parameters File)

The action tries to load a JSON file in the `.cloud/.azure` folder in your repository, which specifies details for the model deployment to your Azure Machine Learning Workspace. By default, the action expects a file with the name `events_mapfile.json`. If your JSON file has a different name, you can specify it with this parameter. Note that none of these values are required and, in the absence, default sample file will be used.

A sample file can be found in this repository in the folder `.cloud/.azure`. The parameters file parameters are configurable and can be changed by user accordingly.

| Input | Required | Default | Description |
| ----- | -------- | ------- | ----------- |
| provider_type | x | - | Microsoft.MachineLearningServices/workspaces/infinity  <provider/topic/name> |
| resource_group |  | x |  azure resource group where the resource is|
| events_to_subscribe |  | x | List of the events to subscribe. |

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
