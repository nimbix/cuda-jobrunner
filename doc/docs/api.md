# API Documentation

## REST API Endpoints

The REST API exposes simple job scheduling functionality for arbitrary asychronous, compute-intensive workflows.

### /submission

**POST** Submit a new job to be processed asynchronously

   Param      | Type          | Description
   ---------- | ------------- | ----------
   command | string | command that should be invoked in the environment
   file[]     | file(s) | multipart form-data files, where name of the file indicates the destination path
   unique_id | string (optional) | unique id used to track (will be generated if not provided)

** Example **

```python
import requests
response = requests.post('http://localhost:5000/submission',
                        data={'command': 'ls -al /tmp'},
                        files=[('file[]', ('/tmp/file.png', open('file.png'), 'image/png'))])
print(response.status_code)
print(response.json())
```
### /status/<string:job_id>

**GET** Queries a list of job statuses

### /files

**GET** Retreive a file for download, or a list of files in the top-level of a directory.

  Param | Type | Description
  ------|------|------------
  path  | string | absolute path to a file or directory


**Example**

### /download

**GET**

### /terminate

**POST** With no parameters, schedules the web service environment to terminate immediately

**Responses**

  Code | Meaning
  -----|--------
  202  | Shutdown has been scheduled
  

## Publish-Subscribe via RabbitMQ

After your call to **POST /submission**, you can use the `job_id` parameter to filter for the response on the `job_response` RabbitMQ queue.

**Example**

`pip install pika`

```python
# job_subscribe.py

import pika

connection = pika.BlockingConnection(pika.ConnectionParmeters('localhost'))
channel = connection.channel()
```
