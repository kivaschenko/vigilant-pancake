# vigilant-pancake
This project is a private attempt to build an e-commerce server according to my specific requirements. 
The main focus of the architecture strategy is TDD (test driven development) based on the book (https://github.com/cosmicpython/code/branches/all).

## Development

```
cd vigilant-pancake
```

### Run database

```
docker compose up -d
```

### Install dependecies
```
poetry install
```

### Run app in development mode:

```
fastapi dev src/main.py
```

### Run tests

```
pytest
```