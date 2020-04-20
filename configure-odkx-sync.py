#! /usr/bin/env python3

"""An interactive script to configure ODK-X sync endpoint on first run.

This is a first attempt at a proof of concept script, and has no
support for internationalization.

"""

import time
import os

def run_interactive_config():
    env_file_location = os.path.join(os.path.dirname(__file__), "config", "https.env")

    try:
        domain, email = parse_env_file(env_file_location)
        print("Found configuration at {}".format(env_file_location))
    except OSError:
        print("No default https configuration file found at expected path {}. This prevents automatically renewing certs!".format(env_file_location))
        print("Please check your paths and file permissions, and make sure your config repo is up to date.")
        exit(1)

    print("Welcome to the ODK-X sync endpoint installation!")
    print("This script will guide you through setting up your installation")
    print("We'll need some information from you to get started though...")
    time.sleep(1)
    print("")
    print("Please input the domain name you will use for this installation. A valid domain name is required for HTTPS without distributing custom certificates.")
    input_domain = input("domain [({})]:".format(domain))

    if input_domain != "":
        domain = input_domain

    while True:
        print("Would you like to enforce HTTPS? We recommend yes.")
        enforce_https = input("enforce https [(Y)/n]:")
        if enforce_https == "":
            enforce_https = "y"
            enforce_https = enforce_https.lower().strip()[0]
        if enforce_https in ["y", "n"]:
            break

    if enforce_https == "n":
        print("Would you like to run an INSECURE and DANGEROUS server that will share your users's information if exposed to the Internet?")
        insecure = input("run insecure [y/(N)]:")
        if insecure == "":
            insecure = "n"
        if insecure.lower().strip()[0] != "y":
            raise RuntimeError("HTTPS is currently required to run a secure public server. Please restart and select to enforce HTTPS")

    print("Enforcing https:", enforce_https)
    if enforce_https == "y":
        print("Please provide an admin email for security updates with HTTPS registration")
        input_email = input("admin email [({})]:".format(email))

        if input_email != "":
            email = input_email

        print("The system will now attempt to setup an HTTPS certificate for this server.")
        print("For this to work you must have already have purchased/acquired a domain name (or subdomain) and setup a DNS A or AAAA record to point at this server's IP address.")
        print("If you have not done this yet, please do it now...")
        time.sleep(1)
        proceed = input("Domain is ready to proceed with certificate acquisition? [(Y)/n]")
        if proceed == "":
            proceed = "y"
        if proceed.strip().lower()[0] != "y":
            print("Re-run this script once the domain is ready!")
            exit(1)

        os.system("sudo certbot certonly --standalone \
          --email {} \
          -d {} \
          --rsa-key-size 4096 \
          --agree-tos \
          --cert-name bootstrap \
          --keep-until-expiring \
          --non-interactive".format(email, domain))

        print("Attempting to save updated https configuration")
        write_to_env_file(env_file_location, domain, email)


def write_to_env_file(filepath, domain_name, email):
    """A janky in-memory file write.

    This is not atomic and would use lots of ram for large files.
    """
    file_lines = []
    with open(filepath, mode="r") as f:
        for line in f:
            file_lines.append(line)

    with open(filepath, mode="w") as f:
        for line in file_lines:
            if line.startswith("HTTPS_DOMAIN="):
                line = "HTTPS_DOMAIN={}\n".format(domain_name)
            if line.startswith("HTTPS_ADMIN_EMAIL="):
                line = "HTTPS_ADMIN_EMAIL={}\n".format(email)
            f.write(line)


def parse_env_file(filepath):
    domain = None
    email = None
    with open(filepath) as f:
        for line in f:
            if line.startswith("HTTPS_DOMAIN="):
                domain=line[13:].strip()
            if line.startswith("HTTPS_ADMIN_EMAIL="):
                email=line[18:].strip()
    return (domain,email)


if __name__ == "__main__":
    run_interactive_config()
