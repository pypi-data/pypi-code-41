from cement import Controller, ex


def get_pool_members(conn, pool_id):
    memberdata = {}
    members = conn.load_balancer.members(pool_id)
    for member in members:
        memberdata[member.id] = {
            'project_id': member.project_id,
            'name': member.name,
            'provisioning_status': member.provisioning_status,
            'operating_status': member.operating_status,
            'dest': "{}:{}".format(member.address, member.protocol_port)
        }
    return memberdata


def get_listener_info(conn, listener_list):
    listenerdata = {}
    for listener in listener_list:
        listener_obj = conn.load_balancer.get_listener(listener['id'])
        members = get_pool_members(conn, listener_obj.default_pool_id)
        listenerdata[listener_obj.id] = {
            'port_proto': "{}{}".format(listener_obj.protocol_port,
                listener_obj.protocol),
            'pool_id': listener_obj.default_pool_id,
            'name': listener_obj.name,
            'project_id': listener_obj.project_id,
            'members': members
        }
    return listenerdata


def get_load_balancer_info(self, conn):

    lbs = conn.load_balancer.load_balancers()
    ips = list(conn.network.ips())

    lbdata = {}
    for lb in lbs:
        # Correlate project IDs to project names
        try:
            project_name = conn.identity.get_project(lb.project_id)
        except self.app.err.NotFoundException:
            project_name = 'missing'

        # Correlate floating IP addresses and VIP addresses
        floating_ip_addr = 'none'
        for floating_ip in ips:
            if floating_ip.fixed_ip_address == lb.vip_address and \
                floating_ip.port_id == lb.vip_port_id:
                floating_ip_addr = floating_ip.floating_ip_address

        # Correlate listener data
        listenerdata = get_listener_info(self.app.conn, lb.listeners)

        # put all the data in a dict
        lbdata[lb.id] = {
            'id': lb.id,
            'data': {
                'vip': lb.vip_address,
                'project_id': lb.project_id,
                'project_name': project_name,
                'vip_address': lb.vip_address,
                'floating_ip': floating_ip_addr,
                'operating_status': lb.operating_status,
                'provisioning_status': lb.provisioning_status,
                'listeners': listenerdata
            }
        }
    return lbdata


class LoadBalancer(Controller):
    class Meta:
        label = "lb"
        stacked_type = 'embedded'
        stacked_on = 'base'
        output_handler = 'yaml'

    @ex(
        help='list broken load balancers',

        # Specify what bit of data are we looking for
        arguments=[
            ### add '-l', '--lb' to look for orphaned load balancers
            ( [ '-t', '--type' ], {
                'help': 'Specify type of thing to list [lb, amphora]',
                'action': 'store',
                'dest': 'type' } ),
        ],
    )
    def list(self):
        lb = {
            'type' : 'lb',
        }

        if self.app.pargs.type is not None:
            lb['type'] = self.app.pargs.type

        self.app.log.info('Gather environment data %s' % lb['type'])
        lbs = get_load_balancer_info(self, self.app.conn)

        for lb in lbs:
            if lbs[lb]['data']['project_name'] == 'missing' or \
                lbs[lb]['data']['operating_status'] == 'ERROR':
                self.app.render(lbs[lb])
        self.app.print('Test')
