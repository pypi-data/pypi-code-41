from MAYA.VIA import uuid, uform, repos
from MAYA.utils.shepherding import waitForPresence
TIMEOUTSECS=0

class NSCSimpleQuery:

  def getAttrs(self, uu, attrs):
    waitForPresence(self.r, uu, TIMEOUTSECS)
    m = uform.UForm(uu, attrs)
    return self.r.getAttr(m)
  
  def getAttr(self, uu, attr):
    waitForPresence(self.r, uu, TIMEOUTSECS)
    return self.r.getAttr(uu, attr)

  def __init__(self, r, nsc_uform):
    self.r = r
    self.nsc_uform = nsc_uform

    # cache info from nsc u-form
    self.nsc_uform_contents = self.getAttrs(self.nsc_uform,
                                            ['head_segment',
                                             'btree_root',
                                             'deep_member_total_count'])
    self.head_segment = self.nsc_uform_contents['head_segment']
    self.btree_root = self.nsc_uform_contents['btree_root']
    self.deep_member_total_count = self.nsc_uform_contents['deep_member_total_count']

    # cache info from head segment
    self.nsc_head_segment_contents = self.getAttrs(self.head_segment,
                                                   ['members',
                                                    'member_info'])
    self.head_members = self.nsc_head_segment_contents['members']
    self.member_info = self.nsc_head_segment_contents['member_info']

    self.visited = 0

  # findNode wrapper
  def find(self, idx):
    self.visited = 0
   
    # is index out of bounds?
    if idx >= self.deep_member_total_count:
      return None, None, None 

    # keep track of total deep members seen so far
    total = 0

    # collection has only one segment if no btree root
    if not self.btree_root:
      element, cur_node, index, mem_info, shallow, _ = self.findNode(idx, self.head_segment)
    else:
      element, cur_node, index, mem_info, shallow, mem = self.findNode(idx, self.btree_root)
    recurse = True 
    while recurse:
	if mem_info:
          uf = self.r.getAttr(uform.UForm(element, ['head_segment',
                                                    'btree_root']))
          if uf['btree_root'] != None:
            element, cur_node, index, mem_info, shallow, mem = self.findNode(index, uf['btree_root'])
          elif uf['head_segment'] != None:
            element, cur_node, index, mem_info, shallow, mem = self.findNode(index, uf['head_segment'])
          else:
            recurse = False
	else:
          recurse = False

    return element, cur_node, index

  # given index and any node starting point start searching for the index
  def findNode(self, idx, cur_node):
    total = 0
    shallow_counts = 0
    while cur_node:

      # get contents of node; either inner node or leaf
      cur_node_contents = self.r.getAttr(uform.UForm(cur_node,
	  ['children',
	  'deep_subtree_counts',
	  'shallow_subtree_counts',
	  'member_info',
	  'members']))
      children = cur_node_contents['children']
      counts = cur_node_contents['deep_subtree_counts']
      shallow_subtree = cur_node_contents['shallow_subtree_counts']
      members = cur_node_contents['members']
      member_info = cur_node_contents['member_info']
	
      # no values for 'deep_subtree_counts' indicate this is a leaf
      # node; Now check for if we recursively search another embedded nsc
      # or just a plain leaf node
      if not counts:
	  mem_index = 0
	  for mem_info in member_info:
	      if mem_info != None:
		  if idx < total + mem_info[0]:
		      return members[mem_index], cur_node, idx-total, mem_info, shallow_counts, mem_index
		  else:
		      total += mem_info[0]
              elif idx == total:
		  return members[mem_index], cur_node, mem_index, mem_info, shallow_counts, mem_index
              else:
                  total += 1
              mem_index += 1
	      shallow_counts += 1
      
      # have inner node; iterate over all counts
      i = 0
      while i < len(counts):
	cur_count = counts[i]
	# if count now too large, go to child on left...
	if idx < total + cur_count:
	    break
	# update total seen
      	shallow_counts += shallow_subtree[i]
	total += cur_count
	i += 1
	
      # traverse to next node; either some count's left child, or the
      # rightmost child
      cur_node = children[i]

  def get_counts(self, info):
    info = info or []
    deep_count = reduce(lambda x, y: x + y, map(lambda x: (x or [1])[0], info))
    shallow_count = len(info)
    return deep_count, shallow_count

  def traverse(self, idx):
    cur_segment = self.head_segment
    total = 0
    self.visited = 0
    while cur_segment:
      self.visited += 1
      uf = uform.UForm(cur_segment, ['members', 'member_info', 'next_segment'])
      uf = self.r.getAttr(uf)
      members = uf['members']
      member_info = uf['member_info']
      next_segment = uf['next_segment']
      
      total += self.get_counts(member_info)[0]
      if idx < total:
        return members[idx - total]
      
      cur_segment = next_segment

    return None
