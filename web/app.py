from flask import Flask, send_from_directory, request
from flask_restful import Resource, Api, reqparse
import os
import subprocess
import logging
import uuid
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(name)s %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = '/data'


app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

template = '#!/bin/bash\n' \
           '#SBATCH -e /tmp/{job_id}.err -o /tmp/{job_id}.out\n' \
           '{extra_options}\n' \
           '/opt/slurm/bin/srun /usr/local/scripts/jarvice_env.sh {command}\n'


def queue_job(command, files, gpus=None):
    job_id = str(uuid.uuid4())
    error = None
    extra_options = ''

    if gpus:
        cpus = 4*gpus
        extra_options += '#SBATCH --gres=gpu:{gpu_count}\n' \
                         '#SBATCH -n {cpus}\n'.format(
                             gpu_count=str(gpus), cpus=cpus)
    message = '"{job_id}","{command}","{files}"\n'.format(
        job_id=job_id,
        command=command,
        files=''.join(files))
    logger.info(message)
    job_script = '/tmp/{job_id}.sh'.format(job_id=job_id)
    with open(job_script, 'wb') as f:
        f.write(template.format(job_id=job_id,
                                extra_options=extra_options,
                                command=command))
    try:
        subprocess.check_call(['/opt/slurm/bin/sbatch',
                               '-J', job_id,
                               job_script])
    except subprocess.CalledProcessError:
        error = 'Failure to launch job'
    return job_id, error


def handle_file(file_t, destination):
    file_t.save(destination)
    return destination


class Jobs(Resource):

    def get(self):
        output = subprocess.check_output(['/opt/slurm/bin/sacct', '-p', '-a'])
        jobs = []
        lines = output.split('\n')
        for i in lines:
            cols = i.split('|')
            jobs.append({
                'internal_id': cols[0],
                'job_id': cols[1]})
        jobs_response = {
            'count': len(jobs),
            'data': jobs
        }
        return jobs, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('command',
                            type=str,
                            required=True,
                            help='Command line to execute')
        parser.add_argument('files', type=str)
        parser.add_argument('gpus', type=int)
        args = parser.parse_args(strict=True)

        command = args.get('command', None)
        gpus = args.get('gpus', None)

        file_list = request.files.getlist('file[]')
        filepaths = []

        for i in file_list:
            handle_file(i, i.filename)
            filepaths.append(i.filename)

        # Post asynchronously
        job_id, error = queue_job(command, filepaths, gpus)

        if not error:
            result = {
                'id': job_id,
                'command': command,
                'files': ';'.join(filepaths)
            }
            if gpus:
                result.update({'gpus': gpus})
            return result, 201
        else:
            return {'message': error}, 500


class JobControl(Resource):

    def get(self, job_id):
        return {'job_id': job_id}

    def delete(self, job_id):
        return {'job_id': job_id}


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
          200 Directory listing returned for download
              {'count': <int>,
               'files': list<str>}
          404 File not found
        """
        parser = reqparse.RequestParser()
        parser.add_argument('path', type=str)
        args = parser.parse_args(strict=True)
        file_path = args.get('path', None)

        if os.path.exists(file_path):
            if not os.path.isdir(file_path):
                basepath = os.path.basename(file_path)
                dirname = os.path.abspath(os.path.dirname(file_path))
                return send_from_directory(dirname, basepath)
            else:
                files = os.listdir(file_path)
                return {'count': len(files),
                        'data': files}, 200

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
api.add_resource(Jobs, '/jobs')
api.add_resource(JobControl, '/jobs/<job_id>')

# Uploading/downloading files over HTTP/S
api.add_resource(Files, '/files')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
