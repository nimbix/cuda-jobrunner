# API Documentation

## REST API Endpoints

   - /submission
     - **POST** Submit a new job to be processed asynchronously
     
     Param      | Type          | Description
     ---------- | ------------- | ----------
     command | string | command that should be invoked in the environment
     file    | string | base64 encoded file data
     unique_id | string (optional) | unique id used to track (will be generated if not provided)
     
   - /status
     - GET
   - /jobs
     - GET
   - /files
     - GET
   - /download
   - /terminate

## Publish-Subscribe via RabbitMQ

