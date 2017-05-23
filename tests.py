import unittest

from incapsula import IncapSession

class TestIncapBlocked(unittest.TestCase):
    body = """
    <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=2977d8d74f63d7f8fedbea018b7a1d05"></script></head><body style="margin:0px;height:100%"><iframe src="/_Incapsula_Resource?CWUDNSAI=18&xinfo=10-145639306-0 0NNN RT(1495555623413 147) q(0 -1 -1 -1) r(0 -1) B15(11,4636,0) U5&incident_id=220011010269131805-850355021556761818&edet=15&cinfo=0b000000" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessful. Incapsula incident ID: 220011010269131805-850355021556761818</iframe></body></html>
    """

    def test_incap_blocked(self):
        s = IncapSession()
        self.assertTrue(s.incap_blocked(self.body))

