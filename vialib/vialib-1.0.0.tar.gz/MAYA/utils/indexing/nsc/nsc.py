from MAYA.VIA import uuid, uform, repos
from MAYA.utils import shepherding, roles
import sys
from  nsc_simple_query import NSCSimpleQuery

from pprint import pprint

NSC_ROLE = uuid._('~0165594120056b100c9bf802e15c6e69fe')
NSC_SEGMENT_ROLE = uuid._('~01288f0e708e9b100ab52c7c0e45475cb0')
NSC_BTREE_NODE_ROLE = uuid._('~014b0d3bb0ca6f100a815103c346700f2c')

class NSC:

    def __init__(self, r, nsc_uform=None, max_children=101, segment_size=100, ephemeral=False):
        self.r = r
        self.nsc = NavigableScalableCollection(self.r, nsc_uform, max_children, segment_size, ephemeral)

    def length(self):
        """ Compute the current deep_member_total_count, checking each
        inclusion recursively for consistency """

        deep_member_total_count = self.nsc.deep_total
        my_revision = self.nsc.revision
        running_count = 0

        modified_member_info = False
        node_uid = self.nsc.head_segment
        update_ufs = []
        while node_uid:
            node_uf = uform.UForm(node_uid, ['member_info',
                                             'members',
                                             'next_segment']) 
            node_uf = self.nsc.getAttrs(node_uf)
            members = node_uf['members'] or []
            member_info = node_uf['member_info'] or []
            
            dirty = False
            new_member_info = []
            i = 0
            while i < len(members):
                m = members[i]
                mi = member_info[i]
                i += 1
                if not mi:
                    running_count += 1
                    continue
                (deep_count, revision) = mi
                child_uf = uform.UForm(m, ['revision_number'])
                child_uf = self.nsc.getAttrs(child_uf)
                if child_uf['revision_number'] == revision:
                    running_count += deep_count
                    new_member_info.append(mi)
                else:
                    dirty = True
                    modified_member_info = True
                    child_n = NSC(self.r, m)
                    (reported_deep_count, reported_revision) = child_n.length()
                    running_count += reported_deep_count
                    new_member_info.append((reported_deep_count, 
                                            reported_revision))
            if dirty:
                uf = uform.UForm(node_uid, { 'member_info': new_member_info })
                update_ufs.append(uf)

            node_uid = node_uf['next_segment']
            
        if running_count != deep_member_total_count or modified_member_info:
            my_revision += 1
            uf = uform.UForm(self.nsc.nsc_uform, 
                             { 'revision_number': my_revision,
                               'deep_member_total_count': running_count })
            update_ufs.append(uf)
            self.nsc.revision = my_revision
            self.nsc.deep_total = running_count

        if update_ufs:
            self.nsc.startBatch()
            for uf in update_ufs:
                self.nsc.setAttrs(uf)
            self.nsc.commit()

        return (running_count, my_revision)
                
    def __len__(self):
        return self.length()[0]

    def __getitem__(self, idx):
        if idx < 0:
            idx = len(self) + idx
	q = NSCSimpleQuery(self.r, self.nsc.nsc_uform)
	x, node, i = q.find(idx)
	if x is None:
	    raise IndexError
	return x
   
    def __getslice__(self, i, j):
	slice_list = []

	try:
	    parent_path = self.nsc.deepConvert(i)
	except:
	    return slice_list

	n = NSCIterator(self)
	n.jump(parent_path)

	count = 0;
	slice_length = j - i

	try:
	    while count < slice_length:
		slice_list.append(n.next())
		count += 1
	except StopIteration:
	    pass
	
	return slice_list

    def __setitem__(self, idx, v):
	self.nsc.insert(idx, v)

    def __delitem__(self, idx):
	self.nsc.remove(idx)

    def __iter__(self):
	return NSCIterator(self)

    # shallow copy
    def __copy__(self):
	copy = NSC(self.r,
	           None,
	           self.nsc.btree_max_children,
		   self.nsc.preferred_segment_size)
	itr = NSCIterator(self)
	try:
	    while True:
		item = itr.next()
		copy.append(item)
	except StopIteration:
	    pass
	return copy
			

    def append(self, v):
	self.nsc.append(v)

    def extend(self, xs):
	for x in xs:
	    self.append(x)
	return

    def appendInclusion(self, v):
	n = v.nsc
	self.nsc.appendInclusion(n)

    def include(self, i, v):
	n = v.nsc
	self.nsc.include(i, n)

    def insert(self, i, v):
	self.nsc.insert(i, v)
	return
	
    def remove(self, idx):
	self.nsc.remove(idx)
	return

    def pop(self, i=None):
	if i == None:
	    l = len(self) - 1
	    tmp = self[l]
	    self.nsc.remove(l)
	    return tmp
	else:
	    tmp = self[i]
	    self.nsc.remove(i)
	    return tmp
	
    def index(self, v):
	idx = 0
	for val in self:
	    if val == v:
	        return idx
	    idx += 1
	return -1

    def count(self, v):
	n = 0
	for i in self:
	    if i == v:
		n += 1
	return n


class NSCIterator:

    def __init__(self, n):
	self.i = 0
	self.nsc = n.nsc
	self.child_iter = False
	self.stopped = False
	uf = uform.UForm(self.nsc.nsc_uform, ['members', 
                                              'member_info', 
                                              'next_segment',
                                              'head_segment'])
        uf = self.nsc.getAttrs(uf)
        head_segment = uf['head_segment']
	self.next_count = 0
        if head_segment == self.nsc.nsc_uform:
            self.current_segment = uf
        else:
	    uf = uform.UForm(head_segment, ['members', 
					    'member_info', 
					    'next_segment',
					    'head_segment'])
            self.current_segment = self.nsc.getAttrs(uf)

    def __iter__(self):
	return self


    def jump(self, parent_path):
	cur_parent, idx, shallow_idx = parent_path[0]
	nsc_query = NSCSimpleQuery(self.nsc.r, cur_parent)

	if not self.nsc.btree_root:
	    element, cur_node, i, mem_info, shallow_count, mem = nsc_query.findNode(idx, self.nsc.head_segment)
	else:
	    element, cur_node, i, mem_infm, shallow_count, mem = nsc_query.findNode(idx, self.nsc.btree_root)

	uf = uform.UForm(cur_node, ['members',
				    'member_info',
				    'next_segment'])
	self.current_segment = self.nsc.getAttrs(uf)
	self.i = mem

	if len(parent_path) > 1:
	    self.i += 1
	    next_parent, next_idx, next_shallow = parent_path[1]
	    child_nsc = NSC(self.nsc.r, next_parent)
	    self.child_iter = NSCIterator(child_nsc)
	    self.child_iter.jump(parent_path[1:])
	else:
	    return

    def next(self):
	self.next_count += 1
	if self.stopped : raise StopIteration
	if self.child_iter:
	    try:
		return self.child_iter.next()
	    except StopIteration:
		self.child_iter = False
	if self.i < len(self.current_segment['members']):
	    i = self.i
	    if self.current_segment['member_info'][i] == None:
		self.i += 1
		return self.current_segment['members'][i]
	    else:
		new_nsc = self.current_segment['members'][i]
		child_nsc = NSC(self.nsc.r, new_nsc)
		self.child_iter = NSCIterator(child_nsc)
		self.i += 1
		try:
		    return self.child_iter.next()
		except StopIteration:
		    self.child_iter = False
		    return self.next()
	elif self.current_segment['next_segment'] != None:
	    self.i = 1
	    uf = uform.UForm(self.current_segment['next_segment'], ['members',
								    'member_info',
								    'next_segment'])
	    self.current_segment = self.nsc.getAttrs(uf)
	    if self.current_segment['member_info'][0] == None:
	    	return self.current_segment['members'][0] 
	    else:
		new_nsc = self.current_segment['members'][0]
		child_nsc = NSC(self.nsc.r, new_nsc)
		self.child_iter = NSCIterator(child_nsc)
		try:
		    return self.child_iter.next()
		except StopIteration:
		    self.child_iter = False
		    return self.next()
	else:
	    self.stopped = True
	    raise StopIteration()
	

class NavigableScalableCollection:


    def getAttrs(self, uf):
        shepherding.waitForPresence(self.r, uf)
        self.uforms_read += 1
        return self.r.getAttr(uf)

    def getAttr(self, uu, attr):
        shepherding.waitForPresence(self.r, uu)
        self.uforms_read += 1
        return self.r.getAttr(uu, attr)

    def setAttrs(self, uf):
        #print "Adding to batch:", uf
        self.uforms_written += 1
	if uf.uuid not in self.batch:
	    self.batch[uf.uuid] = uf
	else:
	    cur_uf = self.batch[uf.uuid]
	    cur_uf.update(uf)
	return

    def setAttr(self, uu, attr, val):
        self.uforms_written += 1
	uf = uform.UForm(uu, [attr])
	uf[attr] = val
	if uu not in self.batch:
	    self.batch[uu] = uf
	else:
	    cur_uf = self.batch[uu]
	    cur_uf.update(uf)
        return

    def startBatch(self):
	self.batch = {}

    def commit(self):
	for uf in self.batch.values():
            if self.ephemeral:
                self.r.send([3009, uform.UForm(uf.uuid, {'do_not_shepherd' : True})])
            #print "Writing", uf
            self.r.send([9, uf])
	for i in self.batch.values():
            if self.ephemeral:
                self.r.recv()
	    self.r.recv()
	self.batch = {}

    def __init__(self, r,
                 nsc_uform=None,
                 preferred_btree_max_children=101,
                 preferred_segment_size=100,
                 name="Navigable Scalable Collection",
                 ephemeral=False):
	self.startBatch()
        self.uforms_read = 0
        self.uforms_written = 0

        self.ephemeral = ephemeral

        self.r = r
        self.nsc_uform = nsc_uform
        if not self.nsc_uform:
            self.create(preferred_segment_size, preferred_btree_max_children, name)
        uf = uform.UForm(self.nsc_uform,
                         ['head_segment',
                          'tail_segment',
                          'preferred_segment_size',
                          'revision_number',
                          'deep_member_total_count',
                          'shallow_member_total_count',
                          'btree_root',
                          'btree_max_children',
                          'btree_rightmost_nodes'])
        self.nsc_uform_contents = self.getAttrs(uf)
        self.head_segment = self.nsc_uform_contents['head_segment']
        self.tail_segment = self.nsc_uform_contents['tail_segment']
        self.preferred_segment_size = self.nsc_uform_contents['preferred_segment_size']
        self.revision = self.nsc_uform_contents['revision_number'] or 0
        self.deep_total = self.nsc_uform_contents['deep_member_total_count']
        self.shallow_total = self.nsc_uform_contents['shallow_member_total_count']
        self.btree_root = self.nsc_uform_contents['btree_root']
        self.btree_max_children = self.nsc_uform_contents['btree_max_children']
        self.btree_rightmost_nodes = self.nsc_uform_contents['btree_rightmost_nodes']
        self.btree_split_point = (self.btree_max_children - 1) / 2
        self.segment_split_point = (self.preferred_segment_size - 1) / 2 + 1
        uf = uform.UForm(self.head_segment,
                         ['members',
                          'member_info',
                          'next_segment',
                          'child_properties'])
        self.nsc_uform_contents = self.getAttrs(uf)
        self.head_members = uf['members'] or []
        self.head_member_info = uf['member_info'] or []
            
    def create(self, preferred_segment_size, preferred_btree_max_children, name):
        self.nsc_uform = uuid.UUID()
        uf = uform.UForm(self.nsc_uform,
                         {'head_segment' : self.nsc_uform,
                          'tail_segment' : self.nsc_uform,
                          'segment_of' : self.nsc_uform,
                          'preferred_segment_size' : preferred_segment_size,
                          'revision_number' : 1,
                          'deep_member_total_count' : 0,
                          'shallow_member_total_count' : 0,
                          'btree_max_children' : preferred_btree_max_children,
                          'members' : [],
                          'member_info' : [],
                          'child_properties' : [],
                          'roles' : [ NSC_ROLE, NSC_SEGMENT_ROLE ],
                          'name' : name,
                          'label' : "nsc"})
        self.setAttrs(uf)
	self.commit()
        #print "Created NSC:", self.nsc_uform
	
    def refresh(self):
        uf = uform.UForm(self.nsc_uform,
                         ['head_segment',
                          'tail_segment',
                          'preferred_segment_size',
                          'revision_number',
                          'deep_member_total_count',
                          'shallow_member_total_count',
                          'btree_root',
                          'btree_max_children',
                          'btree_rightmost_nodes'])
        self.nsc_uform_contents = self.getAttrs(uf)
        self.head_segment = self.nsc_uform_contents['head_segment']
        self.tail_segment = self.nsc_uform_contents['tail_segment']
        self.preferred_segment_size = self.nsc_uform_contents['preferred_segment_size']
        self.revision = self.nsc_uform_contents['revision_number'] or 0
        self.deep_total = self.nsc_uform_contents['deep_member_total_count']
        self.shallow_total = self.nsc_uform_contents['shallow_member_total_count']
        self.btree_root = self.nsc_uform_contents['btree_root']
        self.btree_max_children = self.nsc_uform_contents['btree_max_children']
        self.btree_rightmost_nodes = self.nsc_uform_contents['btree_rightmost_nodes']
        self.btree_split_point = (self.btree_max_children - 1) / 2
        self.segment_split_point = (self.preferred_segment_size - 1)/ 2 + 1
        uf = uform.UForm(self.head_segment,
                         ['members',
                          'member_info',
                          'next_segment',
                          'child_properties'])
        self.nsc_uform_contents = self.getAttrs(uf)
        self.head_members = uf['members'] or []
        self.head_member_info = uf['member_info'] or []

    def get_counts(self, info):
        info = info or []
        deep_count = reduce(lambda x, y: x + y, map(lambda x: (x or [1])[0], info))
        shallow_count = len(info)
        return deep_count, shallow_count
    
    def create_btree_root(self, left_child, right_child, left_deep_count, left_shallow_count):
        new_root_uf = uform.UForm()
        new_root_uf['children'] = [ left_child, right_child ]
        new_root_uf['deep_subtree_counts'] = [ left_deep_count ]
        new_root_uf['shallow_subtree_counts'] = [ left_shallow_count ]
        new_root_uf['roles'] = [ NSC_BTREE_NODE_ROLE ]
        self.setAttrs(new_root_uf)
        self.btree_root = new_root_uf.uuid
        return new_root_uf.uuid

    def create_segment(self,
                       uu,
                       members,
                       member_info,
                       previous_segment,
                       next_segment):
        new_segment_uf = uform.UForm(uu)
        new_segment_uf['members'] = members
        new_segment_uf['member_info'] = member_info
        new_segment_uf['previous_segment'] = previous_segment
        new_segment_uf['next_segment'] = next_segment
        new_segment_uf['segment_of'] = self.nsc_uform
        new_segment_uf['roles'] = [ NSC_SEGMENT_ROLE ]
        self.setAttrs(new_segment_uf)

    def create_node(self,
                    children,
                    deep_subtree_counts,
                    shallow_subtree_counts):
        new_node_uf = uform.UForm()
        new_node_uf['children'] = children
        new_node_uf['deep_subtree_counts'] = deep_subtree_counts
        new_node_uf['shallow_subtree_counts'] = shallow_subtree_counts
        new_node_uf['roles'] = [ NSC_BTREE_NODE_ROLE ]
        self.setAttrs(new_node_uf)
        return new_node_uf.uuid

    def split_segment(self,
                      members,
                      member_info,
                      previous_segment,
                      next_segment,
                      nsc_uf):
        # split existing contents
        members_to_left = members[:self.segment_split_point]
        members_to_right = members[self.segment_split_point:]
        member_info_to_left = member_info[:self.segment_split_point]
        member_info_to_right = member_info[self.segment_split_point:]

        left_segment = uuid.UUID()
        right_segment = uuid.UUID()

        # create the new left segment
        self.create_segment(left_segment,
                            members_to_left,
                            member_info_to_left,
                            previous_segment,
                            right_segment)

        # create the new right segment
        self.create_segment(right_segment,
                            members_to_right,
                            member_info_to_right,
                            left_segment,
                            next_segment)

        if not previous_segment:
            # contents of NSC u-form need to be updated, but don't
            # write back now; wait until all changes are ready, then
            # commit as one write to repository
            nsc_uf['head_segment'] = self.head_segment = left_segment
        return ((left_segment, member_info_to_left),
                (right_segment, member_info_to_right))

    def split_node(self,
                   children,
                   deep_subtree_counts,
                   shallow_subtree_counts):

        # split existing contents
        children_to_left = children[:self.btree_split_point + 1]
        children_to_right = children[self.btree_split_point + 1:]
        deep_subtree_counts_to_left = deep_subtree_counts[:self.btree_split_point]
        deep_subtree_counts_to_right = deep_subtree_counts[self.btree_split_point + 1:]
        shallow_subtree_counts_to_left = shallow_subtree_counts[:self.btree_split_point]
        shallow_subtree_counts_to_right = shallow_subtree_counts[self.btree_split_point + 1:]

        deep_count_to_promote = deep_subtree_counts[self.btree_split_point]
        shallow_count_to_promote = shallow_subtree_counts[self.btree_split_point]
        
        left_node = self.create_node(children_to_left,
                                     deep_subtree_counts_to_left,
                                     shallow_subtree_counts_to_left)
        right_node = self.create_node(children_to_right,
                                      deep_subtree_counts_to_right,
                                      shallow_subtree_counts_to_right)

        total_deep_subtree_count_to_left = reduce(lambda x,y: x+y,
                                                  deep_subtree_counts_to_left) + deep_count_to_promote
        total_shallow_subtree_count_to_left = reduce(lambda x,y: x+y,
                                                     shallow_subtree_counts_to_left) + shallow_count_to_promote
        total_deep_subtree_count_to_right = reduce(lambda x,y: x+y, deep_subtree_counts_to_right)
        total_shallow_subtree_count_to_right = reduce(lambda x,y: x+y, shallow_subtree_counts_to_right)

        return ((left_node, total_deep_subtree_count_to_left, total_shallow_subtree_count_to_left),
                (right_node, total_deep_subtree_count_to_right, total_shallow_subtree_count_to_right))

    # takes an index and traverses the nsc to find if the index refers to a location
    #which is located in another nsc within the structure. Returns the path of parents
    #down the tree to the final nsc and their offsets from the original index
    def deepConvert(self, deep_index):
	nsc_uf = self.getAttrs(uform.UForm(self.nsc_uform, ['head_segment',
	    						    'btree_root']))

	parent_path = []
	nsc_query = NSCSimpleQuery(self.r, self.nsc_uform)
	
	if not nsc_uf['btree_root']:
            element, cur_node, index, mem_info, shallow, mem = nsc_query.findNode(deep_index, nsc_uf['head_segment'])
	else:
            element, cur_node, index, mem_info, shallow, mem = nsc_query.findNode(deep_index, nsc_uf['btree_root'])
	
	parent_path.append((self.nsc_uform, deep_index, shallow))
	
	prev_element = element
	prev_node = cur_node
	prev_index = index
	
	recurse = True
	while recurse:
	    if mem_info:
		uf = self.getAttrs(uform.UForm(element, ['head_segment', 'btree_root']))
		if uf['btree_root'] != None:
		    element, cur_node, index, mem_info, shallow, mem = nsc_query.findNode(index, uf['btree_root'])
		    parent_path.append((prev_element, prev_index, shallow))
		    prev_element = element
		    prev_node = cur_node
		    prev_index = index
		elif uf['head_segment'] != None:
		    element, cur_node, index, mem_info, shallow, mem = nsc_query.findNode(index, uf['head_segment'])
		    parent_path.append((prev_element, prev_index, shallow))
		    prev_element = element
		    prev_node = cur_node
		    prev_index = index
		else:
		    recurse = False
	    else:
		recurse = False

	return parent_path

    # inserts an item into the nsc where it may be inserted into an inclusion which is 
    #deeper in the structure than the top level inclusion that the user called the insert on.
    #Then update all the NSC statistics and trees
    def deepInsert(self, idx, item):
	parent_path = self.deepConvert(idx)

	nsc_uform, index, shallow = parent_path[-1]

	ns = NavigableScalableCollection(self.r, nsc_uform)
	ns.insert(index, item)

	next_index = 1
	nscList = []
	for parent in parent_path[:-1]:
	    nsc_uform, offset, shallow = parent
	    next_nsc, next_offset, next_shallow = parent_path[next_index]
	    n = NavigableScalableCollection(self.r, nsc_uform)
	    seg, path, path_indices, ttl_seen = n.find_path_to_segment(offset - next_offset)
	    n.updatePath(path, path_indices, 1, offset - next_offset - ttl_seen)
	    next_index += 1
	
	self.refresh()
	return

    # includes an nsc into the structure where the actual location of the include may be 
    #within another nsc contained in the head structure the user called the include on.
    def deepInclude(self, idx, item):
	parent_path = self.deepConvert(idx)

	nsc_uform, index, shallow = parent_path[-1]

	n = NavigableScalableCollection(self.r, nsc_uform)
	n.include(index, item)

	next_index = 1
	for parent in parent_path[:-1]:
	    nsc_uform, offset, shallow = parent
	    next_nsc, next_offset, next_shallow = parent_path[next_index]
	    n = NavigableScalableCollection(self.r, nsc_uform)
	    seg, path, path_indices, ttl_seen = n.find_path_to_segment(offset - next_offset)
	    n.updatePath(path, path_indices, new_deep_count, offset - next_offset - ttl_seen)

	self.refresh()
	return

    # using the path provided, this updates the count values of all the btree nodes.
    #Then it updates the member info of the node which contains the inclusion, and increments
    #values in the head of the nsc
    def updatePath(self, path, path_indices, deep_count, member_location):
	while path:
	    node = path.pop()
	    node_idx = path_indices.pop()
	    children = node['children']
	    shallow_subtree_counts = node['shallow_subtree_counts']
	    deep_subtree_counts = node['deep_subtree_counts']
	    # only need to modify a count if child not at extreme
	    # right
	    if node_idx < len(children) - 1:
		node['shallow_subtree_counts'][node_idx] += 1
		node['deep_subtree_counts'][node_idx] += deep_count
		del node['children']
		self.setAttrs(node)
	
	segment_node = children[node_idx]
	uf = self.getAttrs(uform.UForm(segment_node, ['member_info']))	
	uf['member_info'][member_location][0] += deep_count
	self.setAttrs(uf)

	nsc_uf = self.getAttrs(uform.UForm(self.nsc_uform, ['shallow_member_total_count',
						            'deep_member_total_count',
						            'revision_number']))
	self.shallow_total += 1
	self.deep_total += deep_count 
	self.revision += 1
	nsc_uf['shallow_member_total_count'] = self.shallow_total
	nsc_uf['deep_member_total_count'] = self.deep_total 
	nsc_uf['revision_number'] = self.revision 
	self.setAttrs(nsc_uf)
	self.commit()

	return
	
    def appendUniversal(self, appendItem, new_deep_count):
	self.startBatch()
	nsc_uf = uform.UForm(self.nsc_uform)

        # get the current tail segment data
        uf = uform.UForm(self.tail_segment, ['members',
                                             'member_info',
                                             'previous_segment'])
        uf = self.getAttrs(uf)
        members = uf['members'] or []
        member_info = uf['member_info'] or []
        previous_segment = uf['previous_segment']

        # append the new item
        members.append(appendItem)
        member_info.append(new_deep_count)

        # there are a number of cases to deal with:
        # CASE 1: room in leaf segment, no need to split
        # CASE 2: need to split leaf segment, but no btree root yet
        # CASE 3: need to split leaf segment, and parent has enough room
        # CASE 4: need to split leaf segment, and parent node needs to
        # be split; continue splitting up rightmost nodes until we
        # find ancestor with enough room
        # CASE 5: as case 4, but all ancestor nodes are full; need to
        # create new root node
        if len(members) <= self.preferred_segment_size:
            # CASE 1: no need to split
            #print "CASE 1"
            uf['members'] = members
            uf['member_info'] = member_info
            self.setAttrs(uf)
        else:
            # cases 2+: no room in leaf, need to split tail segment
            # into two
            #print "CASE 2"
            (left_info, right_info) = self.split_segment(members,
                                                         member_info,
                                                         previous_segment,
                                                         None,
                                                         nsc_uf)
            left_segment, member_info_to_left = left_info
            right_segment, member_info_to_right = right_info

            # fix up tail segment pointer in head segment
            self.tail_segment = right_segment
            #print "RESET TAIL SEGMENT:", self.tail_segment
            nsc_uf['tail_segment'] = self.tail_segment

            # fix up previous segment pointer to new segment to its
            # right
            if previous_segment:
                self.setAttr(previous_segment, 'next_segment', left_segment)

            deep_count_to_left, shallow_count_to_left = self.get_counts(member_info_to_left)

            if not self.btree_root:
                # CASE 2: no btree root yet, create now, point to two
                # segments
		# print "CASE 2: NEED TO CREATE NEW ROOT"
                self.create_btree_root(left_segment,
                                       right_segment,
                                       deep_count_to_left,
                                       shallow_count_to_left)
                nsc_uf['btree_root'] = self.btree_root
                nsc_uf['btree_rightmost_nodes'] = self.btree_rightmost_nodes = []

            else:
                # case 3+: tree has root, thus at least one btree level

                # create list of rightmost nodes back up the tree,
                # include btree root
                rightmost = [self.btree_root] + self.btree_rightmost_nodes

                n = rightmost.pop()
                uf = self.getAttrs(uform.UForm(n, ['children',
                                                   'shallow_subtree_counts',
                                                   'deep_subtree_counts']))
                children = uf['children']
                shallow_subtree_counts = uf['shallow_subtree_counts']
                deep_subtree_counts = uf['deep_subtree_counts']

                # fix up last child, then add new child
                children[-1] = left_segment
                children.append(right_segment)

                deep_subtree_counts.append(deep_count_to_left)
                shallow_subtree_counts.append(shallow_count_to_left)

                if len(children) <= self.btree_max_children:
		    #print "CASE 3 PARENT HAS ROOM"
                    # CASE 3: parent node has enough room
                    self.setAttrs(uf)
                else:
                    # case 4+: traverse up tree, splitting nodes until
                    # ancestor found with enough room, or root of tree
                    # is reached
                    
                    (left_info, right_info) = self.split_node(children,
                                                              deep_subtree_counts,
                                                              shallow_subtree_counts)
                    left_node, deep_count_to_left, shallow_count_to_left = left_info
                    right_node, deep_count_to_right, shallow_count_to_right = right_info

                    done = False
                    rightmost_nodes_idx = -1
                
                    # traverse all the way up the tree to the root, if
                    # necessary
                    while rightmost:
                        # update rightmost nodes list in place
                        self.btree_rightmost_nodes[rightmost_nodes_idx] = right_node
                        rightmost_nodes_idx -= 1

                        n = rightmost.pop()
                        
                        uf = self.getAttrs(uform.UForm(n, ['children',
                                                           'shallow_subtree_counts',
                                                           'deep_subtree_counts']))
                        children = uf['children']
                        shallow_subtree_counts = uf['shallow_subtree_counts']
                        deep_subtree_counts = uf['deep_subtree_counts']

                        # fix up last child, then add new child
                        children[-1] = left_node
                        children.append(right_node)

                        shallow_subtree_counts.append(shallow_count_to_left)
                        deep_subtree_counts.append(deep_count_to_left)

                        if len(children) <= self.btree_max_children:
                            # CASE 4: an ancestor node has enough room
			    #print "CASE 4 AN ANCESTOR HAS ROOM"
                            self.setAttrs(uf)
                            nsc_uf['btree_rightmost_nodes'] = self.btree_rightmost_nodes
                            done = True
                            break
                        else:
                            (left_info, right_info) = self.split_node(children,
                                                                      deep_subtree_counts,
                                                                      shallow_subtree_counts)
                            left_node, deep_count_to_left, shallow_count_to_left = left_info
                            right_node, deep_count_to_right, shallow_count_to_right = right_info

                    if not done:
                        # CASE 5: not done, need to create new root node
                        self.btree_rightmost_nodes = [right_node] + self.btree_rightmost_nodes
                        #print "CASE 5 NEED TO CREATE NEW ROOT"
                        self.create_btree_root(left_node,
                                               right_node,
                                               deep_count_to_left,
                                               shallow_count_to_left)
                        nsc_uf['btree_root'] = self.btree_root
                        nsc_uf['btree_rightmost_nodes'] = self.btree_rightmost_nodes

        # fix up head segment info
        self.shallow_total += 1
	if new_deep_count:
	    deep_total_add = new_deep_count[0]
	else:
	    deep_total_add = 1

        self.deep_total += deep_total_add 
        self.revision += 1
        nsc_uf['shallow_member_total_count'] = self.shallow_total
        nsc_uf['deep_member_total_count'] = self.deep_total 
        nsc_uf['revision_number'] = self.revision
        self.setAttrs(nsc_uf)
	self.commit()

	return 

    def appendInclusion(self, item):
	self.uforms_read = 0
	self.uforms_written = 0

	# check to see if the item to be appended is another nsc
	try:
	    uf = uform.UForm(item.nsc_uform, ['roles', 'deep_member_total_count', 'revision_number'])
	    uf = item.getAttrs(uf)	
	except:
	    print "append failed: appended node not a valid nsc"
	    return False
	
	if NSC_ROLE in uf['roles']:
	    new_deep_count = (uf['deep_member_total_count'], uf['revision_number'])
	else:
	    print "not nsc head"
	    return False
        
	self.appendUniversal(item.nsc_uform, new_deep_count)

	return

    def append(self, item):
        #print "APPEND:", item

        self.uforms_read = 0
        self.uforms_written = 0
        
	nsc_uform = self.appendUniversal(item, None)

    def find_path_to_segment(self, idx):
        # is index out of bounds?
        if idx >= self.shallow_total:
            return None, None, None, -1

        # only one segment
        if not self.btree_root:
            head_contents = self.getAttrs(uform.UForm(self.head_segment,
                                                      ['members',
                                                       'member_info',
                                                       'previous_segment',
                                                       'next_segment']))
            return head_contents, None, None, 0

        total = 0
        cur_node = self.btree_root

        nodes_on_path = []
        node_indices = []
        
        # traverse tree, starting at root
        while cur_node:

            # get contents of u-form; either node or segment
            cur_node_contents = self.getAttrs(uform.UForm(cur_node,
                                                          ['children',
                                                           'shallow_subtree_counts',
                                                           'deep_subtree_counts',
                                                           'members',
                                                           'member_info',
                                                           'previous_segment',
                                                           'next_segment']))
            children = cur_node_contents['children']
            counts = cur_node_contents['shallow_subtree_counts']

            # no values for 'deep_subtree_counts' indicate this is a leaf
            # segment; just return item at appropriate position
            if not counts:
                # get rid of extraneous attributes
                del cur_node_contents['children']
                del cur_node_contents['shallow_subtree_counts']
                del cur_node_contents['deep_subtree_counts']

                return cur_node_contents, nodes_on_path, node_indices, total

            # get rid of attrs for segments
            del cur_node_contents['members']
            del cur_node_contents['member_info']
            del cur_node_contents['previous_segment']
            del cur_node_contents['next_segment']

            # have btree node; iterate over all counts
            i = 0
            while i < len(counts):
                cur_count = counts[i]
                # if count now too large, go to child on left...
                if idx < total + cur_count:
                  break
                # update total seen, go right
                total += cur_count
                i += 1

            nodes_on_path.append(cur_node_contents)
            node_indices.append(i)

            # traverse to next node; either some count's left child,
            # or the rightmost child
            cur_node = children[i]

    def insertUniversal(self, idx, insert_item, new_deep_count):
	self.startBatch()
	nsc_uf = uform.UForm(self.nsc_uform)
	
        # find path all the way down the tree to leaf segment
        segment, path, path_indices, total_seen = self.find_path_to_segment(idx)
        if not segment:
            return False

        # retrieve segment contents
        members = segment['members'] or []
        deep_member_info = segment['member_info'] or []
        previous_segment = segment['previous_segment']
        next_segment = segment['next_segment']

        # insert the new item
        didx = idx - total_seen
        members.insert(didx, insert_item)
        deep_member_info.insert(didx, new_deep_count)

        # there are a number of cases to deal with:
        # CASE 1: room in leaf segment, no need to split
        # CASE 2: need to split leaf segment, but no btree root yet
        # CASE 3: need to split leaf segment, and parent has enough room
        # CASE 4: need to split leaf segment, and parent node needs to
        # be split; continue splitting up path to root until we find
        # ancestor with enough room
        # CASE 5: as case 4, but all ancestor nodes are full; need to
        # create new root node
        if len(members) <= self.preferred_segment_size:
            # CASE 1: room in leaf node, no need to split
            segment['members'] = members
            segment['member_info'] = deep_member_info
            self.setAttrs(segment)
        else:
            # cases 2+: no room in leaf, need to split this segment
            # into two
            (left_info, right_info) = self.split_segment(members,
                                                         deep_member_info,
                                                         previous_segment,
                                                         next_segment,
                                                         nsc_uf)
            left_segment, member_info_to_left = left_info
            right_segment, member_info_to_right = right_info

            if next_segment:
                # fix up next segment pointer to new segment to its left
                self.setAttr(next_segment, 'previous_segment', right_segment)
            else:
                # fix up pointer to tail segment in head
                self.tail_segment = right_segment #print "RESET TAIL SEGMENT:", self.tail_segment
                nsc_uf['tail_segment'] = self.tail_segment

            # fix up previous segment pointer to new segment to its
            # right
            if previous_segment:
                self.setAttr(previous_segment, 'next_segment', left_segment)

            deep_count_to_left, shallow_count_to_left = self.get_counts(member_info_to_left)

            if not self.btree_root:
                # CASE 2: no btree root yet, create now, point to two
                # segments
                self.create_btree_root(left_segment,
                                       right_segment,
                                       deep_count_to_left,
                                       shallow_count_to_left)
                nsc_uf['btree_root'] = self.btree_root        

            else:
                # case 3+: tree has root, thus at least one btree level

                # pop off first node, immediate parent of segment;
                # deal with this first by adding new child
                node = path.pop()
                node_idx = path_indices.pop()
                children = node['children']
                shallow_subtree_counts = node['shallow_subtree_counts']
                deep_subtree_counts = node['deep_subtree_counts']

                # existing segment is updated, then new segment is
                # added to its right
                children[node_idx] = left_segment
                children.insert(node_idx + 1, right_segment)
                # new count entries (keys) need to be added, do so to
                # immediate left of existing ones, with counts to left
                # of segment just added
                deep_subtree_counts.insert(node_idx, deep_count_to_left)
                shallow_subtree_counts.insert(node_idx, shallow_count_to_left)

                node_idx += 1
                
                # may need to update count to right of just added
                # segment, if not added at end of child pointers; this
                # count will be what the original total would have
                # been if no split occurred, less the count to the
                # left of just added segment
                if node_idx < len(children) - 1:
                    shallow_subtree_counts[node_idx] += 1 - shallow_count_to_left
                    deep_subtree_counts[node_idx] += 1 - deep_count_to_left

                if len(children) <= self.btree_max_children:
                    # CASE 3: parent node has enough room
		    #print "insert: CASE 3 PARENT HAS ROOM"
                    self.setAttrs(node)
                else:
                    # cases 4+: parent node needs to be split;
                    # continue splitting up the tree until we find a
                    # node not full, or need to create new root

                    (left_info, right_info) = self.split_node(children,
                                                              deep_subtree_counts,
                                                              shallow_subtree_counts)
                    left_node, deep_count_to_left, shallow_count_to_left = left_info
                    right_node, deep_count_to_right, shallow_count_to_right = right_info

                    done = False
                    rightmost_nodes_idx = -1
                    rightmost_nodes_modified = False

                    # traverse all the way up the tree to the root, if
                    # necessary
                    while path:
                        # if the split node was a rightmost node, need
                        # to update rightmost nodes list (in place)
                        if node.uuid == self.btree_rightmost_nodes[rightmost_nodes_idx]:
                            self.btree_rightmost_nodes[rightmost_nodes_idx] = right_node
                            rightmost_nodes_modified = True
                        rightmost_nodes_idx -= 1
                        
                        node = path.pop()
                        node_idx = path_indices.pop()

                        children = node['children']
                        shallow_subtree_counts = node['shallow_subtree_counts']
                        deep_subtree_counts = node['deep_subtree_counts']
                        
                        # existing segment is updated, then new segment is
                        # added to its right
                        children[node_idx] = left_node
                        children.insert(node_idx + 1, right_node)
                        shallow_subtree_counts.insert(node_idx, shallow_count_to_left)
                        deep_subtree_counts.insert(node_idx, deep_count_to_left)
                        node_idx += 1
                        if node_idx < len(children) - 1:
                            shallow_subtree_counts[node_idx] += 1 - shallow_count_to_left
                            deep_subtree_counts[node_idx] += 1 - deep_count_to_left

                        if len(children) <= self.btree_max_children:
                            # CASE 4: an ancestor node has enough room
			    #print "insert: CASE 4 Ancestor has room"
                            self.setAttrs(node)
                            done = True
                            break
                        else:
                            (left_info, right_info) = self.split_node(children,
                                                                      deep_subtree_counts,
                                                                      shallow_subtree_counts)
                            left_node, deep_count_to_left, shallow_count_to_left = left_info
                            right_node, deep_count_to_right, shallow_count_to_right = right_info

                    if not done:
                        # CASE 5: not done, need to create new root node
                        self.btree_rightmost_nodes = [right_node] + self.btree_rightmost_nodes
                        rightmost_nodes_modifified = True
                        #print "insert CASE 5 NEED TO CREATE NEW ROOT"
                        self.create_btree_root(left_node,
                                               right_node,
                                               deep_count_to_left,
                                               shallow_count_to_left)
                        nsc_uf['btree_root'] = self.btree_root

                    # check if we need to write back rightmost nodes to nsc u-form
                    if rightmost_nodes_modified:
                        nsc_uf['btree_rightmost_nodes'] = self.btree_rightmost_nodes
	
	if new_deep_count:
	    deep_count_add = new_deep_count[0]
	else:
	    deep_count_add = 1

        # fix up counts all the way up the rest of the tree
        while path:
            node = path.pop()
            node_idx = path_indices.pop()
	    children = node['children']
            shallow_subtree_counts = node['shallow_subtree_counts']
            deep_subtree_counts = node['deep_subtree_counts']
            # only need to modify a count if child not at extreme
            # right
            if node_idx < len(children) - 1:
                node['shallow_subtree_counts'][node_idx] += 1
                node['deep_subtree_counts'][node_idx] += deep_count_add
                del node['children']
                self.setAttrs(node)

        # fix up head segment info
        self.shallow_total += 1

        self.deep_total += deep_count_add 
        self.revision += 1
        nsc_uf['shallow_member_total_count'] = self.shallow_total
        nsc_uf['deep_member_total_count'] = self.deep_total
        nsc_uf['revision_number'] = self.revision
        self.setAttrs(nsc_uf)
	self.commit()

	return

    def include(self, idx, item):
        self.uforms_read = 0
        self.uforms_written = 0

        # insert at end (index of -1) equals append
        if idx == -1 or idx >= self.shallow_total:
            self.appendInclusion(item)
            return True

	try:
	    uf = uform.UForm(item.nsc_uform, ['roles', 'deep_member_total_count', 'revision_number'])
	    uf = item.getAttrs(uf)
	except:
	    print "insert failed: inserted node not a valid nsc"
	    return False
	
	if NSC_ROLE in uf['roles']:
	    new_deep_count = (uf['deep_member_total_count'], uf['revision_number'])
	else:
	    print "not nsc head"
	    return False

	self.insertUniversal(idx, item.nsc_uform, new_deep_count)

        return True

    def insert(self, idx, item):
        self.uforms_read = 0
        self.uforms_written = 0

        # insert at end equals append
        if idx == -1 or idx >= self.shallow_total:
            self.append(item)
            return True
	
	self.insertUniversal(idx, item, None)

        return True

    def merge_segments(self, segment1, segment2):
        s1_members = segment1['members']
        s2_members = segment2['members']
        s1_member_info = segment1['member_info']
        s2_member_info = segment2['member_info']
        if len(s1_members) + len(s2_members) <= self.preferred_segment_size:
            s1_members.extend(s2_members)
            s1_member_info.extend(s2_member_info)
            next_segment = segment2['next_segment']
            segment1['next_segment'] = next_segment
            self.setAttrs(segment1)
            if next_segment:
                self.setAttr(next_segment, 'previous_segment', segment1.uuid)
            return (segment1, None)
        else:
            all_members = s1_members + s2_members
            all_member_info = s1_member_info + s2_member_info
            split = len(all_members) / 2
            segment1['members'] = s1_members = all_members[:split]
            segment2['members'] = s2_members = all_members[split:]
            segment1['member_info'] = s1_member_info = all_member_info[:split]
            segment2['member_info'] = s2_member_info = all_member_info[split:]
            self.setAttrs(segment1)
            self.setAttrs(segment2)
            return (segment1, segment2)

    def merge_nodes(self,
                    node1, total_node1_deep_count, total_node1_shallow_count,
                    node2, total_node2_deep_count, total_node2_shallow_count):

        n1_children = node1['children']
        n2_children = node2['children']
        n1_deep_counts = node1['deep_subtree_counts']
        n2_deep_counts = node2['deep_subtree_counts']
        n1_shallow_counts = node1['shallow_subtree_counts']
        n2_shallow_counts = node2['shallow_subtree_counts']

        # need to know counts of last child of node 1
        n1_rightmost_deep_count = total_node1_deep_count - reduce(lambda x, y: x + y, n1_deep_counts)
        n1_rightmost_shallow_count = total_node1_shallow_count - reduce(lambda x, y: x + y, n1_shallow_counts)


        if len(n1_children) + len(n2_children) <= self.btree_max_children:
            # children will fit in one node

            n1_children.extend(n2_children)

            # this is why we needed counts of node 1's rightmost child; need to fill "gaps"
            n1_deep_counts += [ n1_rightmost_deep_count ] + n2_deep_counts
            n1_shallow_counts += [ n1_rightmost_shallow_count ] + n2_shallow_counts

            self.setAttrs(node1)

            if total_node2_deep_count != None:
                # want total counts across both nodes
                total_deep_count = total_node1_deep_count + total_node2_deep_count
                total_shallow_count = total_node1_shallow_count + total_node2_shallow_count
                return ((node1, total_deep_count, total_shallow_count), (None, None, None))
            else:
                # left node now rightmost node of parent, so don't
                # care about counts
                return ((node1, None, None), (None, None, None))

        else:
            # split children across both nodes

            all_children = n1_children + n2_children

            # make sure to fill "gaps" at extreme right of node 1
            all_deep_counts = n1_deep_counts + [ n1_rightmost_deep_count ] + n2_deep_counts
            all_shallow_counts = n1_shallow_counts + [ n1_rightmost_shallow_count ] + n2_shallow_counts
            
	    split = len(all_children) / 2
            node1['children'] = n1_children = all_children[:split]
            node2['children'] = n2_children = all_children[split:]

            # will eventually discard last counts of node 1
            node1['deep_subtree_counts'] = n1_deep_counts = all_deep_counts[:split]
            node2['deep_subtree_counts'] = n2_deep_counts = all_deep_counts[split:]

            node1['shallow_subtree_counts'] = n1_shallow_counts = all_shallow_counts[:split]
            node2['shallow_subtree_counts'] = n2_shallow_counts = all_shallow_counts[split:]

            # determine total counts at node 1, then discard the last
            # counts
            new_total_node1_deep_count = reduce(lambda x, y: x + y, n1_deep_counts)
            new_total_node1_shallow_count = reduce(lambda x, y: x + y, n1_shallow_counts)
            n1_deep_counts.pop()
            n1_shallow_counts.pop()

            if total_node2_deep_count != None:
                # the counts of node 2 have to be the total counts less
                # the counts at node 1
                total_deep_counts = total_node1_deep_count + total_node2_deep_count
                total_shallow_counts = total_node1_shallow_count + total_node2_shallow_count
                new_total_node2_deep_count = total_deep_counts - new_total_node1_deep_count
                new_total_node2_shallow_count = total_shallow_counts - new_total_node1_shallow_count
            else:
                # right node is rightmost node of parent, no need for
                # counts
                new_total_node2_deep_count = None
                new_total_node2_shallow_count = None

            self.setAttrs(node1)
            self.setAttrs(node2)

            return ((node1, new_total_node1_deep_count, new_total_node1_shallow_count),
                    (node2, new_total_node2_deep_count, new_total_node2_shallow_count))

    def removeUniversal(self, idx, item):
	self.startBatch()

	nsc_uf = uform.UForm(self.nsc_uform)

        # no members, nothing to delete
        if idx < 0 or idx >= self.shallow_total or self.shallow_total == 0:
            return False

        # set this up for eventual writeback
        nsc_uf = uform.UForm(self.nsc_uform)

        # find path all the way down the tree to leaf segment
        segment, path, path_indices, total_seen = self.find_path_to_segment(idx)
        if not segment:
            return False

        # retrieve segment contents
        members = segment['members']
        deep_member_info = segment['member_info']
        previous_segment = segment['previous_segment']
        next_segment = segment['next_segment']

        # determine relative offset of member in segment
        didx = idx - total_seen

        # check for item match (null matches anything)
        if item and item != members[didx]:
            return False

        # remove member from segment, including info
	if deep_member_info[didx]:
	    deep_member_remove = deep_member_info[didx][0]
	else:
	    deep_member_remove = 1

        del members[didx]
        del deep_member_info[didx]

        # cases to deal with:
        # CASE 1: leaf segment size still at or above minimum, no need
        # to merge
        # CASE 2: leaf segment size below minimum, but it is the only
        # segment (head segment)
        # CASE 3: need to merge with sibling, parent size still
        # minimum or above
        # CASE 4: need to merge with sibling, parent node needs to
        # merge; continue until no merge needed
        # CASE 5: as case 4, but merge continues to root, which is
        # deleted, and tree reduces in height
        if len(members) >= self.segment_split_point:
            # CASE 1: no need to merge leaf
            segment['members'] = members
            segment['member_info'] = deep_member_info
            self.setAttrs(segment)
        elif segment.uuid == self.head_segment and not next_segment:
            # CASE 2: head segment only segment
            segment['members'] = members
            segment['member_info'] = deep_member_info
            self.setAttrs(segment)
        else:
            # CASE 3+: need to merge with sibling; merging may split
            # segment contents between existing segments, or cause one
            # of the segments to be removed

            # get immediate parent, and index of segment within
            # parent's children
            node = path.pop()
            cur_node_idx = path_indices.pop()
            children = node['children']

            # indices of siblings of current node
            prev_segment_idx = cur_node_idx - 1
            next_segment_idx = cur_node_idx + 1

            # determine which segment to merge with; should be the one
            # with least members
            # NOTE: there should be at least one sibling, or there is
            # an error
            prev_segment_len = sys.maxint
            next_segment_len = sys.maxint
            if prev_segment_idx >= 0:
                prev_contents = self.getAttrs(uform.UForm(children[prev_segment_idx],
                                                          ['members',
                                                           'member_info',
                                                           'previous_segment',
                                                           'next_segment']))
                prev_members = prev_contents['members']
                prev_segment_len = len(prev_members)
            if next_segment_idx < len(children):
                next_contents = self.getAttrs(uform.UForm(children[next_segment_idx],
                                                          ['members',
                                                           'member_info',
                                                           'previous_segment',
                                                           'next_segment']))
                next_members = next_contents['members']
                next_segment_len = len(next_members)

            # do the merge; will get back a left segment, may or may
            # not get back right segment
            if next_segment_len < prev_segment_len:
                # merge with next segment
                right_segment_uuid = next_segment
                left_segment, right_segment = self.merge_segments(segment, next_contents)
                left_node_idx = cur_node_idx
                right_node_idx = cur_node_idx + 1
            else:
                # merge with previous segment
                right_segment_uuid = segment.uuid
                left_segment, right_segment = self.merge_segments(prev_contents, segment)
                left_node_idx = cur_node_idx - 1
                right_node_idx = cur_node_idx

            if right_segment:
                # have not eliminated a segment, so just need to
                # update counts of immediate parent node here
                # (automatically case 3)
                deep_count_to_left, shallow_count_to_left = self.get_counts(left_segment['member_info'])
                node['deep_subtree_counts'][left_node_idx] = deep_count_to_left
                node['shallow_subtree_counts'][left_node_idx] = shallow_count_to_left
                # only need to update right child counts if not last child
                if right_node_idx < len(children) - 1:
                    deep_count_to_right, shallow_count_to_right = self.get_counts(right_segment['member_info'])
                    node['deep_subtree_counts'][right_node_idx] = deep_count_to_right
                    node['shallow_subtree_counts'][right_node_idx] = shallow_count_to_right
                self.setAttrs(node)
            else:
                # no right segment, so one segment has been
                # eradicated; modify parent, and fix ancestors if
                # needed

                del children[right_node_idx]
                # shift counts over one to the left
                del node['deep_subtree_counts'][left_node_idx]
                del node['shallow_subtree_counts'][left_node_idx]
                # left node may now be rightmost node after delete;
                # only need to update counts if otherwise
                if left_node_idx < len(children) - 1:
                    deep_count_to_left, shallow_count_to_left = self.get_counts(left_segment['member_info'])
                    node['deep_subtree_counts'][left_node_idx] = deep_count_to_left
                    node['shallow_subtree_counts'][left_node_idx] = shallow_count_to_left

                # need to modify tail segment pointer if tail segment
                # has been removed
                if right_segment_uuid == self.tail_segment:
                    self.tail_segment = left_segment.uuid
                    nsc_uf['tail_segment'] = self.tail_segment

                if len(children) > self.btree_split_point:
                    # CASE 3: parent node still big enough
                    self.setAttrs(node)
                else:
                    # cases 4+: parent node needs to be merged with a
                    # sibling; continue merging up the tree until we
                    # find a node that is large enough, or we reach
                    # the root (and possibly have to reduce the height
                    # of the tree); as for segments, merging may
                    # result in one of the nodes being removed

                    # need flag to tell us if whether we've found an
                    # ancestor that remains large enough
                    done = False

                    # may need to modify rightmost nodes as we modify
                    # the tree
                    rightmost_nodes_idx = -1
                    rightmost_nodes_modified = False

                    while path:
                        # get parent node of current node, and index
                        # of current node as child of this parent node
                        parent_node = path.pop()
                        cur_node_idx = path_indices.pop()
                        parent_children = parent_node['children']

                        # indices of siblings of current node
                        prev_node_idx = cur_node_idx - 1
                        next_node_idx = cur_node_idx + 1

                        # determine which sibling has least children,
                        # and choose this one to merge with
                        prev_node_len = sys.maxint
                        next_node_len = sys.maxint
                        if prev_node_idx >= 0:
                            prev_node_contents = self.getAttrs(uform.UForm(parent_children[prev_node_idx],
                                                                           ['children',
                                                                            'shallow_subtree_counts',
                                                                            'deep_subtree_counts']))
                            prev_node_children = prev_node_contents['children']
                            prev_node_len = len(prev_node_children)
                        if next_node_idx < len(parent_children):
                            next_node_contents = self.getAttrs(uform.UForm(parent_children[next_node_idx],
                                                                           ['children',
                                                                            'shallow_subtree_counts',
                                                                            'deep_subtree_counts']))
                            next_node_children = next_node_contents['children']
                            next_node_len = len(next_node_children)

                        # do the merge; will get back left node, maybe
                        # a right node
                        if next_node_len < prev_node_len:
                            # choose right sibling
                            right_node_uuid = parent_children[next_node_idx]
                            total_node_deep_count = parent_node['deep_subtree_counts'][cur_node_idx] - 1
                            total_node_shallow_count = parent_node['shallow_subtree_counts'][cur_node_idx] - 1
                            # if next node is last child, no counts
                            if next_node_idx < len(parent_children) - 1:
                                total_next_node_deep_count = parent_node['deep_subtree_counts'][next_node_idx]
                                total_next_node_shallow_count = parent_node['shallow_subtree_counts'][next_node_idx]
                            else:
                                total_next_node_deep_count = None
                                total_next_node_shallow_count = None
                            left_node_info, right_node_info = self.merge_nodes(node,
                                                                               total_node_deep_count,
                                                                               total_node_shallow_count,
                                                                               next_node_contents,
                                                                               total_next_node_deep_count,
                                                                               total_next_node_shallow_count)
                            left_node_idx = cur_node_idx
                            right_node_idx = next_node_idx
                        else:
                            # choose left sibling
                            right_node_uuid = node.uuid
                            total_prev_node_deep_count = parent_node['deep_subtree_counts'][prev_node_idx]
                            total_prev_node_shallow_count = parent_node['shallow_subtree_counts'][prev_node_idx]
                            # if current node is last child, no counts
                            if cur_node_idx < len(parent_children) - 1:
                                total_node_deep_count = parent_node['deep_subtree_counts'][cur_node_idx] - 1
                                total_node_shallow_count = parent_node['shallow_subtree_counts'][cur_node_idx] - 1
                            else:
                                total_node_deep_count = None
                                total_node_shallow_count = None
                            left_node_info, right_node_info = self.merge_nodes(prev_node_contents,
                                                                               total_prev_node_deep_count,
                                                                               total_prev_node_shallow_count,
                                                                               node,
                                                                               total_node_deep_count,
                                                                               total_node_shallow_count)
                            left_node_idx = prev_node_idx
                            right_node_idx = cur_node_idx

                        left_node, deep_count_to_left, shallow_count_to_left = left_node_info
                        right_node, deep_count_to_right, shallow_count_to_right = right_node_info

                        if right_node:
                            # have maintained both nodes; parent node
                            # remains the same in size, so we must be
                            # done after fixing parent up
                            parent_node['deep_subtree_counts'][left_node_idx] = deep_count_to_left
                            parent_node['shallow_subtree_counts'][left_node_idx] = shallow_count_to_left
                            if right_node_idx < len(parent_children) - 1:
                                parent_node['deep_subtree_counts'][right_node_idx] = deep_count_to_right
                                parent_node['shallow_subtree_counts'][right_node_idx] = shallow_count_to_right
                            self.setAttrs(parent_node)
                            done = True
                            break

                        # at this point, we have determined that the
                        # merge caused the removal of the right node

                        # need to check rightmost nodes here; the node
                        # removed may have been a rightmost node
                        right_child_uuid = parent_children[right_node_idx]
                        if right_child_uuid == self.btree_rightmost_nodes[rightmost_nodes_idx]:
                            self.btree_rightmost_nodes[rightmost_nodes_idx] = left_node.uuid
                            rightmost_nodes_modified = True

                        del parent_children[right_node_idx]

                        # shift node counts one over to the left
                        del parent_node['deep_subtree_counts'][left_node_idx]
                        del parent_node['shallow_subtree_counts'][left_node_idx]

                        # only need to update counts if remaining node
                        # not last of parent's children
                        if left_node_idx < len(parent_children) - 1:
                            parent_node['deep_subtree_counts'][left_node_idx] = deep_count_to_left
                            parent_node['shallow_subtree_counts'][left_node_idx] = shallow_count_to_left

                        self.setAttrs(parent_node)

                        # can stop if parent still large enough
                        if len(parent_children) > self.btree_split_point:
                            done = True
                            break

                        # step back up the righmost nodes list
                        rightmost_nodes_idx -= 1

                        # current node now set to parent node; step
                        # back up the tree
                        node = parent_node

                    # check if we need to write back rightmost nodes to nsc u-form
                    if rightmost_nodes_modified:
                        nsc_uf['btree_rightmost_nodes'] = self.btree_rightmost_nodes

                    # finished traversing; either we found an ancestor
                    # that was large enough, or got to the root and
                    # didn't; root allowed to be less than minimum
                    # node size, but if has only one child, we can
                    # remove it
                    if not done:
                        if len(node['children']) == 1:
                            # CASE 5: remove existing root; tree
                            # shrinks in height
                            only_child = node['children'][0]
                            if only_child == self.head_segment:
                                # the collection consists of only one
                                # segment, don't need root
                                self.btree_root = None
                                self.btree_rightmost_nodes = None
                            else:
                                # update root to be the child
                                self.btree_root = only_child
                                # height of tree reduced, so remove first
                                # rightmost node in list (which should be
                                # new btree root)
                                del self.btree_rightmost_nodes[0]

                            # in any case, the value of the root needs to
                            # be updated in the collection head
                            nsc_uf['btree_root'] = self.btree_root
                            nsc_uf['btree_rightmost_nodes'] = self.btree_rightmost_nodes
                        else:
                            # number of root children less than min size,
                            # but still 2 or more
                            self.setAttrs(node)

        # fix up counts all the way up the rest of the tree, if
        # necessary
        while path:
            node = path.pop()
            node_idx = path_indices.pop()
            children = node['children']
            # only need to modify a count if child not at extreme
            # right
            if node_idx < len(children) - 1:
                node['deep_subtree_counts'][node_idx] -= deep_member_remove
                node['shallow_subtree_counts'][node_idx] -= 1
                # remove children attr from u-form object, since we
                # don't want to set in repository
                del node['children']
                self.setAttrs(node)

        # fix up head segment info
        self.shallow_total -= 1
        self.deep_total -= deep_member_remove 
        self.revision += 1
        nsc_uf['shallow_member_total_count'] = self.shallow_total
        nsc_uf['deep_member_total_count'] = self.deep_total
        nsc_uf['revision_number'] = self.revision
        self.setAttrs(nsc_uf)
	self.commit()

	return True

    def remove(self, idx, item=None):
        self.uforms_read = 0
        self.uforms_written = 0
       
       	self.removeUniversal(idx, item)

        return True

def create(r, preferred_segment_size=100, preferred_btree_max_children=101, 
           name=None, uid=None):
    if uid:
        nsc_uform = uid
    else:
        nsc_uform = uuid.UUID()
    uf = uform.UForm(nsc_uform,
                     {'head_segment' : nsc_uform,
                      'tail_segment' : nsc_uform,
                      'segment_of' : nsc_uform,
                      'preferred_segment_size' : preferred_segment_size,
                      'revision_number' : 1,
                      'deep_member_total_count' : 0,
                      'shallow_member_total_count' : 0,
                      'btree_max_children' : preferred_btree_max_children,
                      'members' : [],
                      'member_info' : [],
                      'child_properties' : []})
    if name:
        uf['name'] = name
    r.setAttr(uf)
    roles.ensure_role(r, nsc_uform, NSC_ROLE)
    roles.ensure_role(r, nsc_uform, NSC_SEGMENT_ROLE)
    return nsc_uform
