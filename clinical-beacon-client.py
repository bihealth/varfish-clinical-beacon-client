#!/usr/bin/env python3

import argparse
import logging
import json
import sys

from Crypto.PublicKey import RSA
import logzero
from logzero import logger
import requests
from requests_http_signature import HTTPSignatureAuth


def run_gen_key(args):
    logger.info("Generating public/private key pair...")
    logger.info("  public key:  %s", args.key_file)

    key = RSA.generate(args.key_length)
    with open(args.key_file, "wb") as f:
        f.write(key.export_key("PEM"))

    logger.info("  private key: %s.pub", args.key_file)

    with open("%s.pub" % args.key_file, "wb") as f:
        f.write(key.public_key().export_key("PEM"))

    logger.info("... done generating key pair.")
    logger.info("Have a nice day!")


def run_query(args):
    while args.endpoint.endswith("/"):
        args.endpoint = args.endpoint[:-1]
    if args.variant:
        logger.info("Executing query for %s...", args.variant)
        url = "%s/query" % args.endpoint
        chrom, pos, ref, alt = args.variant.split("-")
        params = {
            "assemblyId": "GRCh37",
            "referenceName": chrom,
            "start": pos,
            "referenceBases": ref,
            "alternateBases": alt,
        }
    else:
        logger.info("Asking beacon for info...")
        url = "%s/" % args.endpoint
        params = None

    with open(args.key_file, "rb") as keyf:
        key = keyf.read()

    headers = {"X-Beacon-User": args.beacon_user}

    r = requests.get(
        url,
        headers=headers,
        params=params,
        auth=HTTPSignatureAuth(
            algorithm="rsa-sha256",
            key=key,
            key_id=args.key_id,
            headers=["date", "x-beacon-user"],
        ),
    )

    if r.ok:
        logger.info("=> OK %s", r.status_code)
        logger.info("result below on stdout --8<-- --8<-- --8<--")
        print(json.dumps(r.json(), indent=2))
        logger.info("-->8-- -->8-- -->8-- result above on stdout")
    else:
        logger.info("=> ERROR: %s (%s)", r.status_code, r.reason)
        try:
            data = json.dumps(r.json(), indent=2)
            logger.info("details below on stdout --8<-- --8<-- --8<--")
            print(data)
            logger.info("-->8-- -->8-- -->8-- details above on stdout")
        except:
            pass  # swallow

    if args.variant:
        logger.info("... done executing query.")
    else:
        logger.info("... done asking beacon for info.")
    logger.info("Have a nice day!")


def main(argv=None):
    logzero.loglevel(logging.INFO)

    parser = argparse.ArgumentParser(description="Clinical Beacon Client")
    subparsers = parser.add_subparsers(title="subcommands")

    parser_gen_key = subparsers.add_parser("gen-key", help="Create public/private key pair")
    parser_gen_key.set_defaults(func=run_gen_key)
    parser_gen_key.add_argument(
        "--key-length",
        type=int,
        default=2048,
        help="Optional key length to set.",
    )
    parser_gen_key.add_argument(
        "--key-file", help="Path to private key output file", default="key_rsa"
    )

    parser_query = subparsers.add_parser("query", help="Run query")
    parser_query.set_defaults(func=run_query)
    parser_query.add_argument(
        "--key-file", help="Path to private key output file", default="key_rsa"
    )
    parser_query.add_argument(
        "--key-id",
        help="Name of the source site to end as (keyId).",
        required=True,
    )
    parser_query.add_argument(
        "--beacon-user",
        help="String to use as the X-Beacon-User header value.",
        required=True,
    )
    parser_query.add_argument("--endpoint", help="Remote endpoint URL.", required=True)
    parser_query.add_argument(
        "--variant",
        help=(
            "Variant as CHROM-POS-REF-ALT.  If not specified then "
            "the beacon information is queried for."
        ),
    )
    parser_query.set_defaults(func=run_query)

    args = parser.parse_args((argv or [])[1:])
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    else:
        args.func(args)
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
