#!/usr/bin/env python3

from ldap3 import Server, Connection, ALL, NTLM

host = '192.168.0.XXX'
dn = 'CN=Someone,OU=SomeOU,DC=yourDomain,DC=yourDomain'
pw = 'your password'
base_dn = 'OU=SomeOU,DC=yourDomain,DC=yourDomain'

output_users='/path/to/output/users.csv'
output_groups='/path/to/output/groups.csv'
output_members_group='/path/to/output/' # here is a directory


server = Server(host,  get_info=ALL)
conn = Connection(server, dn, pw, auto_bind=True)

def search(filter, attrs):
    conn.search(base_dn, filter, attributes=attrs)
    entries = conn.entries
    print(entries)
    return entries


def normalize(entries, file):
    data=[]
    for i in entries:
        row=str(i['sAMAccountName'].values)[2:-2]+';'+str(i['cn'].values)[2:-2]+';'+str(i['givenname'].values)[2:-2]+';'+str(i['sn'].values)[2:-2]+';'+str(i['description'].values)[2:-2]+';'+str(i['mail'].values)[2:-2]
        data.append(row)
    export(file, data)

def export(file, data):
    with open(file, 'a', encoding='utf-8') as f:
        # clean file before write
        f.truncate(0)
        f.writelines('\n'.join(data))
        f.close()

def getUsers():
    # Show only activated users
    # filter = '(&(memberOf=cn=workers,cn=users,dc=example,dc=com)(!(userAccountControl=66050)))'
    filter_users = '(&(objectclass=person)(objectclass=user)(objectclass=organizationalPerson)(!(objectclass=computer))(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'
    attrs_users = ['cn', 'sAMAccountName', 'givenname', 'sn', 'mail', 'description', 'telephonenumber', 'homephone', 'mobile', 'objectclass', 'userAccountControl']
    entries = search(filter_users, attrs_users)
    normalize(entries, output_users)


def getGroups():
    filter_grps = '(&(objectCategory=group))'
    attrs_grps = ['cn', 'sAMAccountName', 'givenname', 'sn', 'mail', 'description', 'objectclass', 'distinguishedName']
    entries = search(filter_grps, attrs_grps)
    normalize(entries, output_groups)
    getMembers(entries)

def getMembers(groups_entries):
    for group in groups_entries:
        cn=str(group['cn'].values)[2:-2]
        dn=str(group['distinguishedName'].values)[2:-2]
        filter_grps_members='(&(objectCategory=user)(memberOf='+dn+')(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'
        attrs_grps_members = ['cn', 'sAMAccountName', 'givenname', 'sn', 'mail', 'description', 'objectclass', 'distinguishedName']
        entries = search(filter_grps_members, attrs_grps_members)
        individual_file = output_members_group + str(cn) + '.csv'
        normalize(entries, individual_file)

getUsers()
getGroups()
