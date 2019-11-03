import boto3
import requests
import json
import logging


logPath = "/var/log/hashswarm"
filename = "hashswarm.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, filename)),
        logging.StreamHandler()
    ])
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)


sqs = boto3.client('sqs')


class HashSwarmWrapper:

    def __init__(self):
        self.userdata = self.__get_userdata()
        self.queue_url = self.userdata['HASHSWARM_QUEUE_URL']

    def run(self):
        while True:
            job = self._wait_for_job()
            self._process(job)

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
                body = json.loads(response['Messages'][0]['Body'])
                logger.info(f'Received job {body}')
                return body

    def _process(self, job):
        # Buld the command line to execute
        command = ["/opt/hashcat/"]

    @staticmethod
    def __get_userdata():
        r = requests.get("http://169.254.169.254/latest/user-data")
        userdata = r.json()
        logger.debug(f"Found userdata: {json.dumps(userdata)}")
        return userdata


def main():
    HashSwarmWrapper().run()


if __name__ == "__main__":
    main()
