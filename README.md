# Stress Predict Service
## Create Virtual Environment using (virtualenv for linux)
```
virtualenv  vend
source vend/bin/activate
```

## Install 
```
 pip3 install -r requiments.txt
 python3 run.py
```

## Usage

All responses will have the form

```json
{
    "data": "Mixed type holding the content of the response",
    "message": "Description of what happened"
}
```

Subsequent response definitions will only detail the expected value of the `data field`

### List all devices

**Definition**

`GET /hearrate`

**Response**

- `200 OK` on success
### Registering a new device

**Definition**

`POST /devices`

**Arguments**

- `"date":string` date time when send data
- `"time":string` time when send data
- `"data":string` list data hearrate


**Response**

- `200` on success

```json
{
    "date": "20/04/2020",
    "name": "23:23",
    "data": "23,445,33,223,45,232,23,34,23",
}
```


