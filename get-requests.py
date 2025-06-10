#!/usr/bin/python3
#

import requests
import json
import os
from dotenv import load_dotenv

# Sectigo crendentials should go in .env as environment variables
# This keeps them from potentially being uploaded to github

load_dotenv()

sectigo_custUri = os.getenv("sectigo_custUri")
sectigo_username = os.getenv("sectigo_user")
sectigo_password = os.getenv("sectigo_pw")
sectigo_orgID = os.getenv("sectigo_orgID")

headers = {
    'login': sectigo_username,
    'password': sectigo_password,
    'customerUri': sectigo_custUri,
    'Accept': 'application/json'
}

url = f"https://cert-manager.com/api/ssl/v1?size=50&position=0&status=Requested&requestedVia=WEB_FORM"
requested_list = requests.get(url, headers=headers)

if requested_list.status_code == 200:

    if int(requested_list.headers['X-Total-Count']) > 0:
        cert_requests = requested_list.json()

        for cert in cert_requests:
            sslID = cert['sslId']

            get_url = f"https://cert-manager.com/api/ssl/v1/{sslID}"
            detail_req = requests.get(get_url, headers=headers)

            details = detail_req.json()
            commonName = details['commonName']
            status = details['status']
            certType = details['certType']
            profile_id = certType['id']
            profile_name = certType['name']

            print(f"\nRequest: {sslID} - {commonName} {status} with profile {profile_name} ({profile_id})")

            existing_url = f"https://cert-manager.com/api/ssl/v1?status=Issued&commonName={commonName}"
            list_req = requests.get(existing_url, headers=headers)

            if list_req.status_code == 200:
                cert_count = int(list_req.headers['X-Total-Count'])

                if cert_count > 0:
                    print(f"  Found {cert_count} existing certificate(s)")
                    certs = list_req.json()

                    for existing in certs:
                        curID = existing['sslId']

                        get_url = f"https://cert-manager.com/api/ssl/v1/{curID}"
                        detail_req = requests.get(get_url, headers=headers)

                        details = detail_req.json()
                        commonName = details['commonName']
                        status = details['status']
                        certType = details['certType']
                        profile_id = certType['id']
                        profile_name = certType['name']
                        expires = details['expires']
                        requested = details['requested']
                        requester = details['requester']

                        print(f"    {curID}: Expires {expires}. Requested by {requester} on {requested} with profile {profile_name}")
                else:
                    print("  No existing certificates found.")
