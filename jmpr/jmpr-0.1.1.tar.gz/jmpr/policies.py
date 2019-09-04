class Generator:

    def __init__(self, account: str = '*', user='${aws:username}', path='*', bucket=''):
        self.account = account
        if self.account is None:
            self.account = '*'
        self.user = user
        self.path = path
        self.bucket = bucket

    # SOME PRE-BUILT POLICIES
    def blank_policy(self):
        blank = {}
        blank['Version'] = '2012-10-17'
        blank['Statement'] = []

        return blank

    def self_service_policy(self):
        statement = []
        statement.append(self.ViewAccountInfo('Allow'))
        statement.append(self.ManageOwnPasswords('Allow'))
        statement.append(self.IndividualUserToListOnlyTheirOwnMFA('Allow'))
        statement.append(self.IndividualUserToManageTheirOwnMFA('Allow'))

        policy = self.blank_policy()
        policy["Statement"] = statement

        return policy

    def s3_home_dir_policy(self):
        statement = []

        if self.bucket:
            statement.append(self.S3ViewBuckets('Allow'))
            statement.append(self.S3ViewBucketContents('Allow'))
            statement.append(self.S3ListHomeDir('Allow'))
            statement.append(self.S3ModifyHomeDir('Allow'))

        policy = self.blank_policy()
        policy["Statement"] = statement

        return policy

    def enforceMFA(self, enforce_state=True):
        statement = []

        if enforce_state:
            statement.append(self.MFAAllowDeny('Deny'))
        else:
            statement.append(self.MFAAllowDeny('Allow'))

        policy = self.blank_policy()
        policy["Statement"] = statement

        return policy

    # THE POLICY STATEMENT DEFINITIONS
    def ViewAccountInfo(self, effect):
        policy = {}
        policy['Sid'] = 'AllowViewAccountInfo'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('iam:GetAccountPasswordPolicy')
        policy['Action'].append('iam:GetAccountSummary')
        policy['Action'].append('iam:ListVirtualMFADevices')
        policy['Resource'] = '*'

        return policy

    def ManageOwnPasswords(self, effect):
        policy = {}
        policy['Sid'] = 'AllowManageOwnPasswords'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('iam:ChangePassword')
        policy['Action'].append('iam:GetUser')
        policy['Resource'] = []
        policy['Resource'].append('arn:aws:iam::' + str(self.account) + ':user/' + self.user)

        return policy

    def IndividualUserToListOnlyTheirOwnMFA(self, effect):
        policy = {}
        policy['Sid'] = 'AllowIndividualUserToListOnlyTheirOwnMFA'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('iam:ListMFADevices')
        policy['Resource'] = []
        policy['Resource'].append('arn:aws:iam::' + str(self.account) + ':mfa/*')
        policy['Resource'].append('arn:aws:iam::' + str(self.account) + ':user' + self.path + self.user)

        return policy

    def IndividualUserToManageTheirOwnMFA(self, effect):
        policy = {}
        policy['Sid'] = 'AllowIndividualUserToManageTheirOwnMFA'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('iam:CreateVirtualMFADevice')
        policy['Action'].append('iam:DeleteVirtualMFADevice')
        policy['Action'].append('iam:EnableMFADevice')
        policy['Action'].append('iam:ResyncMFADevice')
        policy['Action'].append('iam:DeactivateMFADevice')
        policy['Resource'] = []
        policy['Resource'].append('arn:aws:iam::' + str(self.account) + ':mfa/' + self.user)
        policy['Resource'].append('arn:aws:iam::' + str(self.account) + ':user' + self.path + self.user)

        return policy

    def S3ViewBuckets(self, effect):
        policy = {}
        policy['Sid'] = 'S3ViewBuckets'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('s3:GetBucketLocation')
        policy['Action'].append('s3:ListAllMyBuckets')
        policy['Resource'] = []
        policy['Resource'].append('arn:aws:s3:::*')

        return policy

    def S3ViewBucketContents(self, effect):
        policy = {}
        policy['Sid'] = 'S3ViewBucketContents'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('s3:GetBucketLocation')
        policy['Action'].append('s3:ListAllMyBuckets')
        policy['Resource'] = []
        policy['Resource'].append('arn:aws:s3:::' + self.bucket)
        policy['Condition'] = {}
        policy['Condition']['StringEquals'] = {}
        policy['Condition']['StringEquals']['s3:prefix'] = []
        policy['Condition']['StringEquals']['s3:prefix'].append('')
        policy['Condition']['StringEquals']['s3:prefix'].append(self.path + '/')
        policy['Condition']['StringEquals']['s3:prefix'].append(self.path + '/home/')
        policy['Condition']['StringEquals']['s3:prefix'].append(self.path + '/home/' + self.user)
        policy['Condition']['StringEquals']['s3:delimiter'] = ['/']

        return policy

    def S3ListHomeDir(self, effect):
        policy = {}
        policy['Sid'] = 'S3ListHomeDir'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('s3:ListBucket')
        policy['Resource'] = []
        policy['Resource'].append('arn:aws:s3:::' + self.bucket)
        policy['Condition'] = {}
        policy['Condition']['StringEquals'] = {}
        policy['Condition']['StringEquals']['s3:prefix'] = [self.path + '/home/' + self.user + '/*']

        return policy

    def S3ModifyHomeDir(self, effect):
        policy = {}
        policy['Sid'] = 'S3ModifyHomeDir'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('s3:*')
        policy['Resource'] = []
        policy['Resource'].append('arn:aws:s3:::' + self.bucket + '/' + self.path + '/home/' + self.user + '/*')

        return policy

    def MFAAllowDeny(self, effect):
        policy = {}
        policy['Sid'] = 'MFAAllowDeny'
        policy['Effect'] = effect
        policy['Action'] = []
        policy['Action'].append('sts:AssumeRole')
        policy['Resource'] = '*'
        policy['Condition'] = {}
        policy['Condition']['Bool'] = {}
        policy['Condition']['Bool']['aws:MultiFactorAuthPresent'] = 'false'

        return policy

    def policyDiff(self, policy1, policy2):
        return not policy1 == policy2
