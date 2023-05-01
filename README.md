# Summit - Saloon Studios

## Local development
Requires Python >= 3.7

### Create venv 
```
python -m venv venv
source venv/bin/activate
```

### Install dependencies
```
pip install -r requirements.text
```

### Run migrations
```
python manage.py migrate
```

### Run local server
```
python manage.py runserver
```

## Run django tests
```
python manage.py test --settings=summit.settings.
```