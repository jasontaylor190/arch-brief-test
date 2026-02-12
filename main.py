import os
from dotenv import load_dotenv
import requests
import json

load_dotenv(override=True)
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')
#LEANIX_GRAPHQL_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1/graphql'
#LEANIX_OAUTH2_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token'
LEANIX_GRAPHQL_URL = f'https://demo-us.leanix.net/services/pathfinder/v1/graphql'
LEANIX_OAUTH2_URL = f'https://demo-us.leanix.net/services/mtm/v1/oauth2/token'
LEANIX_UPLOAD_URL = f'https://demo-us.leanix.net/services/pathfinder/v1/graphql/upload'


def _obtain_access_token() -> str:
    """Obtains a LeanIX Access token using the Technical User generated
    API secret.

    Returns:
        str: The LeanIX Access Token
    """
    if not LEANIX_API_TOKEN:
        raise Exception('A valid token is required')
    response = requests.post(
        LEANIX_OAUTH2_URL,
        auth=("apitoken", LEANIX_API_TOKEN),
        data={"grant_type": "client_credentials"},
    )

    response.raise_for_status()
    return response.json().get('access_token')

def loadpdf():
    with open('archbrief.pdf', 'rb') as file:
        return file.read()

def main():
    """Executes a query against the LeanIX GraphQL API and prints
    the output.
    """

    access_token = _obtain_access_token()

    query = """
      query MyQuery {
        factSheet(id: "abd01a88-dd54-4da0-a216-4262e7288005") {
          id
          description
          name
        }
      }
      """
    
    update = """
      mutation MyMutation{
        updateFactSheet(
            id: "abd01a88-dd54-4da0-a216-4262e7288005" 
            patches: {op: replace, path: "/description", value: "This is a placeholder for the architecture brief content."} ) {
                factSheet {
                    id
                    description
                }
            }
      }
      """

    data = {'query': update}
    auth_header = f'Bearer {access_token}'
    response = requests.post(
        url=LEANIX_GRAPHQL_URL,
        headers={'Authorization': auth_header},
        data=json.dumps(data)
    )

    response.raise_for_status()
    factsheet_id=response.json().get('data', {}).get('factSheet', {}).get('id')
    factsheet_id="abd01a88-dd54-4da0-a216-4262e7288005"
    factsheet_name=response.json().get('data', {}).get('factSheet', {}).get('name')

    if not factsheet_id:
        raise Exception('No factsheet found')
    mutation = f"""
        mutation createDocument {{
            createDocument(
                factSheetId: "{factsheet_id}"
                name: "archbrief.pdf"
                documentType: "documentation"
                origin: "LX_STORAGE_SERVICE"
            ) {{
                id
                name
                url
                factSheetId
            }}
        }}
    """ 
    form_data = {
        'graphQLRequest': (
            None, 
             json.dumps({'query': mutation})
            ),
        'file': ('archbrief.pdf', loadpdf(), 'application/pdf')
    }

    response = requests.post(
        url=LEANIX_UPLOAD_URL,
        headers={'Authorization': auth_header,
                 'Accept': 'application/json'},
        files=form_data
        )
    
    print(response.json())

if __name__ == '__main__':
    main()
