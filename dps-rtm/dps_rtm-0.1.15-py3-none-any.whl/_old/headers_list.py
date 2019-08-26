"""
this script initializes a list of "approved" column headers. It also defines a function that compares the approved list
to an input list (future state will be from User's file) and returns a named tuple with found, not found and extra
fs.

"""



"""
#USE THIS!!
list1 = [
    'item1',
    'item2',
]
"""

def header_check(approved_headers_list,users_headers_list):
    # use set() to determine what is missing from users list (approved - users)
    missing_from_users = list(set(approved_headers_list)-set(users_headers_list))
    # use set() to determine the extra items on users list (users - approved)
    users_extra = list(set(users_headers_list)-set(approved_headers_list))
    if (missing_from_users and users_extra) == []:
        matches = users_headers_list




"""
SANDBOX 
"""
if __name__ == '__main__':

    # approved_headers_list contains the "approved" column headers
    approved_headers_list = []
    approved_headers_list.append("ID")
    approved_headers_list.append("Procedure Step")
    approved_headers_list.append("User Need")
    approved_headers_list.append("Design Input")
    approved_headers_list.append("DO Solution L1")
    approved_headers_list.append("DO Solution L2")
    approved_headers_list.append("DO Solution L3")
    approved_headers_list.append("Cascade Level")
    approved_headers_list.append("Requirement Statement")
    approved_headers_list.append("Requirement Rationale")
    approved_headers_list.append("Verification or Validation Strategy")
    approved_headers_list.append("Verification or Validation Results")
    approved_headers_list.append("Devices")
    approved_headers_list.append("Design Output Feature (with CTQ ID #)")
    approved_headers_list.append("CTQ? Yes, No, N/A")
    # print(approved_headers_list)

    # headers_list contains a sample users column headers
    users_headers_list = []
    users_headers_list.append("ID")
    users_headers_list.append("Procedure Step")
    users_headers_list.append("User Need")
    users_headers_list.append("Design Input")
    users_headers_list.append("DO Solution L1")
    users_headers_list.append("DO Solution L2")
    users_headers_list.append("DO Solution L3")
    users_headers_list.append("Cascade Level")
    users_headers_list.append("Requirement Statement")
    users_headers_list.append("Requirement Rationale")
    users_headers_list.append("Verification or Validation Strategy")
    users_headers_list.append("Verification or Validation Results")
    users_headers_list.append("Devices")
    users_headers_list.append("Design Output Feature (with CTQ ID #)")
    users_headers_list.append("CTQ? Yes, No, N/A")
    users_headers_list.append("Extra Header1")
    # users_headers_list.append("Extra Header2")
    # print(users_headers_list)
    # This is your playground
    # call function
    # print result

    testout = header_check(approved_headers_list,users_headers_list)
    print(testout)
    pass
