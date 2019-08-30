from mcvapi.mcvbase import MCVBase

class BiggestsBlobs(MCVBase):

    IMPORT = "from mcvapi.blobs.biggests_blobs import BiggestsBlobs"
    


    def load(self, data, **kwargs):
        super(BiggestsBlobs, self).load(data, **kwargs)
        self._param_biggestsblobs_n = data.get('biggestsblobs_n', 1)

    def save(self, data, **kwargs):
        data = super(BiggestsBlobs, self).save(data, **kwargs)
        data['biggestsblobs_n'] = self._param_biggestsblobs_n
        return data

    def process(self, blobs, **kwargs):
        blobs = sorted(blobs,key=lambda a:a._area,reverse=True)
        if len(blobs)>self._param_biggestsblobs_n: return blobs[:self._param_biggestsblobs_n]
        else: return blobs

    def processflow(self, blobs, **kwargs):
        blobs = super(BiggestsBlobs, self).processflow(blobs, **kwargs)
        return BiggestsBlobs.process(self, blobs, **kwargs)