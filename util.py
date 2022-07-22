from config import creds


def clientSecretID():
    return creds["clientID"], creds["secretID"]
