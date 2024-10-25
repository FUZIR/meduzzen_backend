## meduzzen_backend
### Repository for meduzzen internature back-end

## Steps to start a project:
1. Clone repo ```git clone https://github.com/FUZIR/meduzzen_backend.git``` 
2. Install dependencies ```poetry install```
3. Create ```.env``` with ```SECRET_KEY, ALLOWED_HOSTS```
4. Start project ```poetry run python -m core.manage runserver```

## Steps to start project in Docker:
1. Clone repo ```git clone https://github.com/FUZIR/meduzzen_backend.git``` 
2. Create ```.env``` with ```SECRET_KEY, ALLOWED_HOSTS, DEBUG ...(.env.sample)```
3. Run ```sudo docker compose up --build``` to build and run an images, migrations will migrate automatically
4. Run ```sudo docker compose up``` to start container (migrations will migrate automatically)