import argparse
import ConfigParser
import logging
from ZmPublish import ZmPublish


if __name__ == '__main__':

    # Parse arguments

    parser = argparse.ArgumentParser(
        description='Publish Zimbra addressbooks to a LDAP-Server'
    )

    parser.add_argument(
        "-c, --config",
        metavar='zmpublish.cfg',
        help="ZmPublish configuration file",
        dest="config",
        required=True

    )

    parser.add_argument(
        "-v",
        help="Increase verbosity",
        dest="verbose"
    )

    args = parser.parse_args()

    # Translate verbosity setting to loglevel

    logging_level = logging.ERROR

    if args.verbose != None:
        if len(args.verbose) > 5:
            args.verbose = "vvvvv"

        logging_level = 70 - ((len(args.verbose) + 1) * 10)

    logging.basicConfig(level=logging_level)

    logging.debug("Parsed arguments and set logging level.")

    # Load configuration

    logging.info("Reading configuration")

    config = ConfigParser.ConfigParser()
    config.readfp(open(args.config))

    logging.debug("Read configuration")

    # Build ZmPublish

    logging.debug("Instantiating ZmPublish object")

    my_publisher = ZmPublish.ZmPublish(config)

    # Run ZmPublish

    logging.info("Starting ZmPublish")

    my_publisher.run()

    logging.info("ZmPublish finished")
