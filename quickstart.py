"""
Shows basic usage of the Admin SDK Directory API. Lists of first 10 users in the
domain.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Admin SDK Directory API
SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('/home/adam/PycharmProjects/google-alias-push/client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('admin', 'directory_v1', http=creds.authorize(Http()))

# Call the Admin SDK Directory API
print('Getting the first 10 users in the domain')
results = service.users().list(customer='my_customer', maxResults=10,
                               orderBy='email').execute()
users = results.get('users', [])



if not users:
    print('No users in the domain.')
else:
    print('Users:')
    for user in users:
        print('{0} ({1})'.format(user['primaryEmail'], user['name']['fullName']))