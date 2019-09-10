from util.util import IdGenerator


class Item:

    '''
    Class: Item

    Description: Item for use with TodoList

    Args:
        - id: Identifier
        - desc: Description of item
        - children: Child items of item
        - done: Task marked as done?
        - deleted: Task marked as deleted?
    '''

    def __init__(self, id, desc, done=False, deleted=False, parent=None, progress=False, priority=False):
        self.id = id
        self.original_id = id
        self.children = []
        self.height = 1
        self.desc = desc
        self.done = done
        self.progress = progress
        self.priority = priority
        self.deleted = deleted
        self.idgen = IdGenerator()
        self.parent = parent

    def pop_child(self, child):
        ''' Remove a child Item '''
        self.height -= 1
        return self.children.pop(child)

    def append_child(self, child):
        ''' Add a child Item '''
        self.children.append(child)
        self.height += 1

    def set_desc(self, desc):
        ''' Set description of Item '''
        self.desc = desc

    def mark_progress_recursive(self, tl):
        ''' Recursively mark children as !.progress '''
        self.progress = tl
        for child in self.children:
            child.mark_progress_recursive(tl)

    def mark_progress_recursive_top_level(self):
        ''' Starter for .mark_progress_recursive '''
        self.mark_progress_recursive(not self.progress)

    def mark_progress(self):
        ''' Flip value of .progress '''
        self.progress = not self.progress

    def mark_priority(self):
        ''' Flip value of .priority '''
        self.priority = not self.priority

    def mark_done_recursive(self, tl):
        ''' Recursively mark children as !.done '''
        self.done = tl
        for child in self.children:
            child.mark_done_recursive(tl)

    def mark_done_recursive_top_level(self):
        ''' Starter for .mark_done_recursive '''
        self.mark_done_recursive(not self.done)

    def mark_done(self):
        ''' Flip value of .done '''
        self.done = not self.done

    def mark_deleted(self):
        ''' Flip value of .deleted '''
        if self.done and not self.deleted:
            self.mark_done()
        self.deleted = not self.deleted

    def serialize(self):
        ''' Serialize Item and children to dict '''
        children = []
        for child in self.children:
            children.append(child.serialize())
        return {
            'id': self.id,
            'desc': self.desc,
            'done': self.done,
            'deleted': self.deleted,
            'progress': self.progress,
            'priority': self.priority,
            'children': children
        }

    def __str__(self):
        ''' String translation dunder '''
        marker = ' '
        if self.progress:
            marker = 'P'
        if self.done:
            marker = 'x'
        priority = ''
        if self.priority:
            priority = '!'
        i = str(self.id) + '. '
        if self.deleted:
            marker = 'del'
            i = ''
            priority = ''
        return f'[{marker}] {i}{self.desc}{priority}'
