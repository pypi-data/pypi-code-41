from appJar import gui
import boto3


# Data Access Functions
def assume_role(accountID, accountHandle, creds):
    client = boto3.client('sts')
    response = client.assume_role(
        DurationSeconds=3600,
        RoleArn='arn:aws:iam::' + accountID + ':role/org-admin-role',
        RoleSessionName=accountHandle.replace(' ', '_')  # Gotcha, API does not allow spaces
    )
    credentials = response['Credentials']
    creds.update({accountHandle: credentials})
    print(accountHandle, creds[accountHandle])
    return creds


def get_org_accounts():
    org_client = boto3.client("organizations")  # No creds because in org account so default
    org_accounts = org_client.list_accounts_for_parent(ParentId='ou-6ge1-awqocg6s')
    return org_accounts['Accounts']


def get_accountnames(org_accounts):
    account_names = ['-']
    for account in org_accounts:
        account_names.append(account['Name'])
    return account_names


def get_iam(org_accounts, creds):
    for account in org_accounts:
        try:
            assume_role(account['Id'], account['Name'], creds)
        except:  # noqa: E722
            print("Failed assume role for account " + account['Name'] + ' ' + account['Id'])


def get_identities():
    # Call to identity account and get the appropriate identity roles, maybe by tag or name convention
    # john = {"handle": "JohnS", "arn": "arn:aws:iam::343074669674:role/johns-identity"}
    # rpc = {"handle": "rpc", "arn": "arn:aws:iam::343074669674:role/rpc-identity"}
    # ryan = {"handle": "Ryan", "arn": "arn:aws:iam::343074669674:role/ryan-identity"}
    iam = boto3.client(
        'iam',
        aws_access_key_id=creds['identity']['AccessKeyId'],
        aws_secret_access_key=creds['identity']['SecretAccessKey'],
        aws_session_token=creds['identity']['SessionToken'],)
    iamUsers = iam.list_users()
    return iamUsers['Users']


def get_users():
    identities = get_identities()
    users = ["-"]
    for item in identities:
        users.append(item['Path'] + item['UserName'])
    # for user in identities:
    #    users.append(user["handle"])
    return users


def press(btnName):
    app.popUp("INFO", "You pressed " + btnName)


def update(value):
    if value == "list":
        app.slider("slider", app.listbox(value)[0])
    elif value == "slider":
        app.listbox("list", app.slider(value))
    app.label("display", app.listbox("list")[0])


org_accounts = get_org_accounts()
account_names = get_accountnames(org_accounts)
creds = {}
assume_role('616552976502', 'dev', creds)
assume_role('547869200176', 'identity', creds)
get_iam(org_accounts, creds)
roles = ["Labs Prod ADMINS", "Labs Prod DEVS", "Labs DEV ADMINS", "Labs DEV DEVS"]
identities = get_identities()

# Gui Part
# data = "<people><person><name>Richard</name><age>21</age></person>
# <person><name>kh</name><age>44</age></person></people>"
data = "<egt-Labs>Raw Entry</egt-Labs>"

with gui("Version 1.0", "1000x500", bg="white") as app:
    app.label("jmpr Role Manager", colspan=1, bg="white")

    with app.frame("LEFT", row=0, column=0, bg='white', stretch='column', sticky="w"):
        app.addLabel("Title", "Account", 0, 0, colspan=1)
        app.setLabelAlign("Title", "center")
        app.addOptionBox("Accounts", account_names, sticky="LEFT", row=1, column=0)
        app.setOptionBoxAlign("Accounts", "left")
        # app.addTree("tree", data)

    with app.frame("CENTER", row=0, column=1, bg='white', fg='black', stretch='column', sticky="w"):
        app.addLabel("users", "User", 0, 0, colspan=1)
        app.setLabelAlign("users", "center")
        app.addOptionBox("users", get_users(), sticky="LEFT", row=1, column=0)
        app.setOptionBoxAlign("users", "left")

    with app.frame("RIGHT", row=0, column=2, bg='white', fg='black', stretch='column', sticky="w"):
        app.addLabel("roles", "Roles", 0, 0, colspan=1)
        app.setLabelAlign("roles", "center")
        for role in roles:
            app.addCheckBox(role)
