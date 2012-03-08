import logging
from ZimbraRetriever import ZimbraRetriever
from LDAPPublisher import LDAPPublisher


class ZmPublish:

    """
    Publishes Zimbra addressbooks to a LDAP server.

    @author: Dennis Ploeger <develop@dieploegers.de>
    """

    config = None
    """ZmPublish configuration"""

    publisher_count = None
    """Count of configured publishers"""

    def __init__(self, config):

        """Initialize ZmPublish"""

        self.config = config

    def run(self):

        """Run the publishing work"""

        logging.debug("ZmPublish started")

        # Find out number of publishers

        self.publisher_count = 0

        while self.config.has_section("Publish%d" % (self.publisher_count)):
            self.publisher_count = self.publisher_count + 1

        for current_publisher in range(0, self.publisher_count):

            publisher_name = "Publish%d" % (current_publisher)

            publisher_config = {}

            for config_line in self.config.items(publisher_name):
                publisher_config[config_line[0]] = config_line[1]

            # Fetch Addressbook

            my_retriever = ZimbraRetriever(publisher_config)

            my_retriever.run()

            # Publish to LDAP

            my_publisher = LDAPPublisher(
                publisher_config,
                my_retriever.addressbook
            )

            my_publisher.run()

            # 
