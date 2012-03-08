import logging
from time import time
import hmac
import hashlib
import urllib
import json


class ZimbraRetriever:
    """
    Retrieves an Addressbook from Zimbra
    """

    config = None
    """ Retriever configuration """

    addressbook = None
    """ Retrieved Addressbook """

    def __init__(self, config):
        """ Initialize Retriever """

        self.config = config

        logging.debug("Initialised Retriever for %s" % (self.config["name"]))

    def run(self):
        """ Retrieve the addressbook """

        logging.info(
            "Retrieving addressbook %s of user %s" % (
                self.config["addressbook_name"],
                self.config["account"]
            )
        )

        # Do preauth

        timestamp = int(time() * 1000)

        preauth_key = hmac.new(
            self.config["preauth"],
            '%s|name|0|%s' % (self.config["account"], timestamp),
            hashlib.sha1
        ).hexdigest()

        data_to_send = {
            "Header": {},
            "Body": {
                "AuthRequest": {
                    "_jsns": "urn:zimbraAccount",
                    "account": {
                        "by": "name",
                        "_content": self.config["account"]
                    },
                    "preauth": {
                        "timestamp": timestamp,
                        "expires": 0,
                        "_content": preauth_key
                    }
                }
            }
        }

        returned_data = self.send_to_zimbra(data_to_send)

        preauth_token = \
            returned_data["Body"]["AuthResponse"]["authToken"][0]["_content"]

        logging.debug("Received preauth token %s" % (preauth_token))

        zimbra_header = {
            "Header": {
                "context": {
                    "_jsns": "urn:zimbra",
                    "authToken": {
                        "_content": preauth_token
                    }
                }
            }
        }

        data_to_send = zimbra_header

        data_to_send["Body"] = {
            "GetFolderRequest": {
                "_jsns": "urn:zimbraMail",
                "folder": {
                    "path": "/%s" % (self.config["addressbook_name"])
                }
            }
        }

        returned_data = self.send_to_zimbra(data_to_send)

        folder_id = \
            returned_data["Body"]["GetFolderResponse"]["folder"][0]["id"]

        logging.debug("Folder %s has id %s" %
            (
                self.config["addressbook_name"],
                folder_id
            )
        )

        data_to_send = zimbra_header

        data_to_send["Body"] = {
            "GetContactsRequest": {
                "_jsns": "urn:zimbraMail",
                "l": folder_id,
            }
        }

        returned_data = self.send_to_zimbra(data_to_send)

        if "cn" in returned_data["Body"]["GetContactsResponse"]:

            self.addressbook = \
                returned_data["Body"]["GetContactsResponse"]["cn"]

        else:

            self.addressbook = []

    def send_to_zimbra(self, data_to_send):
        """ Send a request to zimbra """

        data_to_send_json = json.dumps(data_to_send)

        logging.debug("Sending request: %s" % (data_to_send_json))

        zimbra_connect = urllib.urlopen(
            "%s/service/soap" % self.config["server_url"],
            data_to_send_json,
            {}
        )

        returned_data = zimbra_connect.readlines()

        logging.debug("Received response: %s" % (returned_data))

        zimbra_connect.close()

        return json.loads(returned_data[0])
