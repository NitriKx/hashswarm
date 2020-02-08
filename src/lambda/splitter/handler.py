from keyspace import KeyspaceCalculator


def handler(event, context):
    calculator = KeyspaceCalculator()
    calculator.compute("2500", "/var/task/handshakes/Livebox-A196.hccapx", "?a?a?a?a?a?a?a?a")