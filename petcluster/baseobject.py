import weakref

class BaseObject(object):

    def __init__(self, uid, cluster):

        self.uid = uid
        self.source = ''
        self.model_version = ''
        self.editor = ''
        self.change_date = ''
        self.cluster = cluster 
