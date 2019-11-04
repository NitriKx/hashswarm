import os
from tempfile import TemporaryDirectory

import boto3
import requests
import json
import logging
import subprocess


logPath = "/var/log/hashswarm"
filename = "hashswarm.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}".format(logPath, filename)),
        logging.StreamHandler()
    ])
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)

hashcatlogger = logging.getLogger('hashcat')
hashcatlogger.setLevel(logging.INFO)

sqs = boto3.client('sqs')


class HashSwarmWrapper:

    def __init__(self):
        self.userdata = self.__get_userdata()
        self.job_file_bucket = self.userdata['HASHSWARM_JOB_FILE_BUCKET']
        self.queue_url = self.userdata['HASHSWARM_QUEUE_URL']

    def run(self):
        while True:
            try:
                message = self._wait_for_job()
                job = json.loads(message['Body'])
                logger.info(f"Received HashSwarm job: {message['Body']}")

                try:
                    self._process(job)
                    self.__delete_message(self.queue_url, message['ReceiptHandle'])
                except:
                    logger.exception(f"An error occurred while processing: {message['Body']}")
            except:
                logger.exception(f"Could not receive/parse the next job")

    def _wait_for_job(self):
        while True:
            response = sqs.receive_message(
                QueueUrl=self.queue_url,
                AttributeNames=['SentTimestamp'],
                MaxNumberOfMessages=1,
                MessageAttributeNames=['All'],
                WaitTimeSeconds=20
            )

            if response['Messages'] and len(response['Messages']) > 0:
                return response['Messages'][0]

    def _process(self, job):
        # Check if the job needs file
        file_path = None
        # If the job need a file (pcap, hash...)
        file_s3_key = job.get('file_s3_key', None)
        if file_s3_key:
            tempfolder = TemporaryDirectory(suffix='.tmp', prefix="hashswarm")
            s3 = boto3.client('s3')
            file_path = f"{tempfolder}/jobfile"
            s3.download_file(self.job_file_bucket, file_s3_key, file_path)

        # Build the command line with the job parameters
        skip = job.get('skip')
        limit = job.get('limit')
        command = ["/opt/hashcat/hashcat64.bin", "-s", skip, "-l", limit]

        # Append the custom parameters
        custom_parameters = job.get('custom_parameters')
        if custom_parameters:
            command = command + custom_parameters

        # Append the file
        command = command + [file_path]

        # Execute the command line
        logger.info(f"Executing HashCat: {' '.join(command)}")
        self.__execute_command(command)

        # Delete the temporary file
        os.remove(file_path)

    @staticmethod
    def __execute_command(command):
        popen = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            logger.info(stdout_line)
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)

    @staticmethod
    def __delete_message(queue_url, msg_receipt_handle):
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg_receipt_handle)

    @staticmethod
    def __get_userdata():
        r = requests.get("http://169.254.169.254/latest/user-data")
        userdata = r.json()
        logger.debug(f"Found userdata: {json.dumps(userdata)}")
        return userdata


def main():
    logger.info("Starting hashswarm wrapper...")
    HashSwarmWrapper().run()


if __name__ == "__main__":
    main()
