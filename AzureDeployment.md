1. Create a Microsoft Azure account.
    * See https://azure.microsoft.com/en-us/
1. Create a resource group (e.g. FXTradingGame).
    * See https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal
1. Create a container registry to upload our Docker images (e.g. fxtradinggame).
    * See https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal
1. Enable admin authentication for the container registry created above.
    * See https://docs.microsoft.com/en-us/azure/container-registry/container-registry-authentication?tabs=azure-cli#admin-account
1. Install Docker Desktop locally if using Windows. Note that you will need WSL 2 with virtualisation enabled in the 
   BIOS for that (by default disabled).
1. Open PowerShell as administrator.
1. cd to the home directory for this project, where Dockerfile is.
1. Create a docker image for this project.
    ```buildoutcfg
    docker build -t fx-trading-game .
    ```
1. Try to run the image locally.
    ```buildoutcfg
    docker run -p 80:80 -p 443:443 fx-trading-game
    ```
   Note that there is a known bug on Windows, whereby it is impossible to access the ports exposed by a docker container
   from the host itself. One would need to use the container's own IP address - which did not work in our case - or
   connect from another machine using the IP address of the host and the port exposed by the Docker container.
1. Tag the image with the container registry identifier.
    ```buildoutcfg
    docker tag fx-trading-game fxtradinggame.azurecr.io/fx-trading-game
    ```
1. Login to Azure.
    ```buildoutcfg
    docker login azure
    ```
1. Create an Azure ACI context.
    ```buildoutcfg
    docker context create aci fxtradinggame
    ```
1. Login to the container registry using the admin credentials provided on the Azure portal.
    ```buildoutcfg
    docker login fxtradinggame.azurecr.io/fx-trading-game
    ```
1. Upload the container to the registry.
    ```buildoutcfg
    docker push fxtradinggame.azurecr.io/fx-trading-game
    ```
1. Run the container locally
    ```buildoutcfg
    docker --context fxtradinggame run -p 80:80 -p 443:443 fxtradinggame.azurecr.io/fx-trading-game
    ```

## Running the image on Azure Container
1. You can spin up an image on a Container using the admin details from step 4 above
   ```
    az container create `
    --resource-group FXTradingGameRG `
    --name fx-trading-game-york-challenge `
    --image fxtradinggame.azurecr.io/fx-trading-game-custom:latest `
    --cpu 4 `
    --memory 16 `
    --registry-login-server fxtradinggame.azurecr.io `
    --registry-username fxtradinggame `
    --registry-password <REDACTED> `
    --ports 443 80 `
    --dns-name-label fx-trading-game-york-challenge `
   ```

Here are some useful commands

```
az container exec `
    --resource-group FXTradingGameRG `
    --name fx-trading-game-york-test `
    --exec-command "/bin/bash"

az container logs `
    --resource-group FXTradingGameRG `
    --name fx-trading-game-york-challenge `


az container delete `
    --resource-group FXTradingGameRG `
    --name fx-trading-game-york-challenge `
```
