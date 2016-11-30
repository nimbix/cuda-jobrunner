from flask import Flask, send_from_directory, redirect, request
from flask_restful import Resource, Api, reqparse
import random
import os
import subprocess
import logging
import uuid

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = '/data'


app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

template = '#!/bin/bash\n' \
           '#SBATCH -e /tmp/{job_id}.err -o ' \
           '/tmp/{job_id}.out\nsrun {command}\n'


def queue_job(command, files):
    job_id = uuid.uuid4()
    message = '"{job_id}","{command}","{files}"\n'.format(
        job_id=job_id,
        command=command,
        files=''.join(files))
    logger.info(message)
    job_script = '/tmp/{job_id}.sh'.format(job_id=job_id)
    with open(job_script, 'wb') as f:
        f.write(template.format(job_id=job_id,
                                command=command))
    subprocess.call(['sbatch', '-J', str(job_id), job_script])
    return job_id


@app.route('/terminate', methods=['POST'])
def terminate():
    """Cleanly terminates the entire web service environment.

    Returns:
       202 {'message': <string>}
    """
    os.system('sudo poweroff')
    return {'message': 'terminating'}, 202


@app.route('/status', methods=['GET'])
def status():
    """Returns status of the environment in the following format:

    {
        'id': '%NAE_PUBLICADDR%',
        'shutdown_policy': {
            'policy': 'idle_countdown'
         },
         'jobs': [{
             'id': 'job-xyz-response-queue',
             'status': 'xxx',
             'command': 'yyy',
             'output_dir': 'zzz'
         }, ... ],
    }
    """
    return {'status': 'OK'}


def handle_file(file_t, destination):
    file_t.save(destination)
    return destination


class Status(Resource):
    def get(self, job_id):
        return {'id': job_id, 'status': 'OK'}


class Submission(Resource):

    def post(self, todo_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('command',
                            type=str,
                            required=True,
                            help='Command line to execute')
        parser.add_argument('files', type=str)
        args = parser.parse_args(strict=True)

        command = args.get('command', None)

        file_list = request.files.getlist('file[]')
        filepaths = []

        for i in file_list:
            handle_file(i, i.filename)
            filepaths.append(i.filename)

        # Post asynchronously
        job_id = queue_job(command, filepaths)
        return {
            'id': job_id,
            'command': command,
            'files': ';'.join(filepaths)
        }, 201


class Files(Resource):
    """Static file REST endpoint. Note that all files that are not stored
    in /data will not be persisted when this environment is terminated.
    """

    def get(self):
        """Retrieves a file from path

        Args:
          path(string): Full path to file

        Returns:
          200 File returned for download
          404 File not found
        """
        parser = reqparse.RequestParser()
        parser.add_argument('path', type=str)
        args = parser.parse_args(strict=True)
        file_path = args.get('path', None)

        if os.path.exists(file_path):
            basepath = os.path.basename(file_path)
            dirname = os.path.abspath(os.path.dirname(file_path))
            return send_from_directory(dirname, basepath)

        return {'message':
                {'path': 'File not found!'}}, 404

    def post(self):
        """Upload a file or file(s) to an arbitrary location

        Args:
          file or file[]: multipart/form file uploads
        """

        files_added = []
        if 'file' in request.files:
            f = request.files['file']
            handle_file(f, f.filename)
        elif 'file[]' in request.files:
            files = request.files.getlist('file[]')
            for i in files:
                result = handle_file(i, i.filename)
                files_added.append(result)
        else:
            return {'message': 'No files found.'}, 400

        return {'files': files_added}, 201


# Launching jobs and querying status
api.add_resource(Submission, '/submission')
api.add_resource(Status, '/submission/<string:job_id>')
# Uploading/downloading files over HTTP/S
api.add_resource(Files, '/files')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
