"""Update Class file."""


class Update(object):
    """Update class."""

    def __init__(self, auth, github):
        """Initialize a class instance."""
        self.auth = auth
        self.github = github

        # data
        self.people = {}
        self.users = {}

    def _get_invitations(self):
        """Return a dict of invitations by GitHub ID."""
        invitations = {}
        for i in self.github.get_org_invitations():
            login = i['login'].lower()
            invitations[login] = i
        return invitations

    def _get_members(self):
        """Return a dict of members by GitHub ID."""
        members = {}
        for m in self.github.get_org_members():
            gid = u'%s' % (m['id'])
            members[gid] = m
        return members

    def _get_new_logins(self, new):
        """Return a list of logins in the new users data."""
        logins = []
        for gid in new:
            n = new[gid]
            login = n['login'].lower()
            logins.append(login)
        return logins

    def _get_users_to_invite(self, current, new, invitations):
        """Return a list of logins to invite to the organization."""
        invite = []
        for gid in new:
            n = new[gid]
            login = n['login']
            if gid not in current:
                # make sure user doens't already have an invitation
                if login not in invitations:
                    invite.append(login)
        return invite

    def _get_users_to_remove(self, current, new):
        """Return a list of users to remove from the organization."""
        remove = []
        for gid in current:
            if gid not in new:
                login = current[gid]['login']
                remove.append(login)
        return remove

    def _get_users_to_uninvite(self, invitations, logins):
        """Return a list of users to uninvite from the organization."""
        uninvite = []
        for login in invitations:
            if login.lower() not in logins:
                uninvite.append(login)
        return uninvite

    def _prepare_members(self):
        """Prepare a list of org members for GitHub."""
        datastore = self.github.datastore(self.auth)
        if not self.users:
            self.users = datastore.get_users_dict()
        print('Found %s Tokens in GitHub App.' % (len(self.users)))

        # firestore - get people
        firestore = self.github.firestore(self.auth)
        if not self.people:
            self.people = firestore.get_people_dict()
        print('Found %s People in BITSdb.' % (len(self.people)))

        role_accounts = self.github.get_team_members(self.github.role_team)
        print('Found %s GitHub Role Accounts.' % (len(role_accounts)))

        members = {}

        # add github users who have linked their account and have a valid token
        for email in self.users:
            if email not in self.people:
                print('ERROR: Person not found: %s' % (email))
                continue
            elif self.people[email]['terminated']:
                # print('WARNING: Person is terminated: %s' % (email))
                continue
            user = self.users[email]
            gid = u'%s' % (user['github_id'])
            members[gid] = user

        # add in role accounts
        for member in role_accounts:
            gid = u'%s' % (member['id'])
            members[gid] = member

        return members

    def update_members(self):
        """Update members in GitHub."""
        current = self._get_members()
        print('Found %s current GitHub Members.' % (len(current)))

        new = self._prepare_members()
        print('Found %s suitable GitHub Members.' % (len(new)))

        invitations = self._get_invitations()
        print('Found %s open GitHub Invitations.' % (len(invitations)))

        # get users to invite and remove from the org
        invite = self._get_users_to_invite(current, new, invitations)
        remove = self._get_users_to_remove(current, new)

        # check for invitations to cancel
        logins = self._get_new_logins(new)
        uninvite = self._get_users_to_uninvite(invitations, logins)

        if invite:
            print('\nMembers to invite: %s' % (len(invite)))
            for login in sorted(invite):
                print('   + %s' % (login))
                # self.github.invite_org_member(login)

        if remove:
            print('\nMembers to remove: %s' % (len(remove)))
            for login in sorted(remove):
                print('   - %s' % (login))
                # self.github.remove_org_member(login)

        if uninvite:
            print('\nInvitations to cancel: %s' % (len(uninvite)))
            for login in sorted(uninvite):
                print('   - %s' % (login))
                # self.github.remove_org_member(login)

    def update_teams(self):
        """Update team membership in GitHub from Google Groups."""
        datastore = self.github.datastore(self.auth)
        if not self.users:
            self.users = datastore.get_users_dict()
        print('Found %s Tokens in GitHub App.' % (len(self.users)))

        # firestore - get people
        firestore = self.github.firestore(self.auth)
        people = firestore.get_people_dict()
        print('Found %s People in BITSdb.' % (len(people)))

        # firestore - get team syncs
        firestore = self.github.firestore(self.auth)
        team_syncs = firestore.get_team_syncs_dict()
        print('Found %s GitHub Team Syncs in BITSdb.' % (len(team_syncs)))

        for slug in sorted(team_syncs):
            s = team_syncs[slug]
            tid = s['github_team']
            email = s['google_group']
            print('\n%s [%s] <-- %s:' % (
                slug,
                tid,
                email,
            ))

            # get team members
            current = self.github.get_team_members(tid)
            print('   current members: %s' % (len(current)))

            # get team invitations
            invitations = self.github.get_team_invitations(tid)
            if invitations:
                print('   invitations: %s' % (len(invitations)))

            # get google group members
            # group_members = self._get_google_group_members(email)

            # prepare google group members into team members
            # new = self._prepare_team_members(group_members, self.users)

            # get team members to add
            # add = self._get_team_members_to_add(current, new)

            # get team members to remove
            # remove = self._get_team_members_to_remove(current, new)
