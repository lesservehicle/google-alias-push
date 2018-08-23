from ldap3 import Server, Connection, ObjectDef, Reader, ALL
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import configparser
#from var_dump import var_dump



if __name__ == "__main__":

    # Setup the Admin SDK Directory API
    SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/home/adam/PycharmProjects/google-alias-push/client_secret-prod.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('admin', 'directory_v1', http=creds.authorize(Http()))

    # Setup the local LDAP connection
    Config = configparser.ConfigParser(comment_prefixes='#')
    server = Server('ldap.montclair.edu', get_info=ALL)
    Config.read('./config.ini')
    basedn = Config.get('doit','basedn')
    authdn = Config.get('doit','authdn')
    authpw = Config.get('doit','authpw', raw=True)

    conn = Connection(server, user=authdn, password=authpw)
    conn.bind()
    conn.start_tls()

    #debugging
    #print(conn, '\n')
    print("Authenticated as " + conn.extend.standard.who_am_i(), '\n')

    obj_inet = ObjectDef('inetLocalMailRecipient', conn)
    r = Reader(conn, obj_inet, basedn, '!(employeeType=ST)')
    r.search()

    for entry in r.entries:

        gaccount = str(entry.mail).replace('mail.', '')

        for alt in entry.mailalternateaddress:
            if not (str(alt) == gaccount):
                print(str(alt) + ' => ' + gaccount)

        try:
            results = service.users().aliases().list(userKey=gaccount).execute()
        except:
            continue

        alias = results.get('aliases', [])
        for item in alias:
            print(item['alias'])

    # Generate request for insert
    #requestDict = {'alias': 'adam.copeland@sandbox.montclair.edu'}
    #request = service.users().aliases()

    #if service.users().aliases().insert(userKey='copelanda@sandbox.montclair.edu', body=requestDict).execute():
    #    results = service.users().aliases().list(userKey='copelanda@sandbox.montclair.edu').execute()
    #    alias = results.get('aliases', [])
    #    print(alias[0]['alias'])


