# Week 04 — Running and Deploying the Campus Course Platform

## Prerequisites

Install the following software before starting:

* Docker Desktop
* Python 3.12
* Node.js (LTS)
* Visual Studio Code
* Azure CLI
* PostgreSQL client (`psql`)

Login to Azure (selecting your correct Azure subscription):

```bash
az login
```

Verify:

```bash
az account show --output table
```

---

# Part 1 — Test Student Service

Start the student database:

```bash
docker compose up -d student-db
```

Navigate to the Student Service:

```bash
cd student-service
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment (macOS/Linux):

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run unit tests:

```bash
$env:POSTGRES_PORT=5433
pytest --verbose tests
```

Return to the project root:

```bash
cd ..
```

---

# Part 2 — Test Course Service

Start the course database:

```bash
docker compose up -d course-db
```

Navigate to the Course Service:

```bash
cd course-service
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run unit tests:

```bash
$env:POSTGRES_PORT=5434
pytest tests
```

Return to the project root:

```bash
cd ..
```

---

# Part 3 — Test Frontend

Navigate to the frontend:

```bash
cd frontend
```

Install packages:

```bash
npm install
```

Run frontend tests:

```bash
npm test
```

Build the frontend:

```bash
npm run build
```

Return to the project root:

```bash
cd ..
```

---

# Part 4 — Run the Entire Application Locally

Build and start all services:

```bash
docker compose down
```

```bash
docker compose up --build -d
```

Open:

Frontend

```
http://localhost:5173
```

Student Service Swagger

```
http://localhost:8001/docs
```

Course Service Swagger

```
http://localhost:8002/docs
```

Stop the application:

```bash
docker compose down
```

---

# Part 5 — Create Azure Resource Group

```bash
az group create \
    --name rg-campus-course-week04 \
    --location australiaeast
```

---

# Part 6 — Create Azure Container Registry

```bash
az acr create \
    --resource-group rg-campus-course-week04 \
    --name <YOUR_ACR_NAME> \
    --sku Basic
```

Login to ACR:

```bash
az acr login --name <YOUR_ACR_NAME>
```

---

# Part 7 — Create Azure PostgreSQL Flexible Server

```bash
az postgres flexible-server create \
  --resource-group rg-campus-course-week04 \
  --name <POSTGRES_SERVER_NAME> \
  --location australiaeast \
  --admin-user <ADMIN_USERNAME> \
  --admin-password '<PASSWORD>' \
  --tier burstable \
  --sku-name Standard_B1ms \
  --storage-size 32 \
  --version 16 \
  --public-access 0.0.0.0
```

---

# Part 8 — Configure Firewall Rules

Get your current public IP address:

```bash
CLIENT_IP=$(curl -s https://api.ipify.org)
echo $CLIENT_IP
```

Allow your local computer to access the PostgreSQL server:

```bash
az postgres flexible-server firewall-rule create \
  --resource-group rg-campus-course-week04 \
  --name <POSTGRES_SERVER_NAME> \
  --rule-name AllowMyLocalComputer \
  --start-ip-address $CLIENT_IP \
  --end-ip-address $CLIENT_IP
```

Allow Azure services (required for Azure App Services to connect to PostgreSQL):

```bash
az postgres flexible-server firewall-rule create \
  --resource-group rg-campus-course-week04 \
  --name <POSTGRES_SERVER_NAME> \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

(Optional) Verify the firewall rules:

```bash
az postgres flexible-server firewall-rule list \
  --resource-group rg-campus-course-week04 \
  --name <POSTGRES_SERVER_NAME> \
  --output table
```

---

# Part 9 — Create Databases

Connect to the PostgreSQL server:

```bash
psql "host=<POSTGRES_SERVER>.postgres.database.azure.com port=5432 dbname=postgres user=<ADMIN_USERNAME> password=<PASSWORD> sslmode=require"
```

Create the databases:

```sql
CREATE DATABASE students;
CREATE DATABASE courses;
```

Exit PostgresSQL:

```sql
\q
```

---

# Part 10 — Build Backend Images

Student Service:

```bash
az acr build \
    --registry <YOUR_ACR_NAME> \
    --image student-service:v1 \
    ./student-service
```

Course Service:

```bash
az acr build \
    --registry <YOUR_ACR_NAME> \
    --image course-service:v1 \
    ./course-service
```

Verify:

```bash
az acr repository list \
    --name <YOUR_ACR_NAME> \
    --output table
```

---

# Part 11 — Create Azure App Service Plan

```bash
az appservice plan create \
    --resource-group rg-campus-course-week04 \
    --name <APP_SERIVCE_NAME> \
    --location australiaeast \
    --is-linux \
    --sku B1
```

---

# Part 12 — Create Service Principal

Get the ACR Resource ID:

```bash
ACR_ID=$(az acr show \
    --name <YOUR_ACR_NAME> \
    --query id \
    --output tsv)
```

Create the Service Principal:

```bash
SP_PASSWORD=$(az ad sp create-for-rbac \
    --name <APP_SERIVCE_NAME> \
    --role AcrPull \
    --scopes "$ACR_ID" \
    --query password \
    --output tsv)
```

Get the Application ID:

```bash
SP_APP_ID=$(az ad sp list \
    --display-name <APP_SERIVCE_NAME> \
    --query "[0].appId" \
    --output tsv)
```

---

# Part 13 — Deploy Student Service

Create App Service:

```bash
az webapp create \
    --resource-group rg-campus-course-week04 \
    --plan campus-plan \
    --name <STUDENT_APP_NAME> \
    --container-image-name <YOUR_ACR_NAME>.azurecr.io/student-service:v1
```

Configure container registry:

```bash
az webapp config container set \
    --resource-group rg-campus-course-week04 \
    --name <STUDENT_APP_NAME> \
    --container-image-name <YOUR_ACR_NAME>.azurecr.io/student-service:v1 \
    --container-registry-url https://<YOUR_ACR_NAME>.azurecr.io \
    --container-registry-user "$SP_APP_ID" \
    --container-registry-password "$SP_PASSWORD"
```

Configure application settings:

```bash
az webapp config appsettings set \
    --resource-group rg-campus-course-week04 \
    --name <STUDENT_APP_NAME> \
    --settings \
        WEBSITES_PORT=8000 \
        POSTGRES_USER=<ADMIN_USERNAME> \
        POSTGRES_PASSWORD=<PASSWORD> \
        POSTGRES_DB=students \
        POSTGRES_HOST=<POSTGRES_SERVER>.postgres.database.azure.com \
        POSTGRES_PORT=5432 \
        POSTGRES_SSLMODE=require
```

Restart:

```bash
az webapp restart \
    --resource-group rg-campus-course-week04 \
    --name <STUDENT_APP_NAME>
```

---

# Part 14 — Deploy Course Service

Create App Service:

```bash
az webapp create \
    --resource-group rg-campus-course-week04 \
    --plan campus-plan \
    --name <COURSE_APP_NAME> \
    --container-image-name <YOUR_ACR_NAME>.azurecr.io/course-service:v1
```

Configure container registry:

```bash
az webapp config container set \
    --resource-group rg-campus-course-week04 \
    --name <COURSE_APP_NAME> \
    --container-image-name <YOUR_ACR_NAME>.azurecr.io/course-service:v1 \
    --container-registry-url https://<YOUR_ACR_NAME>.azurecr.io \
    --container-registry-user "$SP_APP_ID" \
    --container-registry-password "$SP_PASSWORD"
```

Configure application settings:

```bash
az webapp config appsettings set \
    --resource-group rg-campus-course-week04 \
    --name <COURSE_APP_NAME> \
    --settings \
        WEBSITES_PORT=8000 \
        POSTGRES_USER=<ADMIN_USERNAME> \
        POSTGRES_PASSWORD=<PASSWORD> \
        POSTGRES_DB=courses \
        POSTGRES_HOST=<POSTGRES_SERVER>.postgres.database.azure.com \
        POSTGRES_PORT=5432 \
        POSTGRES_SSLMODE=require
```

Restart:

```bash
az webapp restart \
    --resource-group rg-campus-course-week04 \
    --name <COURSE_APP_NAME>
```

---

# Part 15 — Build Frontend Image

```bash
az acr build \
    --registry <YOUR_ACR_NAME> \
    --image frontend:v1 \
    --build-arg VITE_STUDENT_SERVICE_URL=https://<STUDENT_APP_NAME>.azurewebsites.net/students \
    --build-arg VITE_COURSE_SERVICE_URL=https://<COURSE_APP_NAME>.azurewebsites.net/courses \
    ./frontend
```

---

# Part 16 — Deploy Frontend

Create App Service:

```bash
az webapp create \
    --resource-group rg-campus-course-week04 \
    --plan <APP_SERIVCE_NAME> \
    --name <FRONTEND_APP_NAME> \
    --container-image-name <YOUR_ACR_NAME>.azurecr.io/frontend:v1
```

Configure container registry:

```bash
az webapp config container set \
    --resource-group rg-campus-course-week04 \
    --name <FRONTEND_APP_NAME> \
    --container-image-name <YOUR_ACR_NAME>.azurecr.io/frontend:v1 \
    --container-registry-url https://<YOUR_ACR_NAME>.azurecr.io \
    --container-registry-user "$SP_APP_ID" \
    --container-registry-password "$SP_PASSWORD"
```

Configure App Service:

```bash
az webapp config appsettings set \
    --resource-group rg-campus-course-week04 \
    --name <FRONTEND_APP_NAME> \
    --settings WEBSITES_PORT=80
```

Restart:

```bash
az webapp restart \
    --resource-group rg-campus-course-week04 \
    --name <FRONTEND_APP_NAME>
```

---

# Part 17 — Update Backend CORS

Student Service:

```bash
az webapp config appsettings set \
    --resource-group rg-campus-course-week04 \
    --name <STUDENT_APP_NAME> \
    --settings FRONTEND_ORIGIN=https://<FRONTEND_APP_NAME>.azurewebsites.net
```

Course Service:

```bash
az webapp config appsettings set \
    --resource-group rg-campus-course-week04 \
    --name <COURSE_APP_NAME> \
    --settings FRONTEND_ORIGIN=https://<FRONTEND_APP_NAME>.azurewebsites.net
```

Restart both services:

```bash
az webapp restart \
    --resource-group rg-campus-course-week04 \
    --name <STUDENT_APP_NAME>
```

```bash
az webapp restart \
    --resource-group rg-campus-course-week04 \
    --name <COURSE_APP_NAME>
```

---

# Part 18 — Verify Deployment

Open the frontend:

```
https://<FRONTEND_APP_NAME>.azurewebsites.net
```

Open Student Swagger:

```
https://<STUDENT_APP_NAME>.azurewebsites.net/docs
```

Open Course Swagger:

```
https://<COURSE_APP_NAME>.azurewebsites.net/docs
```

Verify:

* Create Student
* Update Student
* Delete Student
* Create Course
* Update Course
* Delete Course
* Refresh the frontend
* Confirm data persists in PostgreSQL

---

# Part 19 — Clean Up Resources

Delete the resource group:

```bash
az group delete \
    --name rg-campus-course-week04 \
    --yes \
    --no-wait
```

Delete the Service Principal:

```bash
az ad sp delete \
    --id "$SP_APP_ID"
```
