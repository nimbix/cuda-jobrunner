# Copyright (c) 2016, Nimbix, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nimbix, Inc.

from flask import Flask, send_from_directory, request
from flask_restful import Resource, Api, reqparse

import os
import subprocess
import logging
import uuid
import sys

# Configure logging
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


def queue_job(command, files, gpus=None):
    """Queues a task using an interface to the job runner.

    Args:
      command(str): Command to execute. Assumes /bin/bash shell.
      files(str): Absolute paths to files
      gpus(int): The number of GPUs required for this task.
    """
    job_id, error = SlurmInterface.submit(command, gpus)

    message = '"{job_id}","{command}","{files}"\n'.format(
        job_id=job_id,
        command=command,
        files=''.join(files))
    logger.info(message)

    return job_id, error


def handle_file(file_t, destination):
    """Saves file_t to the destination.

    This saves any input file to any destination path.

    Args:
      file_t: Uploaded file object
      destination(str): Destination path. Can be any path.
    """
    file_t.save(destination)
    return destination


def validate_path(path):
    """Validates that the given path is an absolute path by validating
    that the first character is a '/'

    Args:
      path(str): Path

    Returns:
      boolean (Valid, True)
    """
    if path[0] != '/':
        return False, 'Path must be absolute path beginning with /'

    return True


def parse_acct_jobs(raw_output, internal=False):
    """Helper function to parse the output of Slurm sacct command

    Args:
      raw_output(str): Raw std output of the Slurm sacct command

    Returns: Dict of key: job-dict pairs. The primary key is the
      job_id. The data structure contained is:
        {'id': '<job uuid>',
         'status': '<completion status>',
         'internal_id': '<task runner's number>'}
    """
    lines = raw_output.split('\n')
    jobs = {}
    for row in lines:
        row_items = row.split('|')
        if len(row_items) >= 7 and len(row_items[0].split('.')) == 1:
            job_id = row_items[1]
            internal_id = row_items[0]
            status = row_items[5]
            job = {'id': job_id,
                   'status': status}
            if internal:
                job.update({'internal_id': internal_id})
            jobs.update({job_id: job})

    return jobs


class SlurmInterface(object):
    template = '#!/bin/bash\n' \
               '#SBATCH -e /tmp/{job_id}.err -o /tmp/{job_id}.out\n' \
               '{extra_options}\n' \
               '/opt/slurm/bin/srun ' \
               '/usr/local/scripts/jarvice_env.sh {command}\n'

    @classmethod
    def get_job_status(cls, job_name):
        job_status = 'placeholder'
        job_output = 'path-to-output'
        raise
        return {'id': job_name,
                'status': job_status,
                'output': job_output}

    @classmethod
    def get_all_jobs(cls):
        queued = cls.get_queued_jobs()
        not_queued = cls.get_acct_jobs()
        jobs = queued.copy()
        jobs.update(not_queued)
        return jobs

    @classmethod
    def get_acct_jobs(cls, internal=False):
        """Use sacct command to query all jobs that are running or
        ending

        Args:
          internal: Whether to include the internal SLURM job identifier
                    which must be used for some commands like scancel.

        Returns:
          dict: Dict of {
            key(job_id):
               {'id': job_id, 'status': ..., 'internal_id'}}
        """
        try:
            output = subprocess.check_output(
                ['/opt/slurm/bin/sacct', '-a', '-p', '-n'])
        except subprocess.CalledProcessError:
            logger.exception('Failure to get jobs from job interface.')
            return {}
        return parse_acct_jobs(output)

    @classmethod
    def get_queued_jobs(cls):
        # Query output in form of:
        # JOBID,NAME,STATE
        output = subprocess.check_output(
            ['/opt/slurm/bin/squeue',
             '-t', 'PENDING',
             '-h',
             '-o', '%i,%j,%T'])
        lines = output.split('\n')
        jobs = {}
        for line in lines:
            cols = line.split(',')
            if len(cols) >= 3:
                internal_id = cols[0]
                job_id = cols[1]
                status = cols[2]
                jobs.update({
                    job_id: {
                        'id': job_id,
                        'internal_id': internal_id,
                        'status': status
                    }})
        return jobs

    @classmethod
    def submit(cls, command, gpus=None):
        """Submit a job to SLURM using sbatch

        Args:
          command: The command to execute
          gpus: The number of GPUs requested by the job
        """
        job_id = str(uuid.uuid4())
        error = None
        extra_options = ''
        if gpus:
            extra_options += '#SBATCH --gres=gpu:{gpu_count}\n'.format(
                gpu_count=str(gpus))

        job_script = '/tmp/{job_id}.sh'.format(job_id=job_id)
        with open(job_script, 'wb') as f:
            f.write(cls.template.format(job_id=job_id,
                                        extra_options=extra_options,
                                        command=command))

        try:
            subprocess.check_call(['/opt/slurm/bin/sbatch',
                                   '-J', job_id,
                                   job_script])
        except subprocess.CalledProcessError:
            error = 'Failure to launch job'
        return job_id, error

    @classmethod
    def cancel(cls, job_id=None, internal_id=None):

        if job_id:
            subprocess.call(['/opt/slurm/bin/scancel',
                             '-n', '{job_id}'.format(job_id=job_id)])
            return {'job_id': job_id,
                    'message': 'Caceling job'}, 202
        return {'message': 'Job not found'}, 404


class Jobs(Resource):
    """List and create jobs

     - GET: Query a list of jobs
     - POST: Submit a job
    """
    def get(self):
        """Query list of jobs"""
        jobs = SlurmInterface.get_all_jobs()
        jobs_response = {
            'count': len(jobs),
            'data': jobs
        }
        return jobs_response, 200

    def post(self):
        """Submit a job

        Args:
          command: A bash command to execute.
          file[](optional): One or more files to upload, with identifier as the
                            destination.
          gpus: The minimum number of GPUs requested for this job.
        """
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
            path = handle_file(i, i.filename)
            filepaths.append(path)

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
    """
    Interact with individual jobs, identified by its Job ID

     - GET: Queries status
     - DELETE: Cancels if running or queued
    """
    def _get_acct_jobs(self, internal=False):
        return SlurmInterface.get_acct_jobs(internal)

    def _get_internal_id_from_job_name(self, job_id):
        jobs = self._get_acct_jobs(internal=True)
        jobs_dict = dict(jobs)
        if job_id in jobs_dict.keys():
            return jobs_dict[job_id]['internal_id']
        return None

    def get(self, job_id):
        """Get status of a submitted job"""
        jobs = self._get_acct_jobs()
        job = jobs.get(job_id, None)
        if job is not None:
            job.pop('internal_id', None)
            return job
        return {'message': 'Job id {job_id} not found!'.format(
            job_id=job_id)}, 404

    def delete(self, job_id):
        """Cancel a queued or running job"""
        internal_job_id = self._get_internal_id_from_job_name(job_id)
        if internal_job_id:
            SlurmInterface.cancel(job_id=job_id)
            return {'job_id': job_id,
                    'message': 'Canceling job'}, 202
        return {'message': 'Job not found'}, 404


class Files(Resource):
    """Static file REST endpoint. Note that all files that are not stored
    in /data will not be persisted when this environment is terminated.

     - GET: Download a file
     - POST: Upload a file
     - DELETE: Delete a file
    """
    def _validate_path(self, path):
        if path[0] != '/':
            return False, 'Path must be absolute beginning with /'
        return True, None

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
                {'path': 'File not found.'}}, 404

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

    def delete(self):
        """Removes a file or directory

        Args:
          path: Absolute path to file or directory to remove
        """
        parser = reqparse.RequestParser()
        parser.add_argument('path', type=str)

        args = parser.parse_args(strict=True)
        file_path = args.path('path', None)

        is_valid, message = validate_path(file_path)
        if not is_valid:
            return {'message': {'path': message}}, 400

        if os.path.exists(file_path):
            try:
                if not os.path.isdir(file_path):
                    os.remove(file_path)
                else:
                    os.rmdir(file_path)
            except Exception:
                return {'message': 'Unexpected failure removing file'}, 500
            return {
                'message': 'Removing {file_path}'.format(
                    file_path=file_path)
            }, 200
        else:
            return {'message':
                    {'path': 'File not found.'}}, 404


class Output(Resource):

    def get(self, job_id):
        """Returns stdout from job

        Args:
          job_id: job_id for queried job
        """
        # TODO: Look up Standard out via slurm rather than using this
        # as the default location.
        output_path = '/tmp/{job_id}.out'.format(job_id=job_id)
        if os.path.exists(output_path):
            return send_from_directory('/tmp', '{job_id}.out'.format(
                job_id=job_id))
        else:
            return {'id': '{job_id}'.format(job_id=job_id),
                    'message': 'Job output not found. Is it running?'}, 404


# Launching jobs and querying status
api.add_resource(Jobs, '/jobs')
api.add_resource(JobControl, '/jobs/<job_id>')
api.add_resource(Output, '/output/<job_id>')


# Uploading/downloading files over HTTP(S)
api.add_resource(Files, '/files')

if __name__ == '__main__':
    if not os.path.exists('/opt/slurm/bin') or not \
       os.path.exists('/opt/slurm/sbin'):
        logger.critical(
            'SLURM could not be found in this environment. Exiting')
        sys.exit(1)
    app.run(host='0.0.0.0', debug=True)
