"""
This script serves as a library of functions for FDR checker. Each function has two comments before it, the first is
which column it is intended for and the second states what it does. unless otherwise stated, each function returns a
boolean true or false

"""


# functions start here

# Any
# take value_at_index in and return it with no carriage returns (\n). This will make strings easier to evaluate
def remove_carriage_returns(value):
    value = value.replace("\n", "")
    return value

# Any
# checks if empty. returns True if empty
def is_empty(value):
    if not value:
        return True
    else:
        return False


# Any
# checks if value_at_index is N/A.
# FDR rules: type of requirement/other circumstances may/may not allow N/A in certain fs
def is_notapplic(value):
    # remove whitespace for direct string comparison. e.g. 'n / a ' becomes 'n/a'
    value = value.replace(" ", "")
    # compare lower case version of cell contents to 'n/a'.
    if value.lower() == "n/a":
        return True
    else:
        return False


# Any
# checks if value_at_index is explicitly a hyphen
# FDR rules: if row is a procedure step, all columns besides ID, cascade visualizer, cascade level and requirement
#   statement should be a hyphen
def is_hypen(value):
    # remove whitespace for direct string comparison. e.g. ' - ' becomes '-'
    value = value.replace(" ", "")
    if value == "-":
        return True
    else:
        return False


# Any
# checks if value_at_index is yes
def is_yes(value):
    # remove whitespace for direct string comparison. e.g. 'yes ' becomes 'yes'
    value = value.replace(" ", "")
    if value.lower() == "yes":
        return True
    else:
        return False


# Any
# checks if value_at_index is no
def is_no(value):
    # remove whitespace for direct string comparison. e.g. 'no ' becomes 'no'
    value = value.replace(" ", "")
    if value.lower() == "no":
        return True
    else:
        return False


# Any
# checks if value_at_index contains 'not required' in its text
# FDR rules: some fs are not required. e.g. validation is not required if requirement is a business need
def has_not_required(value):
    if value.lower().find("not required") != -1:
        return True
    else:
        return False


# ID
# checks that value_at_index has a capital P as the first character.
# FDR rules: recommended ID formatting for procedure steps and procedure based requirements follow a naming convention.
#   e.g. P010, P020, etc. for procedure steps and P010-020 for procedure based requirements
def starts_with_p(value):
    if value.startswith("P"):
        return True
    else:
        return False


# ID
# checks if value_at_index has integers following the first letter
# FDR rules: recommended ID formatting for procedure steps follow a naming convention.
#   e.g. P010, P020, etc. for procedure steps
def has_digits_after_first(value):
    return value[1:].isdigit()


# ID
# checks if value_at_index has 3 integers following the first character. First char is omitted
# FDR rules: recommended ID formatting for procedure steps follow a naming convention.
#   e.g. P010, P020, etc. for procedure steps
def has_three_digits(value):
    str1 = value[1:]
    if (len(str1) == 3) and (str1.isdigit() is True):
        return True
    else:
        return False


# ID
# checks if value_at_index has 6 integers following the first character.
# FDR rules: recommended ID formatting for procedure based requirements follow a naming convention.
#   e.g. P010-020, P010-030, etc. for procedure based requirements
# NOTE: First char is omitted. Assumes there is a dash and removes it
def has_six_digits(value):
    # slice string. keep all characters after the first. (removes P)
    value_slice = value[1:]
    # find the location/get_index of the hypen within the string.
    dash_index = value_slice.find("-")
    # slice string around the hyphen. this will leave only the numeric characters if ID if formatted correctly
    value_slice = value_slice[:dash_index] + value_slice[dash_index + 1:]
    if (len(value_slice) == 6) and (value_slice.isdigit() is True):
        return True
    else:
        return False


# ID
# checks for hyphen within string
# FDR rules: recommended ID formatting for procedure based requirements follow a naming convention.
# e.g. P010-020, P010-030, etc. for procedure based requirements
def has_hyphen(value):
    if value.find("-") != -1:
        return True
    else:
        return False


# ID
# Check for dash in 4th position (P010-001)
# FDR rules: recommended ID formatting for procedure based requirements follow a naming convention.
# e.g. P010-020, P010-030, etc. for procedure based requirements
def has_hyphen_positioned(value):
    if value.find("-") == 4:
        return True
    else:
        return False


# Cascade Block
# checks for capital X
# FDR rules: only a capital X or capital F are allowed in the cascade visualizer columns. (B-G in its current form)
# TODO Question: "has" implies there are allowed to be other chars in the string as well.
# TODO I forget how, but there's a better way of removing that whitespace. Strip, maybe?
def has_capital_x(value):
    # remove whitespace for direct string comparison. e.g. ' X ' becomes 'X'
    value = value.replace(" ", "")
    if value == "X":
        return True
    else:
        return False


# Cascade Block
# checks for lowercase x
# FDR rules: only a capital X or capital F are allowed in the cascade visualizer columns. (B-G in its current form)
def has_lower_x(value):
    # remove whitespace for direct string comparison. e.g. ' x ' becomes 'x'
    value = value.replace(" ", "")
    if value == "x":
        return True
    else:
        return False


# Cascade Block
# checks for capital F
# FDR rules: only a capital X or capital F are allowed in the cascade visualizer columns. (B-G in its current form)
def has_capital_f(value):
    # remove whitespace for direct string comparison. e.g. ' F ' becomes 'F'
    value = value.replace(" ", "")
    if value == "F":
        return True
    else:
        return False


# Cascade Block
# checks for lowercase f
# FDR rules: only a capital X or capital F are allowed in the cascade visualizer columns. (B-G in its current form)
def has_lower_f(value):
    # remove whitespace for direct string comparison. e.g. ' f ' becomes 'f'
    value = value.replace(" ", "")
    if value == "f":
        return True
    else:
        return False


# Cascade level
# checks if cascade level is 'procedure step'
# FDR rules: cascade level defines the type of requirement and can only contain one of the following strings:
# procedure step, user need, risk need, business need, design input or design output
def is_procedure_step(value):
    # remove whitespace at the beginning and end of the string and test for value_at_index
    if value.strip().lower() == "procedure step":
        return True
    else:
        return False


# Cascade Level
# checks if cascade level is 'user need'
# FDR rules: cascade level defines the type of requirement and can only contain one of the following strings:
# procedure step, user need, risk need, business need, design input or design output
def is_user_need(value):
    # remove whitespace at the beginning and end of the string and test for value_at_index
    if value.strip().lower() == "user need":
        return True
    else:
        return False


# Cascade Level
# checks if cascade level is 'risk need'
# FDR rules: cascade level defines the type of requirement and can only contain one of the following strings:
# procedure step, user need, risk need, business need, design input or design output
def is_risk_need(value):
    # remove whitespace at the beginning and end of the string and test for value_at_index
    if value.strip().lower() == "risk need":
        return True
    else:
        return False


# Cascade Level
# checks if cascade level is 'business need'
# FDR rules: cascade level defines the type of requirement and can only contain one of the following strings:
# procedure step, user need, risk need, business need, design input or design output
def is_business_need(value):
    # remove whitespace at the beginning and end of the string and test for value_at_index
    if value.strip().lower() == "business need":
        return True
    else:
        return False


# Cascade Level
# checks if cascade level is 'design input'
# FDR rules: cascade level defines the type of requirement and can only contain one of the following strings:
# procedure step, user need, risk need, business need, design input or design output
def is_design_input(value):
    # remove whitespace at the beginning and end of the string and test for value_at_index
    if value.strip().lower() == "design input":
        return True
    else:
        return False


# Cascade Level
# checks if cascade level is 'design output solution'
# FDR rules: cascade level defines the type of requirement and can only contain one of the following strings:
# procedure step, user need, risk need, business need, design input or design output
def is_design_output(value):
    # remove whitespace at the beginning and end of the string and test for value_at_index
    if value.strip().lower() == "design output solution":
        return True
    else:
        return False


# Cascade level
# checks if cascade level is one of the approved options.
# returns true if it is procedure step, user need, risk need, business need, design input or design output
# FDR rules: cascade level may only be one of the 6 defined types.
def is_cascade_lvl_approved(value):
    if is_procedure_step(value) \
            ^ is_user_need(value) \
            ^ is_risk_need(value) \
            ^ is_business_need(value) \
            ^ is_design_input(value) \
            ^ is_design_output(value) is True:
        return True
    else:
        return False


# V&V Results
# checks if W/C,wc or windchill is present. should indicate if windchill number is present
# FDR rules: Design inputs and outputs may reference a document in windchill for its verification/validation results
def has_w_slash_c(value):
    # convert input argument to all lower case for comparison
    val_lower = value.lower()
    if val_lower.find("w/c") != -1:
        return True
    elif val_lower.find("wc") != -1:
        return True
    elif val_lower.find("windchill") != -1:
        return True
    else:
        return False


# V&V
# checks if 10 digit windchill number is present. example W/C# 0000006634
def is_windchill_number_present(value):
    # remove all spaces
    value = value.replace(" ", "")
    # find get_index of 000. windchill numbers have at least three leading zeros.
    leading_zeros_index = value.find("000")
    # slice the string starting at that get_index until the end of the string
    value = value[leading_zeros_index:]
    # slice string again into two parts. first 10 characters (possible WC number) and remaining characters
    wc_number = value[:9]
    remaining_char = value[10:]
    # test if wc_number is all set_and_get_funcs and remaining is all letters
    if wc_number.isdigit() and (remaining_char.isalpha() or len(remaining_char) == 0) is True:
        return True
    else:
        return False


# Design Output Feature
# checks for CTQ IDs. returns true if "CTQ" is present in the cell
# FDR rules: CTQ (critical to quality) features should be called out in the Design Output features column.
# CTQs should be called out using the following format: (CTQ08)
def has_ctq_id(value):
    if value.lower().find("ctq") != -1:
        return True
    else:
        return False


# Design Output Features
# checks for CTQ number after CTQ tag. returns true if all occurrences of CTQ are followed by two set_and_get_funcs
# returns false if no CTQs are present OR they are not followed by two set_and_get_funcs. (this should be used in conjunction
# with the previous function that looks for CTQ in the cell to eliminate possibility of the former case)
# FDR rules: CTQ (critical to quality) features should be called out in the Design Output features column.
# CTQs should be called out using the following format: (CTQ08)
def has_ctq_numbers(value):
    ctq_count = 0
    number_count = 0
    # find get_index of first CTQ ID
    ctq_index = value.lower().find("ctq")
    # while loop will keep searching for CTQ IDs until there are none. the string is sliced, checked for set_and_get_funcs,
    # searched for a new ID, get_index found for new CTQ ID, repeat.
    while ctq_index != -1:
        # add 1 to ctq_counter, if there were no CTQs, the while condition would not be met.
        ctq_count += 1
        # slice value_at_index from after "ctq"
        value = value[ctq_index + 3:]
        # if the next two characters are numbers (they should be if formatted correctly)
        if value[0:2].isdigit() is True:
            # add 1 to number counter. this counter will be compared to ctq_count later. they should match
            number_count += 1
        # search for next CTQ. if there are not, find() will output a -1 and while loop will end
        ctq_index = value.lower().find("ctq")
    # if "ctq" and number count match AND they aren't zero...they are formatted correctly.
    if (ctq_count == number_count) and ctq_count > 0:
        return True
    else:
        return False


# Requirement Statement
# checks for hash (#) symbol in string
# FDR rules: hastags are used to identify parent/child relationships,
# functional requirements, mating part requirements, user interface requirements and mechanical properties
def has_hash(value):
    if value.find("#") != -1:
        return True
    else:
        return False


# Requirement Statement
# checks for #Function in cell.
# FDR rules: The requirement statement can be tagged using #Function to identify a functional requirement
def has_hash_function(value):
    if value.find("#Function") != -1:
        return True
    else:
        return False


# Requirement Statement
# checks for #MatingParts
# FDR rules: The requirement statement can be tagged using #MatingParts to identify a requirement pertaining to proper
# fitting between components
def has_hash_mating_parts(value):
    if value.find("#MatingParts") != -1:
        return True
    else:
        return False


# Requirement Statement
# checks for #MechProperties
# FDr rules: The requirement statement can be tagged using #MechProperties to identify a requirement that pertains to
# the mechanical properties of the implant/instrument
def has_hash_mech_properties(value):
    if value.find("#MechProperties") != -1:
        return True
    else:
        return False


# Requirement Statement
# checks for #UserInterface
# FDR rules: the requirement statement can be tagged using #UserInterface to identify a requirement that relates to how
# the user handles the implant/instrument
def has_hash_user_interface(value):
    if value.find("#UserInterface") != -1:
        return True
    else:
        return False


# TODO will #Parent or #AdditionalParent be used in requirement statement? sticking with #Parent for now
# Requirement Statement
# checks for #Child returns true if #Child is present
# FDR rules: #Child and #Parent are used to link a Design Input that leads to a Design Output Solution that has
# been documented earlier in the form. The Design Input is tagged using #Child = P###-### where the ID refers to the
# Output solution and the Output solution is tagged using #Parent = P###-### where the ID refers to the Design Input
def has_hash_child(value):
    if value.find("#Child") != -1:
        return True
    else:
        return False


# Requirement Statement
# checks for #Parent returns true if #Parent is present
# FDR rules: #Child and #Parent are used to link a Design Input that leads to a Design Output Solution that has
# been documented earlier in the form. The Design Input is tagged using #Child = P###-### where the ID refers to the
# Output solution and the Output solution is tagged using #Parent = P###-### where the ID refers to the Design Input
# TODO let's not use the word "hash" here. It has a very specific meaning in computer science which can cause
#   confusion. In fact, you've probably already heard/seen it mentioned in the git literature. It's synonymous with
#   "checksum". It's how Python dictionaries work too.
def has_hash_parent(value):
    if value.find("#Parent") != -1:
        return True
    else:
        return False


# Requirement Statement
# returns IDs (P###-###) that are tagged using #Child as a list. assumes there are #Child present.
# FDR rules: #Child and #Parent are used to link a Design Input that leads to a Design Output Solution that has
# been documented earlier in the form. The Design Input is tagged using #Child = P###-### where the ID refers to the
# Output solution and the Output solution is tagged using #Parent = P###-### where the ID refers to the Design Input
def child_ids(value):
    # init output list. will append with values later
    ids_output_list = []
    # remove spaces for easier evaluation
    value = value.replace(" ", "")
    # while there are #child in string. string will be sliced after each ID is retrieved
    while value.find("#Child") != -1:
        # find the get_index of the child hashtag
        hash_index = value.find("#Child")
        value = value[hash_index:]
        # find the beginning of the ID by searching for P
        id_start_index = value.find("P")
        # append output list with ID
        ids_output_list.append(value[id_start_index:id_start_index + 7])
        value = value[id_start_index:]
    return ids_output_list


# Requirement Statement
# returns IDs (P###-###) that are tagged using #Parent as a list. assumes there are #Parent present.
# FDR rules: #Child and #Parent are used to link a Design Input that leads to a Design Output Solution that has
# been documented earlier in the form. The Design Input is tagged using #Child = P###-### where the ID refers to the
# Output solution and the Output solution is tagged using #Parent = P###-### where the ID refers to the Design Input
def parent_ids(value):
    # init output list. will append with values later
    ids_output_list = []
    # remove spaces for easier evaluation
    value = value.replace(" ", "")
    # while there are #child in string. string will be sliced after each ID is retrieved
    while value.find("#Parent") != -1:
        # find the get_index of the child hashtag
        hash_index = value.find("#Parent")
        # slice value_at_index from the hash_index + 2 (to account for capital P at the beginning of Parent) to the end
        value = value[hash_index+2:]
        # find the beginning of the ID by searching for P
        id_start_index = value.find("P")
        # append output list with ID
        ids_output_list.append(value[id_start_index:id_start_index + 7])
        value = value[id_start_index:]
    return ids_output_list

#list of tags

"""
SANDBOX 
"""
if __name__ == '__main__':
    # This is your playground
    # call function
    # print result

    testval = "blah blah TBD \n anatomy (TBD percentile, etc.). \nFunction #Parent = P40-030 #Parent = P40-040"
    testout = remove_carriage_returns(testval)
    print(testout)
    pass

"""

# init a mock requirement (row on FDR) for testing
req1 = dict(iD="P20", procedureStep=" ", userNeed="X", cascadeLevel="DESIGN OUTPUT SOLUTION",
            requirementStatement="Prepare Patient")
print("\n")
print(req1)
print("\n")

"""
