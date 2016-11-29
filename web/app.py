from flask import Flask, send_from_directory, redirect, request
from flask_restful import Resource, Api, reqparse
import random
import os
import subprocess

UPLOAD_FOLDER = '/dev/shm'


app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def queue_job(command, files):
    job_id = int(random.random()*100)
    message = '"{job_id}","{command}","{files}"\n'.format(
        job_id=job_id,
        command=command,
        files=''.join(files))
    with open('jobs.txt', 'a') as f:
        f.write(message)
    return job_id


def run_job(command):
    code = subprocess.call(['qsub', command])
    return code


@app.route('/terminate', methods=['POST'])
def terminate():
    """Cleanly terminates the entire web service environment."""
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


class Submission(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        args = parser.parse_args()
        job_id = args.get('id', None)

        return {'id': job_id, 'status': 'queued'}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('command',
                            type=str,
                            required=True,
                            help='Command line to execute')
        parser.add_argument('files', type=str)
        args = parser.parse_args()

        command = args.get('command', None)

        file_list = request.files.getlist('file[]')
        filepaths = []

        for i in file_list:
            i.save(i.filename)
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
        parser = reqparse.RequestParser()
        parser.add_argument('path', type=str)

        args = parser.parse_args()
        file_path = args.get('path', None)

        if os.path.exists(file_path):
            basepath = os.path.basename(file_path)
            dirname = os.path.abspath(os.path.dirname(file_path))
            return send_from_directory(dirname, basepath)

        return {'message':
                {'path': 'File not found!'}}

    def post(self):
        if 'file' not in self.request.files:
            return redirect(self.request.url)
        dest_path = '/data/file'
        return {'file': dest_path}, 201


# Launching jobs and querying status
api.add_resource(Submission, '/submission')
# Uploading/downloading files over HTTP/S
api.add_resource(Files, '/files')

if __name__ == '__main__':
    app.run(debug=True)
