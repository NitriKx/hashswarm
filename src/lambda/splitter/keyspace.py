import shutil
import os
import subprocess
import logging


logger = logging.getLogger('KeyspaceCalculator')
logger.setLevel(logging.INFO)


class KeyspaceCalculator:

    _prepared = False

    def compute(self, hashtype, filepath, mask):
        if not self._prepared:
            self._prepare()
        command = f"./hashcat64.bin --hash-type={hashtype} -a3 --keyspace {mask}"
        logger.info(f"Executing command {command}...")
        popen = subprocess.Popen(command, cwd='/tmp/bin/', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        code = popen.wait()
        output = popen.stdout.read()
        error = popen.stderr.read()
        if code == 0:
            print(f"Success. Keyspace size is: {output.decode('UTF-8')}")
        else:
            print(output.decode('UTF-8'))
            print(error.decode('UTF-8'))

    def _prepare(self):
        os.makedirs("/tmp/bin", exist_ok=True)
        os.makedirs("/tmp/bin/OpenCL/", exist_ok=True)
        shutil.copy2("bin/hashcat64.bin", "/tmp/bin/hashcat64.bin")
        os.chmod("/tmp/bin/hashcat64.bin", 0o775)
        self._prepared = True

