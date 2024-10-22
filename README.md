## meduzzen_backend
### Repository for meduzzen internature back-end

## Steps to start a project:
1. Clone repo ```git clone https://github.com/FUZIR/meduzzen_backend.git``` 
2. Install dependencies ```poetry install```
3. Create ```.env``` with ```SECRET_KEY, ALLOWED_HOSTS```
4. Start project ```poetry run python -m core.manage runserver```

## Steps to start project in Docker:
1. Clone repo ```git clone https://github.com/FUZIR/meduzzen_backend.git``` 
2. Create ```.env``` with ```SECRET_KEY, ALLOWED_HOSTS, DEBUG```
3. Run ```sudo docker buildx build -t django_backend .``` to build an image
4. Run ```sudo docker run -p 8000:8000 django_backend``` to start container