from ldap3 import Server, Connection, ObjectDef, Reader, ALL
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import configparser
#from var_dump import var_dump



if __name__ == "__main__":

    # Setup the Admin SDK Directory API
    SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/home/adam/PycharmProjects/google-alias-push/credentials-prod.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('admin', 'directory_v1', http=creds.authorize(Http()))

    # Setup the local LDAP connection
    Config = configparser.ConfigParser(comment_prefixes='#')
    Config.read('./config.ini')
    basedn = Config.get('google-alias-push','basedn')
    authdn = Config.get('google-alias-push','authdn')
    authpw = Config.get('google-alias-push','authpw', raw=True)
    host = Config.get('google-alias-push','host')

    server = Server(host, get_info=ALL)
    conn = Connection(server, user=authdn, password=authpw)
    conn.bind()
    conn.start_tls()

    print("Authenticated as " + conn.extend.standard.who_am_i(), '\n')

    obj_inet = ObjectDef('inetLocalMailRecipient', conn)
    r = Reader(conn, obj_inet, basedn, '!(employeeType=ST)')
    r.search()


    for entry in r.entries:

        gaccount = str(entry.mail).replace('mail.', '')

        for alt in entry.mailalternateaddress:
            if not (str(alt) == gaccount):
                print(str(alt) + ' => ' + gaccount)

                alias = str(alt).replace('mail.', '')
                netid = gaccount

                requestDict = {'alias': alias}
                request = service.users().aliases()

                try:
                    if service.users().aliases().insert(userKey=netid, body=requestDict).execute():
                        results = service.users().aliases().list(userKey=netid).execute()
                        alias = results.get('aliases', [])
                        print(alias[0]['alias'])
                except:
                    continue

        try:
            results = service.users().aliases().list(userKey=gaccount).execute()
        except:
            continue

        alias = results.get('aliases', [])
        for item in alias:
            print(item['alias'])

