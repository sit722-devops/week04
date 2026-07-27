# Week 04 : Example 1 — Running and Deploying the University Course Platform

## Prerequisites

Install the following software before starting:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.12](https://www.python.org/downloads/)
- [Node.js (LTS)](https://nodejs.org/en/download)
- [Visual Studio Code](https://code.visualstudio.com/download?_exp_download=fb315fc982)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [PostgreSQL client (`psql`)](https://www.postgresql.org/download/)

## Setup Azure CLI

1. Login to Azure (selecting your correct Azure subscription):

   ```bash
   az login
   ```

2. Verify:

   ```bash
   az account show --output table
   ```

---

## Test Backend Services

1. Start the student database:

   ```bash
   docker compose up -d student-db
   ```

2. Navigate to the Student Service:

   ```bash
   cd student-service
   ```

3. Create a virtual environment:

   ```bash
   # Create the virtual environment
   python -m venv .venv

   # Activate the virtual environment
   # On macOS/Linux:
   source ./.venv/bin/activate

   # On Windows (Command Prompt):
   # .\.venv\Scripts\activate.bat

   # On Windows (PowerShell):
   # .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run unit tests:

   ```bash
   pytest tests
   $env:POSTGRES_PORT=5433
   pytest --verbose tests
   ```

6. Deactivate the virtual environment and return to the project root.

   ```bash
   deactivate
   cd ..
   ```

> **NOTE**:
> Repeat the same steps for the Course Service using  `$env:POSTGRES_PORT=5434`
> Make sure to start course-db before testing Course Service.
> Ensure all tests pass before continuing.

---

## Test Frontend

1. Navigate to the frontend:

   ```bash
   cd frontend
   ```

2. Install packages:

   ```bash
   npm install
   ```

3. Run frontend tests:

   ```bash
   npm test
   ```

4. Return to the project root:

   ```bash
   cd ..
   ```

---

## Run the Entire Application Locally

Before deploying to Azure App Service, verify that the application works correctly using Docker Compose.

From the project root:

```bash
docker compose build --no-cache

docker compose up -d
```

## Verify Running Containers

Run following:

```bash
docker compose ps
```

You should see the following containers running:

- frontend
- student-service
- course-service
- student-db
- course-db

---

### Access the Application

### Frontend

```
http://localhost:5173
```

Verify that:

- Student records load successfully.
- Course records load successfully.
- Create, Update and Delete operations work correctly.

## Stop the Application

Stop all running containers.

```bash
docker compose down
```

To also remove the PostgreSQL volumes and start with a fresh database next time, run:

```bash
docker compose down -v
```

---

## Deploy Apllication on Azure App Service

1. Define Deployment Variables

   We will define all deployment variables before creating the Azure resources.

   > **NOTE**:
   > Replace the values inside angle brackets with your own unique values.

   ```bash
   # General Azure configuration
   RESOURCE_GROUP="rg-campus-course-week04"
   LOCATION="australiaeast"

   # Azure Container Registry
   # ** The name must be globally unique and contain only lowercase letters and numbers. **
   ACR_NAME="<your-unique-acr-name>"
   ACR_SKU="Basic"

   # Azure PostgreSQL Flexible Server
   # ** The server name must be globally unique. **
   POSTGRES_SERVER_NAME="<your-unique-postgres-server-name>"
   POSTGRES_ADMIN_USER="<your-postgres-admin-username>"
   POSTGRES_ADMIN_PASSWORD="<your-strong-postgres-password>"
   POSTGRES_SKU="Standard_B1ms"
   POSTGRES_TIER="burstable"
   POSTGRES_STORAGE_SIZE="32"
   POSTGRES_VERSION="16"

   # PostgreSQL databases
   STUDENT_DATABASE="students"
   COURSE_DATABASE="courses"

   # Azure App Service Plan
   APP_SERVICE_PLAN="campus-plan"
   APP_SERVICE_SKU="B1"

   # Azure App Service names
   # ** Each App Service name must be globally unique. **
   STUDENT_APP_NAME="<your-unique-student-app-name>"
   COURSE_APP_NAME="<your-unique-course-app-name>"
   FRONTEND_APP_NAME="<your-unique-frontend-app-name>"

   # Container image names
   STUDENT_IMAGE_NAME="student-service"
   COURSE_IMAGE_NAME="course-service"
   FRONTEND_IMAGE_NAME="frontend"
   IMAGE_TAG="v1"

   # Service Principal
   # ** Consider making the campus-acr-sp unique. I.e., with your student number of initials. **
   SP_NAME='<campus-acr-sp-initials>'
   ```

2. Create the derived variables:

   ```bash
   ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"

   POSTGRES_HOST="${POSTGRES_SERVER_NAME}.postgres.database.azure.com"

   STUDENT_IMAGE="${ACR_LOGIN_SERVER}/${STUDENT_IMAGE_NAME}:${IMAGE_TAG}"
   COURSE_IMAGE="${ACR_LOGIN_SERVER}/${COURSE_IMAGE_NAME}:${IMAGE_TAG}"
   FRONTEND_IMAGE="${ACR_LOGIN_SERVER}/${FRONTEND_IMAGE_NAME}:${IMAGE_TAG}"

   STUDENT_APP_URL="https://${STUDENT_APP_NAME}.azurewebsites.net"
   COURSE_APP_URL="https://${COURSE_APP_NAME}.azurewebsites.net"
   FRONTEND_APP_URL="https://${FRONTEND_APP_NAME}.azurewebsites.net"
   ```

   > **NOTE**:
   > These shell variables are stored only in the current terminal session. Continue using the same terminal while completing the deployment.

3. Create Azure Resource Group

   ```bash
   az group create \
       --name "$RESOURCE_GROUP" \
       --location "$LOCATION"
   ```

   Verify the resource group:

   ```bash
   az group show \
       --name "$RESOURCE_GROUP" \
       --output table
   ```

4. Create Azure Container Registry

   ```bash
   az acr create \
       --resource-group "$RESOURCE_GROUP" \
       --name "$ACR_NAME" \
       --sku "$ACR_SKU"
   ```

5. Log in to the registry:

   ```bash
   az acr login \
       --name "$ACR_NAME"
   ```

6. Verify the registry:

   ```bash
   az acr show \
       --resource-group "$RESOURCE_GROUP" \
       --name "$ACR_NAME" \
       --query "{Name:name, LoginServer:loginServer, SKU:sku.name}" \
       --output table
   ```

7. Create Azure PostgreSQL Flexible Server

   ```bash
   az postgres flexible-server create \
       --resource-group "$RESOURCE_GROUP" \
       --name "$POSTGRES_SERVER_NAME" \
       --location "$LOCATION" \
       --admin-user "$POSTGRES_ADMIN_USER" \
       --admin-password "$POSTGRES_ADMIN_PASSWORD" \
       --tier "$POSTGRES_TIER" \
       --sku-name "$POSTGRES_SKU" \
       --storage-size "$POSTGRES_STORAGE_SIZE" \
       --version "$POSTGRES_VERSION" \
       --public-access 0.0.0.0
   ```

8. Verify the PostgreSQL server:

   ```bash
   az postgres flexible-server show \
       --resource-group "$RESOURCE_GROUP" \
       --name "$POSTGRES_SERVER_NAME" \
       --query "{Name:name, Host:fullyQualifiedDomainName, State:state, Version:version}" \
       --output table
   ```

   > **NOTE:**
   > Wait until the server state is:
   > `Ready`

9. Configure PostgresSQL Firewall Rules
   1. Get your current public IP address:

      ```bash
      CLIENT_IP=$(curl -s https://api.ipify.org)
      echo $CLIENT_IP
      ```

   2. Allow your local computer to access the PostgreSQL server:

      ```bash
      az postgres flexible-server firewall-rule create \
          --resource-group "$RESOURCE_GROUP" \
          --name "$POSTGRES_SERVER_NAME" \
          --rule-name "AllowMyLocalComputer" \
          --start-ip-address "$CLIENT_IP" \
          --end-ip-address "$CLIENT_IP"
      ```

   3. Allow Azure services (required for Azure App Services to connect to PostgreSQL):

      ```bash
      az postgres flexible-server firewall-rule create \
          --resource-group "$RESOURCE_GROUP" \
          --name "$POSTGRES_SERVER_NAME" \
          --rule-name "AllowAzureServices" \
          --start-ip-address "0.0.0.0" \
          --end-ip-address "0.0.0.0"
      ```

      The Azure services firewall rule allows the Azure App Services to connect to the PostgreSQL server.

   4. Verify the firewall rules:

      ```bash
      az postgres flexible-server firewall-rule list \
          --resource-group "$RESOURCE_GROUP" \
          --name "$POSTGRES_SERVER_NAME" \
          --output table
      ```

10. Create Databases
    1. Create the Student Service database:

       ```bash
       az postgres flexible-server db create \
           --resource-group "$RESOURCE_GROUP" \
           --server-name "$POSTGRES_SERVER_NAME" \
           --database-name "$STUDENT_DATABASE"
       ```

    2. Create the Course Service database:

       ```bash
       az postgres flexible-server db create \
           --resource-group "$RESOURCE_GROUP" \
           --server-name "$POSTGRES_SERVER_NAME" \
           --database-name "$COURSE_DATABASE"
       ```

    3. Verify the databases:

       ```bash
       az postgres flexible-server db list \
           --resource-group "$RESOURCE_GROUP" \
           --server-name "$POSTGRES_SERVER_NAME" \
           --output table
       ```

       The database list should include:

       ```bash
       students
       courses
       ```

11. Build Backend Images in ACR

    Azure Container Registry can build the images directly from the Dockerfiles in the project.
    1. Build the Student Service image:

       ```bash
       az acr build --registry "$ACR_NAME" \
           --image "${STUDENT_IMAGE_NAME}:${IMAGE_TAG}" \
           "$STUDENT_IMAGE_NAME"
       ```

    2. Build the Course Service image:
       ```bash
       az acr build --registry "$ACR_NAME" \
           --image "${COURSE_IMAGE_NAME}:${IMAGE_TAG}" \
           "$COURSE_IMAGE_NAME"
       ```
    3. Verify the repositories:
       ```bash
       az acr repository list --name "$ACR_NAME" \
           --output table
       ```

12. Create the Azure App Service Plan
    1. Create a Linux App Service Plan:

       ```bash
       az appservice plan create \
           --resource-group "$RESOURCE_GROUP" \
           --name "$APP_SERVICE_PLAN" \
           --location "$LOCATION" \
           --is-linux \
           --sku "$APP_SERVICE_SKU"
       ```

       The Student Service, Course Service and frontend will use the same App Service Plan.

    2. Verify the plan:

       ```bash
       az appservice plan show \
           --resource-group "$RESOURCE_GROUP" \
           --name "$APP_SERVICE_PLAN" \
           --query "{Name:name, Location:location, SKU:sku.name, Linux:reserved}" \
           --output table
       ```

13. Create the ACR Service Principal
    1. Get the Azure Container Registry resource ID:

       ```bash
       ACR_ID=$(az acr show \
           --resource-group "$RESOURCE_GROUP" \
           --name "$ACR_NAME" \
           --query id \
           --output tsv)
       ```

    2. Create a Service Principal and assign the AcrPull role:

    ```bash
    read -r SP_APP_ID SP_PASSWORD <<< "$(az ad sp create-for-rbac \
        --name "$SP_NAME" \
        --role "AcrPull" \
        --scopes "$ACR_ID" \
        --query "[appId,password]" \
        --output tsv)"
    ```

    3. Verify the role assignment:

       ```bash
       az role assignment list \
           --assignee "$SP_APP_ID" \
           --scope "$ACR_ID" \
           --output table
       ```

    > **NOTE:**
    > Keep this terminal open. The generated Service Principal password is stored in the `SP_PASSWORD` variable and will be used when configuring the App Services.

14. Deploy the Student Service
    1. Create the Student Service App Service:

       ```bash
       az webapp create \
           --resource-group "$RESOURCE_GROUP" \
           --plan "$APP_SERVICE_PLAN" \
           --name "$STUDENT_APP_NAME" \
           --container-image-name "$STUDENT_IMAGE"
       ```

    2. Configure the App Service to pull the image from ACR:

       ```bash
       az webapp config container set \
           --resource-group "$RESOURCE_GROUP" \
           --name "$STUDENT_APP_NAME" \
           --container-image-name "$STUDENT_IMAGE" \
           --container-registry-url "https://${ACR_LOGIN_SERVER}" \
           --container-registry-user "$SP_APP_ID" \
           --container-registry-password "$SP_PASSWORD"
       ```

    3. Configure the Student Service application settings:

       ```bash
       az webapp config appsettings set \
           --resource-group "$RESOURCE_GROUP" \
           --name "$STUDENT_APP_NAME" \
           --settings \
               WEBSITES_PORT="8000" \
               POSTGRES_USER="$POSTGRES_ADMIN_USER" \
               POSTGRES_PASSWORD="$POSTGRES_ADMIN_PASSWORD" \
               POSTGRES_DB="$STUDENT_DATABASE" \
               POSTGRES_HOST="$POSTGRES_HOST" \
               POSTGRES_PORT="5432" \
               POSTGRES_SSLMODE="require"
       ```

    4. Restart the Student Service:
       ```bash
       az webapp restart \
           --resource-group "$RESOURCE_GROUP" \
           --name "$STUDENT_APP_NAME"
       ```
    5. Check the Student Service status:

       ```bash
       az webapp show \
           --resource-group "$RESOURCE_GROUP" \
           --name "$STUDENT_APP_NAME" \
           --query "{Name:name, State:state, URL:defaultHostName}" \
           --output table
       ```

15. Deploy the Course Service
    1. Create the Course Service App Service:

       ```bash
       az webapp create \
           --resource-group "$RESOURCE_GROUP" \
           --plan "$APP_SERVICE_PLAN" \
           --name "$COURSE_APP_NAME" \
           --container-image-name "$COURSE_IMAGE"
       ```

    2. Configure the App Service to pull the image from ACR:

       ```bash
       az webapp config container set \
           --resource-group "$RESOURCE_GROUP" \
           --name "$COURSE_APP_NAME" \
           --container-image-name "$COURSE_IMAGE" \
           --container-registry-url "https://${ACR_LOGIN_SERVER}" \
           --container-registry-user "$SP_APP_ID" \
           --container-registry-password "$SP_PASSWORD"
       ```

    3. Configure the Course Service application settings:

       ```bash
       az webapp config appsettings set \
           --resource-group "$RESOURCE_GROUP" \
           --name "$COURSE_APP_NAME" \
           --settings \
               WEBSITES_PORT="8000" \
               POSTGRES_USER="$POSTGRES_ADMIN_USER" \
               POSTGRES_PASSWORD="$POSTGRES_ADMIN_PASSWORD" \
               POSTGRES_DB="$COURSE_DATABASE" \
               POSTGRES_HOST="$POSTGRES_HOST" \
               POSTGRES_PORT="5432" \
               POSTGRES_SSLMODE="require"
       ```

    4. Restart the Course Service:

       ```bash
       az webapp restart \
           --resource-group "$RESOURCE_GROUP" \
           --name "$COURSE_APP_NAME"
       ```

    5. Check the Course Service status:
       ```bash
       az webapp show \
           --resource-group "$RESOURCE_GROUP" \
           --name "$COURSE_APP_NAME" \
           --query "{Name:name, State:state, URL:defaultHostName}" \
           --output table
       ```

16. Verify the Backend Services
    1. Open the Student Service Swagger interface:
       ```bash
       https://<your-student-app-name>.azurewebsites.net/docs
       ```
    2. Open the Course Service Swagger interface:
       ```bash
       https://<your-course-app-name>.azurewebsites.net/docs
       ```

17. Build the Frontend Image
    The frontend requires the deployed backend URLs during the Vite build process.
    1. Build the frontend image in ACR:

       ```bash
       az acr build \
           --registry "$ACR_NAME" \
           --image "${FRONTEND_IMAGE_NAME}:${IMAGE_TAG}" \
           --build-arg "VITE_STUDENT_SERVICE_URL=${STUDENT_APP_URL}/students" \
           --build-arg "VITE_COURSE_SERVICE_URL=${COURSE_APP_URL}/courses" \
           ./frontend
       ```

    2. Verify the frontend image:
       ```bash
       az acr repository show-tags \
           --name "$ACR_NAME" \
           --repository "$FRONTEND_IMAGE_NAME" \
           --output table
       ```

18. Deploy the Frontend
    1. Create the frontend App Service:
       ```bash
       az webapp create \
           --resource-group "$RESOURCE_GROUP" \
           --plan "$APP_SERVICE_PLAN" \
           --name "$FRONTEND_APP_NAME" \
           --container-image-name "$FRONTEND_IMAGE"
       ```
    2. Configure the frontend to pull the image from ACR:
       ```bash
       az webapp config container set \
           --resource-group "$RESOURCE_GROUP" \
           --name "$FRONTEND_APP_NAME" \
           --container-image-name "$FRONTEND_IMAGE" \
           --container-registry-url "https://${ACR_LOGIN_SERVER}" \
           --container-registry-user "$SP_APP_ID" \
           --container-registry-password "$SP_PASSWORD"
       ```
    3. Configure the frontend container port:
       ```bash
       az webapp config appsettings set \
           --resource-group "$RESOURCE_GROUP" \
           --name "$FRONTEND_APP_NAME" \
           --settings \ WEBSITES_PORT="80"
       ```
    4. Restart the frontend:
       ```bash
       az webapp restart \
           --resource-group "$RESOURCE_GROUP" \
           --name "$FRONTEND_APP_NAME"
       ```
    5. Check the frontend status:
       ```bash
       az webapp show \
           --resource-group "$RESOURCE_GROUP" \
           --name "$FRONTEND_APP_NAME" \
           --query "{Name:name, State:state, URL:defaultHostName}" \
           --output table
       ```

19. Configure Backend CORS
    1. Configure the Student Service to allow requests from the deployed frontend:
       ```bash
           az webapp config appsettings set \
               --resource-group "$RESOURCE_GROUP" \
               --name "$STUDENT_APP_NAME" \
               --settings \
                   FRONTEND_ORIGIN="$FRONTEND_APP_URL"
       ```
    2. Configure the Course Service to allow requests from the deployed frontend:
       ```bash
       az webapp config appsettings set \
           --resource-group "$RESOURCE_GROUP" \
           --name "$COURSE_APP_NAME" \
           --settings \
               FRONTEND_ORIGIN="$FRONTEND_APP_URL"
       ```
    3. Restart the Student Service:
       ```bash
       az webapp restart \
           --resource-group "$RESOURCE_GROUP" \
           --name "$STUDENT_APP_NAME"
       ```
    4. Restart the Course Service:
       ```bash
       az webapp restart \
           --resource-group "$RESOURCE_GROUP" \
           --name "$COURSE_APP_NAME"
       ```
    5. Restart the frontend:
       ```bash
       az webapp restart \
           --resource-group "$RESOURCE_GROUP" \
           --name "$FRONTEND_APP_NAME"
       ```

20. Verify the Complete Deployment
    1. Open the frontend:

       ```bash
       https://<your-frontend-app-name>.azurewebsites.net
       ```

    2. Open the Student Service Swagger interface:

       ```bash
       https://<your-student-app-name>.azurewebsites.net/docs
       ```

    3. Open the Course Service Swagger interface:
       ```bash
       https://<your-course-app-name>.azurewebsites.net/docs
       ```

21. Test the Bachend service

    Perform following operations through the frontend:
    1. Student Service
       - View all students
       - Create a student
       - Update a student
       - Delete a student

    2. Course Service
       - View all courses
       - Create a course
       - Update a course
       - Delete a course

    Refresh the frontend and confirm that the data remains available in PostgreSQL.

22. Clean Up Azure Resources
    1. Delete the Service Principal:
       ```bash
       az ad sp delete --id "$SP_APP_ID"
       ```
    2. Delete the Azure Resource Group and all resources contained within it:
       ```bash
       az group delete \
           --name "$RESOURCE_GROUP" \
           --yes \
           --no-wait
       ```
