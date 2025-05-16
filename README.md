# Bachelorproef-prestatietesten

## Before starting the project
```bash
    $ npm install -g artillery
    $ python -m venv venv
    $ venv\Scripts\Activate.ps1
    $ pip install -r requirements.txt
```

- Create a `.env` file with the following values.
```
# --- Algemene API-configuratie ---

NODE_ENV=development
PORT=3000

# Databaseverbinding
DATABASE_URL=mysql://<USERNAME>:<PASSWORD>@localhost:3306/<DATABASE_NAME>

# Argon2 wachtwoordhash-instellingen
ARGON_HASH_LENGTH=32
ARGON_TIME_COST=6
ARGON_MEMORY_COST=131072

# JWT-configuratie
AUTH_JWT_SECRET=<YOUR-JWT-SECRET>
AUTH_JWT_EXPIRATION_INTERVAL=3600
AUTH_JWT_AUDIENCE=budget.hogent.be
AUTH_JWT_ISSUER=budget.hogent.be

# Logging
LOG_LEVEL=silly
LOG_DISABLED=false


# --- Scriptconfiguratie (voor automatisering en benchmarks) ---

# Pad naar de Yarn executable
YARN_EXECUTABLE="<PATH_TO_YARN>"

# Paden naar de drie API-implementaties
API_DIRECTORY_KOA="<PATH_TO>/webservices-budget"
API_DIRECTORY_HONO="<PATH_TO>/webservices-budget-hono"
API_DIRECTORY_NEST="<PATH_TO>/webservices-budget-nest"

```
## Compile and run the tests

### Build_test
```bash
    $ python build_testing/build_timer.py  
```

### Load_test
#### Before running Load tests for nest
 In each scenario, the API paths should be changed to correspond to the framework being tested.


#### Run commands
```bash
    # NestJs
    $ python load_testing_api/load_tests.py nest
    # Hono
    $ python load_testing_api/load_tests.py hono
    # Koa
    $ python load_testing_api/load_tests.py koa

```
