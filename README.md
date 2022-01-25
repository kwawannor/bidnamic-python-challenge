> NOTE! Building my own abstractions to show understanding of advanced python features, how and when to use them. In the real world, I will use existing solutions that have a huge community support and are well documented.


## Setup (Without Docker)


### 1) Install the dependencies and devDependencies.
> Requires Python3.9

```sh
make install
```

### 2) Set database env variables.
> Tested with Postgres 14.1

```sh
export DATABASE_NAME="dbname"
export DATABASE_PASSWORD="***"
export DATABASE_PORT=5432
export DATABASE_USER="dbuser"
export DATABASE_HOST="dbhost"
```

### 3) Load data.

```sh
make data
```

### 4) Run Endpoint
Run command below and access endpoint at local `PORT 8000`  http://localhost:8000/search
eg: http://localhost:8090/search?term=structure_value&value=nike

```sh
make endpoint

# testing
curl http://localhost:8000/search?term=structure_value&value=nike
```

### Run unit tests.

```sh
make test
```

## Setup (With Docker)
> Requires Docker Engine >= 17.05

### 1) Start Database

```sh
make dbuild
make ddatabase
```

### 2) Load Data

```sh
make dload
```


### 3) Start Endpoint 

```sh
make dendpoint


```
Access endpoint at local `PORT 8090` 
```
# testing
curl http://localhost:8090/search?term=structure_value&value=nike
```

### Run unit tests.

```sh
make dtest
```

### Stop all containers

```sh
make dstop
```