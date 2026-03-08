# Kubernetes Cluster
As of now this is a single environment cluster intended for PROD use.  
If adding QA or DEV, I recomment using `Kustomize` which is included in the used version of k8s

## Requirements

### Kubernetes
You will need to install k8s, you can follow instructions here: https://kubernetes.io/docs/setup/.   

### Cluster set up
If the cluster does not exist on the Azure account, you will have to create one, following [these instructions](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-portal?tabs=azure-cli).   
**Note**: name your research group `FXTradingGame` and your cluster `FX-Trading-Game-PROD`.    
Follow [these instructions](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?tabs=azure-cli) to install the Azure CLI on your machine.   
Login via `az login --tenant your_directory_here`, you can find the ID of your directory [here](https://portal.azure.com/#settings/directory); if you are using the default directory, you can skip this `--tenant`.   
Finally, link Azure and Kubernetes `az aks get-credentials --resource-group myResourceGroup --name myAKSCluster`   
You can now run k8s commands against the cluster: `kubectl get nodes` should return the system and user nodes you created above.   

#### Authorization
 1. For the pods to be able to pull the image, when the cluster is set up for the first time, you will need to add a service principal:   
    **Note** you might need to replace `db689aeb-843c-41a3-bf4e-54fdcc9a8c33` with the subscription ID you are using in the Azure Account, this is linked within the Cluster overview page.
    **Note** You need to have the `Application administrator` or `Cloud application administrator` role in Azure Active Directory to create a service principal.
    ```
    az ad sp create-for-rbac --name fxTradingGameAuthPrincipal --role Contributor --scopes /subscriptions/db689aeb-843c-41a3-bf4e-54fdcc9a8c33/resourceGroups/FXTradingGame --sdk-auth
    ```
    This command will output a JSON object with the service principal’s credentials. Save this JSON object as you will need it in the next step.     

 2. Create a Kubernetes secret with the service principal’s credentials:
    ```
    kubectl create secret docker-registry acr-auth --docker-server=<acr-login-server> --docker-username=<app-id> --docker-password=<password> --docker-email=<email>
    ```
    Replace `<acr-login-server>` with the login server of your Azure Container Registry, `<app-id>` with the clientId from the JSON object, `<password>` with the clientSecret from the JSON object, and `<email>` with your email address.   
    You can find the name of the `acr-login-server` by running the following command `az acr show --name msfxtradinggame --query loginServer --output table` where `msfxtradinggame` is the registry where we pushed the docker image (it should be `msfxtradinggame.azurecr.io`)

You will notice the `Deployment.yaml` already contains a reference to this secret that the pods can use:
```
imagePullSecrets:
    - name: acr-auth
```

## Docker Image
The deployment of the docker image for the k8s set up is similar to the one suggested in the main README for single instance deployment.
Please run the following commands:
```
az acr show --name msfxtradinggame --query loginServer --output table
docker build -t fx-trading-game .
docker tag fx-trading-game msfxtradinggame.azurecr.io/fx-trading-game:latest
docker push msfxtradinggame.azurecr.io/fx-trading-game:latest
```

## Networking
**Core** Follow [this guide](https://learn.microsoft.com/en-us/azure/aks/static-ip) to create the Service with the correct IP address. 
The static IP address used within the ingress config was created as follows
```
az network public-ip create --resource-group FXTradingGame --name fx-game-static-ip --allocation-method Static --sku Standard
```
which resulted in
```
{
  "publicIp": {
    "ddosSettings": {
      "protectionMode": "VirtualNetworkInherited"
    },
    "etag": "W/\"501ca925-3b3c-4b68-b1e6-3ff3bad4fe5e\"",
    "id": "/subscriptions/db689aeb-843c-41a3-bf4e-54fdcc9a8c33/resourceGroups/FXTradingGame/providers/Microsoft.Network/publicIPAddresses/fx-game-static-ip",
    "idleTimeoutInMinutes": 4,
    "ipAddress": "52.233.160.180",
    "ipTags": [],
    "location": "westeurope",
    "name": "fx-game-static-ip",
    "provisioningState": "Succeeded",
    "publicIPAddressVersion": "IPv4",
    "publicIPAllocationMethod": "Static",
    "resourceGroup": "FXTradingGame",
    "resourceGuid": "3096221b-1aaf-4c22-8a1d-b6f8b1c52319",
    "sku": {
      "name": "Standard",
      "tier": "Regional"
    },
    "type": "Microsoft.Network/publicIPAddresses"
  }
}
```
You can check the IP address via
```
az network public-ip show --resource-group FXTradingGame --name fx-game-static-ip --query ipAddress --output tsv
```

## Deployment
You can deploy the app and latest version of the config by running `kubectl apply -f .` within this directory.   
Here is a set of helpful commands you can use to check the status of the pods and app once deployed:
```
kubectl get deployments
kubectl get pods
kunectl describe pod pod_id_here
kuectl logs pod_id_here
```