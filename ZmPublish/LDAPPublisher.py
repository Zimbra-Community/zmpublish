import logging
import ldap
import re


class LDAPPublisher:

    """
    Publish a Zimbra addressbook to a LDAP server
    """

    addressbook = None
    """ Zimbra Addressbook to publish """

    config = None
    """ Publisher configuration """

    attribute_map = {

        "cn": "fileAsStr",
        "sn": "_attrs/lastName",
        "givenname": "_attrs/firstName",
        "street": "_attrs/workStreet",
        "l": "_attrs/workCity",
        "st": "_attrs/workState",
        "postalCode": "_attrs/workPostalCode",
        "telephoneNumber": "_attrs/workPhone",
        "facsimileTelephoneNumber": "_attrs/workFax",
        "mobile": "_attrs/mobilePhone",
        "mail": "_attrs/email",
        "labeleduri": "_attrs/workURL",
        "o": "_attrs/company",
        "ou": "_attrs/department",
        "description": "_attrs/notes"

    }
    """ Attribute Map Zimbra <> LDAP """

    ldap_connect = None
    """ LDAP-Connection used by the publisher """

    mandatory_attributes = ["cn", "sn"]
    """ Mandatory LDAP attributes """

    attribute_alternatives = {
        "sn": "o",
        "sn": "cn"
    }
    """ Alternatives for specific attributes if empty """

    log_attribute = "cn"
    """ Attribute to use when logging """

    def __init__(self, config, addressbook):
        """ Initialize Publisher """

        self.addressbook = addressbook
        self.config = config

        logging.debug("Initialised Publisher %s" % (self.config["name"]))

    def drop_tree(self, dn):
        """ Recursively drop a LDAP tree """

        logging.debug("Deleting dn %s" % (dn))

        result = self.ldap_connect.search_s(
            dn,
            ldap.SCOPE_ONELEVEL  # @UndefinedVariable
        )

        if len(result) > 0:
            for leaf in result:
                self.drop_tree(leaf[0])

        self.ldap_connect.delete_s(dn)

    def run(self):
        """ Publish the addressbook """

        # Bind to ldap

        self.ldap_connect = ldap.initialize(self.config["ldap_url"])
        self.ldap_connect.simple_bind_s(
            self.config["bind_uid"],
            self.config["bind_pw"],
        )

        logging.debug("Connected to LDAP-Server %s as user %s" %
            (
                self.config["ldap_url"],
                self.config["bind_uid"]
            )
        )

        ldap_dn = "ou=%s,%s" % (self.config["name"], self.config["base_dn"])

        # Find our branch

        result = self.ldap_connect.search_s(
            self.config["base_dn"],
            ldap.SCOPE_SUBTREE, # @UndefinedVariable
            "ou=%s" % (self.config["name"])
        )

        if len(result) > 0 and self.config["drop"] == "1":

            # Branch exists, but needs to be recreated

            logging.info("Dropping branch %s" % (ldap_dn))

            self.drop_tree(ldap_dn)

        if (len(result) == 0) or (
            len(result) > 0 and self.config["drop"] == "1"
        ):

            # Branch doesn't exists or is recently dropped. Recreate!

            add_data = [
                ("objectclass", ["top", "organizationalUnit"]),
                ("ou", [self.config["name"]])
            ]

            logging.info("Recreating tree %s" % (ldap_dn))

            self.ldap_connect.add_s(ldap_dn, add_data)

        uid = 0

        for address in self.addressbook:

            current_item = ""

            converted_addressbook = {}

            for attribute in self.attribute_map:

                matched_attribute = re.search(
                    "_attrs/(.*)",
                    self.attribute_map[attribute]
                )

                if matched_attribute != None:

                    if matched_attribute.group(1) in address["_attrs"]:

                        attribute_value = \
                            address["_attrs"][matched_attribute.group(1)]

                    else:

                        attribute_value = ""

                else:
                    attribute_value = address[self.attribute_map[attribute]]

                    if (self.attribute_map[attribute] in address):

                        attribute_value = \
                            address[self.attribute_map[attribute]]

                    else:
                        attribute_value = ""

                if attribute == self.log_attribute:

                    current_item = attribute_value

                try:
                    ldap_value = attribute_value.encode('ascii')
                except UnicodeEncodeError:
                    ldap_value = attribute_value.encode('utf-8')

                converted_addressbook[attribute] = ldap_value

            # Apply alternatives

            for attribute in self.attribute_alternatives:

                alternate_attribute = self.attribute_alternatives[attribute]

                if converted_addressbook[attribute] == "" and\
                    converted_addressbook[alternate_attribute] != "":

                    converted_addressbook[attribute] = \
                        converted_addressbook[alternate_attribute]

            sanity_checked = True

            for attribute in self.mandatory_attributes:

                if converted_addressbook[attribute] == "":

                    sanity_checked = False

            if sanity_checked:

                logging.info("Adding entry %s" % (current_item))

                add_data = [
                    ("objectClass", [
                        'top',
                        'person',
                        'organizationalperson',
                        'inetorgperson'
                    ])
                ]

                for entry in converted_addressbook:

                    if converted_addressbook[entry] != "":

                        add_data.append(
                            (
                                entry,
                                [converted_addressbook[entry]]
                            )
                        )

                dn = "uid=%d,%s" % (uid, ldap_dn)

                logging.debug(
                    "Adding entry at dn %s with the following data:\n %s" % (
                        dn,
                        add_data
                    )
                )

                self.ldap_connect.add_s(dn, add_data)

                uid = uid + 1
