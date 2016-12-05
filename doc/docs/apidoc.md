# API Documentation

## REST API Endpoints

The REST API exposes simple job scheduling functionality for arbitrary asychronous, compute-intensive workflows.

### /jobs

**GET** Queries a list of job statuses

**Responses**

  Code | Meaning
  -----|--------
  200  | List of jobs returned

Response Content:

  Param | Type | Description
  ------|------|------------
  count | int  | Number of currently running jobs
  results | array | Array of currently running jobs
  results[i] | job | dict-like representation of job

**POST** Submit a new job to be processed asynchronously

   Param      | Type          | Description
   ---------- | ------------- | ----------
   command    | string        | command that should be invoked in the environment
   file[]     | file(s)       | multipart form-data files, where name of the file indicates the destination path

**Responses**

  Code | Meaning
  -----|--------
  201  | Job has been created

Response Content:

  Param | Type | Description
  ------|------|------------
  job_id|string| unique job identifier
  command|string| The command used
  gpus | int(optional) | If present, indicates the number of GPUs requested

** Example **

```python
import requests
response = requests.post('http://localhost:5000/submission',
                        data={'command': 'ls -al /tmp'},
                        files=[('file[]', ('/tmp/file.png', open('file.png'), 'image/png'))])
print(response.status_code)
print(response.json())
```

### /jobs/{job_id}

**GET** Queries status of a single job

**Responses**

  Param | Type | Description
  ------|------|------------
  job_id|string|Job ID for currently running job
  status|string|One of 'QUEUED', 'PENDING', 'RUNNING', 'COMPLETE', 'FAILED'

  Code | Meaning
  -----|--------
  200  | OK
  404  | Job ID is not found

**DELETE** Schedules immediate termination of currently running job

**Responses**

  Code | Meaning
  -----|--------
  202  | Shutdown has been scheduled

  Param | Type | Description
  ------|------|------------
  id    | string | job id
  message | string | Status message that job is shutting down

### /files

**GET** Retreive a file for download, or a list of files in the top-level of a directory.

  Param | Type | Description
  ------|------|------------
  path  | string | absolute path to a file or directory


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
