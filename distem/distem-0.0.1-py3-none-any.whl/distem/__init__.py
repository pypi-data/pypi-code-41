import json
import copy
import logging
import requests


class Distem:
    def __init__(self, *,  serveraddr="localhost", port=4567):
        self.serveraddr = serveraddr
        self.port = port
        self.client = requests.Session()

    def vnetwork_create(self, name, address, opts=None):
        """
        Create a new virtual network


        Args:
            name (str): The name of the virtual network (unique) address(str) The
            addres (str): address in CIDR format (e.g 10.0.8.0/24)
            opts (dict): used to store vxlan_id and number of PNODES
                (should not be used directly)

        Returns:
            dict of the virtual network description
              see :desc:`resources description <>`.
        """
        if opts is None:
            opts = []

        return self.post_json("/vnetworks",
                                data={"name": name,
                                "address": address})

    def vnetwork_remove(self, vnetname):

        """
        Remove a virtual network, that will disconnect every
        virtual node connected on it and remove it's virtual routes.


        Args:
            vnetname(str) The name of the virtual network

        Returns:
            dict of the virtual network description
              see :desc:`resources description<>`
        """

        return self.delete_json(
            "/vnetworks/%s" % (str(vnetname)), data={"type": "remove"}
        )

    def vnetwork_info(self, vnetname):
        """
        Retrieve informations about a virtual network


        Args:
            vnetname(str) The name of the virtual network

        Returns:
            dict of the virtual network description
              see :desc:`resources description<>`
        """

        return self.get_json("/vnetworks/%s" % (str(vnetname)))

    def vnode_info(self, vnodename):
        """
        Retrieve informations about a virtual node


        Args:
            vnodename(str) The name of the virtual node

        Returns:
            dict of the virtual node description
              see :desc:`resources description<>`
        """
        return self.get_json("/vnodes/%s" % (str(vnodename)))

    def vnode_create(self, name, desc=None, ssh_key=None, asynch=False):
        """
        Create a new virtual node

        Args:
            name(str): The name of the virtual node which should be unique
            desc(dict): Hash structured as described in
                :desc:`resources description<>`
            ssh_key(dict): SSH key pair to be copied on the virtual node (also
              adding the public key to .ssh/authorized_keys). Note that every SSH
              keys located on the physical node which hosts this virtual node are
              also copied in .ssh/ directory of the node (copied key have a
              specific filename prefix). The key are copied in .ssh/ directory of
              SSH user (see {Distem::Daemon::Admin#SSH_USER} and
              Distem::Node::Container::SSH_KEY_FILENAME)

                _Format_: dict.

                _Structure_:
                    {
                    "public" : "KEYHASH",
                    "private" : "KEYHASH"
                    }
                Both of +public+ and +private+ parameters are optional
            asynch(bool) Asynchronious mode, check virtual node status
                to know when node is configured (see {#vnode_info})

        Returns:
            dict of the virtual node description
              see :desc:`resources description<>`
        """

        if desc is None:
            desc = {}

        if ssh_key is None:
            ssh_key = {}

        data = {"desc": desc, "ssh_key": ssh_key, "async": asynch}

        return self.post_json("/vnodes/%s" % (name), data=data)

    def vnode_start(self, vnodename, *, asynch=False):
        """Start a virtual node.

        A physical node (that have enough physical resources (CPU,...))
        will be automatically allocated if there is none set as +host+ at
        the moment The filesystem archive will be copied on the hosting
        physical node. A filesystem image *must* have been set (see
        {#vnode_create} or {#vfilesystem_create}/{#vfilesystem_update}).


        Args:
            vnodename (str): The name of the virtual node
            asynch (bool): Asynchronious mode, check virtual node status to know
                when node is configured (see {#vnode_info})

        Returns:
            dict of the virtual node description
              see :desc:`resources description<>`
        """

        desc = {
            "desc": {"name": str(vnodename), "status": "RUNNING"},
            "type": "update",
            "async": asynch,
        }

        return self.put_json("/vnodes/%s" % (str(vnodename)), data=desc)

    def vnode_stop(self, vnodename, asynch=False):
        """
        Stopping a virtual node, deleting it's data from the hosting physical
        node. The +host+ association for this virtual node will be cancelled,
        if you start the virtual node directcly after stopping it, the hosting
        physical node will be chosen randomly (to set it manually, see host
        field, {#vnode_update})


        Args:
            vnodename(str): The name of the virtual node
            asynch(bool): Asynchronious mode, check virtual node status
              to know when node is configured (see {#vnode_info})

        Returns:
            dict of the virtual node description
              see :desc:`resources description<>`
        """

        desc = {"desc": {"status": "DOWN"}, "type": "stop", "async": asynch}

        return self.put_json("/vnodes/%s" % (vnodename), data=desc)

    def vnode_remove(self, vnodename):

        """
        Remove the virtual node

        "Cascade" removing: remove all the vroutes
        in which this virtual node apears as gateway


        Args:
            vnodename (str): The name of the virtual node

        Returns:
            dict of the virtual node description
              see :desc:`resources description<>`
        """

        return self.put_json("/vnodes/%s" % (vnodename), data={"type": "remove"})

    def vnode_freeze(self, vnodename, asynch=False):

        """
        Freeze a virtual node, but without deleting its data


        Args:
            vnodename (str): The name of the virtual node
            asynch bool): Asynchronious mode, check virtual node status
                to know when node is configured (see {#vnode_info})

        Returns:
            dict of the virtual node description
              see :desc:`resources description<>`
        """

        return self.put_json(
            "/vnodes/%s" % (str(vnodename)), {"async": asynch, "type": "freeze"}
        )

    def vnode_unfreeze(self, vnodename, asynch=False):

        """
        Unfreeze a virtual node, but without deleting its data


        Args:
            vnodename (str): The name of the virtual node
            asynch (bool): Asynchronious mode, check virtual node status
                to know when node is configured

        Returns:
            dict of the virtual node description
              see :desc:`resources description<>`
        """

        return self.put_json(
            "/vnodes/%s" % (str(vnodename)), {"async": asynch, "type": "unfreeze"}
        )

    def vnode_execute(self, vnodename, command):

        """
        Execute and get the result of a command on a virtual node


        Args:
            vnodename (str): The name of the virtual node
            command (str): The command to be executed

        Returns:
            [String] The result of the command (Array of string if multilines)
        """

        return self.post_json(
            "/vnodes/%s/commands/" % (str(vnodename)), data={"command": str(command)}
        )

    def vnodes_info(self):

        """
        Retrieve informations about every virtual
        nodes currently set on the platform


        Returns:
            [Array] Array of virtual nodes description
              see :desc:`resources description<>`
        """

        return self.get_json("/vnodes")

    def vnodes_create(self, names, desc=None, ssh_key=None, asynch=False):

        """
        Create new virtual nodes

        Args:
            names (Array): The names of the virtual nodes which should be
              unique desc(dict) Hash structured as described in
              :desc:`resources description<>` ssh_key(dict) SSH key pair
              to be copied on the virtual node (also adding the public key
              to .ssh/authorized_keys). Note that every SSH keys located
              on the physical node which hosts this virtual node are also
              copied in .ssh/ directory of the node (copied key have a
              specific filename prefix). The key are copied in .ssh/
              directory of SSH user (see {Distem::Daemon::Admin#SSH_USER}
              and Distem::Node::Container::SSH_KEY_FILENAME)
            asynch (bool): Asynchronious mode, check virtual node status
              to know when node is configured (see {#vnode_info})

        Returns:
            [Array] The virtual nodes description
              see :desc:`resources description<>`
        """

        if desc is None:
            desc = {}

        if ssh_key is None:
            ssh_key = {}

        data = {"names": names, "desc": desc, "ssh_key": ssh_key, "async": asynch}

        return self.post_json("/vnodes/", data=data)

    def vnodes_remove(self, names=None):

        """
        Remove the virtual vnodes, or every if names is nil


        Returns:
            [Array] Array of virtual nodes description
                (see :desc:`resources description<>`
        """
        if names is None:
            names = []

        return self.put_json(
            "/vnodes", data={"names": names, "type": "delete", "async": False}
        )

    def vnodes_start(self, names, asynch=False):

        """
        Start several virtual nodes

        A physical node (that have enought physical resources (CPU,...))
        will be automatically allocated if there is none set as +host+ at
        the moment The filesystem archive will be copied on the hosting
        physical node. A filesystem image *must* have been set (see
        {#vnode_create} or {#vfilesystem_create}/{#vfilesystem_update}).


        Args:
            names (Array): The names of the virtual nodes
            asynch (bool): Asynchronious mode, check virtual nodes status
              to know when node is configured (see {#vnode_info})

        Returns:
            dict of the virtual nodes description
              see :desc:`resources description<>`
        """

        desc = {"status": "RUNNING"}
        return self.put_json(
            "/vnodes", {"names": names, "desc": desc, "async": asynch, "type": "update"}
        )

    def vnodes_stop(self, names=None, asynch=False):

        """
        Stop given virtal nodes

        Args:
            names (Array): The name of the virtual nodes
            asynch (bool): Asynchronious mode, check virtual node status
                to know when node is configured (see {#vnode_info})

        Returns:
            dict of the description of the virtual nodes
        """

        if names is None:
            names = []

        return self.put_json(
            "/vnodes", {"names": names, "async": asynch, "type": "stop"}
        )

    def vnodes_freeze(self, names=None, asynch=False):

        """
        Freeze some virtual nodes


        Args:
            names (Array): The names of the virtual nodes
            asynch (bool): Asynchronious mode, check virtual node status
                to know when node is configured (see {#vnode_info})

        Returns:
            [Array] The virtual node descriptions
              see :desc:`resources description<>`
        """

        if names is None:
            names = []

        return self.put_json(
            "/vnodes", {"names": names, "async": asynch, "type": "freeze"}
        )

    def vnodes_unfreeze(self, names=None, asynch=False):

        """
        Unfreeze some virtual nodes


        Args:
            names (Array): The names of the virtual nodes
            asynch (bool): Asynchronious mode, check virtual node status
                to know when node is configured (see {#vnode_info})

        Returns:
            [Array] The virtual node descriptions
              see :desc:`resources description<>`
        """

        if names is None:
            names = []

        return self.put_json(
            "/vnodes", {"names": names, "async": asynch, "type": "unfreeze"}
        )

    def vnodes_execute(self, names, command):

        """
        Execute and get the result of a command on a set of virtual nodes


        Args:
            names (Array): Array of virtual nodes
            command (str): The command to be executed

        Returns:
            dict of the result of the command (one entry by vnode)
        """

        return self.post_json("/commands", {"names": names, "command": command})

    def vfilesystem_info(self, vnodename):

        """
        Retrieve informations about a virtual node filesystem


        Args:
            vnodename (str): The name of the virtual node

        Returns:
            dict of the virtual node filesystem informations
        """

        return self.get_json("/vnodes/%s/filesystem/" % (str(vnodename)))

    def vfilesystem_create(self, vnodename, desc):

        """
        Set up the filesystem of a virtual node


        Args:
            vnodename (str): The name of the virtual node
            desc (dict): Hash structured as described in
                :desc:`resources description<>`

        Returns:
            dict of the virtual Filesystem description
              see :desc:`resources description<>`
        """

        return self.post_json(
            "/vnodes/%s/filesystem/" % (str(vnodename)), {"desc": desc}
        )

    def vfilesystem_update(self, vnodename, desc):

        """
        Update the filesystem of a virtual node


        Args:
            vnodename (str): The name of the virtual node
            desc (dict): Hash structured as described in
                :desc:`resources description<>`

        Returns:
            dict of the virtual Filesystem description
              see :desc:`resources description<>`
        """

        return self.put_json("/vnodes/%s/filesystem/" % (str(vnodename)), data=desc)

    def viface_info(self, vnodename, vifacename):

        """
        Retrieve informations about a virtual
        network interface associated to a virtual node


        Args:
            vnodename (str): The name of the virtual node
            vifacename (str): The name of the virtual network interface

        Returns:
            dict of the virtual network interface description
              see :desc:`resources description<>`
        """

        return self.get_json("/vnodes/%s/ifaces/%s" % (str(vnodename), str(vifacename)))

    def viface_create(self, vnodename, name, desc):

        """
        Create a virtual network interface on the virtual node


        Args:
            vnodename (str): The name of the virtual node
            name (str): The name of the virtual network interface
                to be created (have to be unique on that virtual node)
            desc (dict): Hash structured as described in
                :desc:`resources description<>`

        Returns:
            dict of the virtual network interface description
              see :desc:`resources description<>`
        """

        return self.post_json(
            "/vnodes/%s/ifaces/" % (str(vnodename)), {"name": name, "desc": desc}
        )

    def viface_remove(self, vnodename, vifacename):

        """
        Remove a virtual network interface


        Args:
            vnodename (str): The name of the virtual node
            vifacename (str): The name of the network virtual interface

        Returns:
            dict of the virtual network interface description
              see :desc:`resources description<>`
        """

        return self.delete_json(
            "/vnodes/%s/ifaces/%s/" % (str(vnodename), str(vifacename)), data={}
        )

    def viface_update(self, vnodename, vifacename, desc=None):

        """
        Update a virtual network interface

        Disconnect (detach): the virtual network interface from
        any virtual network it's connected on if +desc+ is empty

        Args:
            vnodename (str): The name of the virtual node
            vifacename (str): The name of the virtual network interface
            desc (dict): Hash structured as described in
              :desc:`resources description<>`

        Returns:
            dict of the virtual network interface description
              see :desc:`resources description<>`
        """

        if desc is None:
            desc = {}

        return self.put_json(
            "/vnodes/%s/ifaces/%s" % (vnodename, vifacename), {"desc": desc}
        )

    def vcpu_create(self, vnodename, val, unit="mhz", corenb=1):

        """
        Set up a virtual CPU on the virtual node


        Args:
            vnodename( str): The name of the virtual node val(float): The
            frequency defined as a value in MHz or as a ratio
              (percentage of the physical core frequency).
            unit (str): Tell if val is a frequency or a ratio (allowed
              values are mhz and ration)
            corenb (Integer): The number of cores to allocate
              (need to have enough free ones on the physical node)

        Returns:
            dict of the virtual CPU description
              see :desc:`resources description<>`
        """

        desc = {"corenb": corenb, "val": val, "unit": unit}
        return self.post_json("/vnodes/%s/cpu" % (vnodename), data={"desc": desc})

    def vcpu_update(self, vnodename, val, unit="mhz"):

        """
        Update a virtual CPU on the virtual node
        This setting works on-the-fly (i.e. even
        if the virtual node is already running)

        Args:
            vnodename (str): The name of the virtual node
            val (float): The frequency defined as a value in MHz
                or as a ratio (percentage of the physical core frequency).
            unit (str): Tell if val is a frequency or
            a ratio (allowed values are mhz and ration)

        Returns:
            dict of the virtual CPU description
              see :desc:`resources description<>`
        """

        desc = {"val": val, "unit": unit}
        return self.put_json("/vnodes/%s/cpu" % (vnodename), {"desc": desc})

    def vcpu_remove(self, vnodename):

        """
        Removing a virtual CPU on the virtual node


        Args:
            vnodename (str): The name of the virtual node

        Returns:
            dict of the virtual CPU description
              see :desc:`resources description<>`
        """

        return self.delete_json("/vnodes/%s/cpu" % (vnodename), data={})

    def vcpu_info(self, vnodename):

        """
        Retrive information about a virtual node CPU


        Returns:
            dict of the virtual CPU description
              see :desc:`resources description<>`
        """

        return self.get_json("/vnodes/%s/cpu" % (vnodename))

    def vinput_update(self, vnodename, vifacename, desc=None):

        """
        Update the traffic description on the input of a specified
        virtual network interface The vtraffic description is updated
        on-the-fly (even if the virtual node is running) Reset the
        vtraffic description if +desc+ is empty


        Args:
            vnodename (str): The name of the virtual node
            vifacename (str): The name of the virtual network interface
            desc (dict): Hash structured as described in
              :desc:`resources description<>`

        Returns:
            dict of the virtual traffic description
              see :desc:`resources description<>`
        """

        if desc is None:
            desc = {}

        return self.put_json(
            "/vnodes/%s/ifaces/%s/input/" % (vnodename, vifacename), {"desc": desc}
        )

    def vinput_info(self, vnodename, vifacename):

        """
        Retrive the traffic description on
        the input of a specified virtual network interface


        Args:
            vnodename (str): The name of the virtual node
            vifacename (str): The name of the virtual network interface

        Returns:
            dict of the virtual traffic description
              see :desc:`resources description<>`
        """

        return self.get_json("/vnodes/%s/ifaces/%s/input" % (vnodename, vifacename))

    def voutput_update(self, vnodename, vifacename, desc=None):

        """
        Update the traffic description on the output of a specified
        virtual network interface The vtraffic description is updated
        on-the-fly (even if the virtual node is running) Reset the
        vtraffic description if +desc+ is empty


        Args:
            vnodename (str): The name of the virtual node
            vifacename (str): The name of the virtual network interface
            desc (dict): Hash structured as described in
                :desc:`resources description<>`

        Returns:
            dict of the virtual traffic description
              see :desc:`resources description<>`
        """

        if desc is None:
            desc = {}

        return self.put_json(
            "/vnodes/%s/ifaces/%s/output" % (vnodename, vifacename), {"desc": desc}
        )

    def voutput_info(self, vnodename, vifacename):

        """
        Retrive the traffic description on
        the output of a specified virtual network interface


        Args:
            vnodename (str): The name of the virtual node
            vifacename (str): The name of the virtual network interface

        Returns:
            dict of the virtual traffic description
              see :desc:`resources description<>`
        """

        return self.get_json("/vnodes/%s/ifaces/%s/output" % (vnodename, vifacename))

    def vmem_create(self, vnodename, mem, swap=None, hierarchy="v1"):

        """
        Create a new memory limitation

        Args:
            vnodename (str): The vnode's name to create
            mem (str): The required amount of RAM
            swap (str): The required amount of swap
            hierarchy (str): The hierarchy where memory controller
              is mounted (default to v1)

        Returns:
            dict of the memory limitation
        """

        if swap is None:
            swap = []

        desc = {"mem": mem, "swap": swap, "hierarchy": hierarchy}
        return self.post_json("/vnodes/%s/vmem" % (vnodename), {"desc": desc})

    def vmem_update(self, vnodename, desc):

        """
        Update a memory limitation

        Args:
            vnodename (str): The vnode's name to update
            desc (dict): The memory limitation description
        """

        return self.put_json("/vnodes/%s/vmem" % (vnodename), {"desc": desc})

    def get_json(self, route):
        return self.raw_request(
            method="get",
            route="http://%s:%s%s" % (self.serveraddr, self.port, route),
            data={},
        )

    def post_json(self, route, data):
        return self.raw_request(
            method="post",
            route="http://%s:%s%s" % (self.serveraddr, self.port, route),
            data=data,
        )

    def put_json(self, route, data):
        return self.raw_request(
            method="put",
            route="http://%s:%s%s" % (self.serveraddr, self.port, route),
            data=data,
        )

    def delete_json(self, route, data):
        return self.raw_request(
            method="delete",
            route="http://%s:%s%s" % (self.serveraddr, self.port, route),
            data=data,
        )

    def raw_request(self, method, route, data):
        logging.debug("method=%s, route=%s, data=%s", method, route, data)
        result = ""
        _data = copy.deepcopy(data)
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                _data[key] = json.dumps(_data[key], separators=(",", ":"))

        req = requests.Request(method, route, data=_data)
        prepped = req.prepare()
        response = self.client.send(prepped)

        if 200 <= response.status_code < 300:
            try:
                result = response.json()
            except ValueError:
                result = response.text
            return result
        else:
            err = response.headers.get("X-Application-Error-Code", "Unknown error")
            raise Exception(err)
