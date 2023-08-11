def run(params={}):
    from datetime import datetime
    from datetime import timedelta
    import re

    fmt = '%Y-%m-%d %H:%M:%S'
    match = 0

    # convert todays date
    now = datetime.today().strftime(fmt)
    now_convert = datetime.strptime(now, fmt)
    params["now"] = now_convert

    # convert 90 days ago and 14 days ago
    now_90days = now_convert - timedelta(90)
    params["now_90days"] = now_90days
    now_14days = now_convert - timedelta(14)
    params["now_14days"] = now_14days

    # convert when created date
    whenCreated = params["whenCreated"]
    whenCreated_convert = datetime.strptime(whenCreated[:19], fmt)

    # convert verify date
    try:
        verify_date = params["extensionAttribute1"] or params["extensionattribute1"]
        verify_date_regex = re.search(r'\d{1,2}/\d{1,2}/\d{4}', verify_date)
        verify_date_convert = datetime.strptime(verify_date_regex.group(0), '%d/%M/%Y')
        if verify_date_convert < now_90days:
            match += 1
    except KeyError:
        verify_date_convert = None
        if whenCreated_convert > now_14days:
            match += 1
    params["verify_date"] = verify_date_convert


    # convert last logon date
    try:
        last_logon = params["lastLogon"]
        last_logon_convert = datetime.strptime(last_logon[:19], fmt)
        if last_logon_convert is not None and last_logon_convert < now_90days:
            match += 1
        elif last_logon_convert is None and whenCreated_convert < now_14days:
            match += 1
        else:
            match += 0
    except TypeError:
        last_logon_convert = None
    params["lastLogon"] = last_logon_convert

    # create manager email
    manager = params["manager"]
    if manager is not None:
        manager_clean = re.search(r'(CN=)(.*?)(?<!\\),.*', manager).group(2)
        if "\," in manager_clean:
            manager_firstname = manager_clean.split(" ")[1]
            manager_lastname = manager_clean.split(" ")[0].replace("\,", "")
        else:
            manager_firstname = manager_clean.split(" ")[1]
            manager_lastname = manager_clean.split(" ")[0]
    else:
        manager_email = None
    manager_email = (manager_firstname + "." + manager_lastname + "@workplace.com")
    params["manager"] = manager_email

    employee_email = params["mail"]
    params["match"] = match

    return {"results": params}

input = {
      "displayName": "Doe, John",
      "distinguishedName": "CN=Doe\\, John,OU=ServiceNowTest,OU=Users,OU=GS,DC=workplace,DC=corp",
      "extensionattribute1": "Test2 verified by Doe, Jane|DoeJ|3/7/2022",
      "lastLogon": "2023-07-12 14:44:44",
      "mail": "John.Doe@workplace.com",
      "manager": "CN=Doe\\, John,OU=Users,OU=GS,DC=Boardwalk,DC=corp",
      "sAMAccountName": "Test2",
      "userAccountControl": 512,
      "whenCreated": "2023-07-12 14:44:44+00:00"
    }

run(input)