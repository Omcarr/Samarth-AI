import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
import os



def post_jira_issues(content_text, content_type, para):
    load_dotenv()
    jira_api = os.getenv("JIRA_API_KEY")
    jira_url = os.getenv("JIRA_URL")
    jira_mail = os.getenv("JIRA_MAIL")

    auth = HTTPBasicAuth(jira_mail, jira_api)
    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
    }

    payload = json.dumps( {
    "fields": {
        "description": {
        "content": [
            {
            "content": [
                {
                "text": content_text,
                "type": content_type
                }
            ],
            "type": para
            }
        ],
        "type": "doc",
        "version": 1
        },

        "issuetype": {
        "id": "10001"
        },

        "project": {
        "key": "SIH"
        },

        "summary": "Main order flow broken",

        },

    "update": {}
    } )
    response = requests.request(
    "POST",
    jira_url,
    data=payload,
    headers=headers,
    auth=auth
    )

    return json.loads(response.text)

