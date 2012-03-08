ZmPublish
=========

Publish Zimbra addressbooks on a LDAP server.

This tool fetches Zimbra addressbooks via SOAP/JSON from a Zimbra server and 
publishes them on a specified branch on a LDAP server.

How it works
============

ZmPublish connects via PreAuth to the Zimbra server and fetches the specified
addressbook using the SOAP protocol using JSON format. (GetContactsRequest is
used to be precise)

The resulting addressbook will be used by a LDAP publisher, that connects
to the ldap-server and fills the specified branch with the addresses from
the addressbook.

There's no merging or synchronisation features, so the corresponding branch
on the ldap-server will simply be dropped and recreated. You can also turn
off the drop action, so that you can even configure nested ldap branches, 
though this is not recommended.

The LDAP branch will be added as a organizational unit "ou".

Every addressbook entry will be added using a "uid"-attribute containing a 
continous number starting at 0. ("uid=0,ou=...", "uid=1,ou=...", etc.)

Prerequisites
=============

  - Python v2.7 (http://www.python.org)
  - python-ldap (http://www.python-ldap.org)
  - Zimbra Network Edition or Community Edition v6 or 
    later (http://www.zimbra.com)
  - Configured PreAuth for domains (see http://wiki.zimbra.com/wiki/Preauth)
 
Configuration
=============

Configuration is done in the file **zmpublish.cfg** located in the application
directory.

Every workflow "Fetch Addressbook", "Publish to LDAP-Server" is called a
"Publisher" and is configured by using the section name [Publisher<id>] with
a id starting at 0.

Inside the publisher the following options need to be configured:

  - **name**: Name of organizational unit in the LDAP tree
  - **server_url**: Zimbra-Server-URL (without /service/soap)
  - **domain**: Domain of the account, that holds the addressbook
  - **preauth**: PreAuth-Key for the specific domain
  - **account**: Name of account, that holds the addressbook
  - **addressbook_name**: Name of the addressbook in Zimbra
  - **ldap_url**: LDAP-URL of the ldap-server
  - **base_dn**: Base DN, where the new organizational unit with the addressbook
    will reside
  - **bind_uid**: UID to bind to the ldap-server with
  - **bind_pw**: Password for the bind
  - **drop**: 0 - skip dropping the ldap branch, 1 - drop the branch before
    filling it

Running it
==========

Run the application by starting it in a python interpreter and specifying your
configuration file and (optionally) a verbosity level:

python zmpublish.py -c zmpublish.cfg

To generate debugging output, specify many v's:

python zmpublish.py -c zmpublish.cfg -vvvvvvv