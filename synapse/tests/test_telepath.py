import time
import unittest

import synapse.link as s_link
import synapse.daemon as s_daemon
import synapse.session as s_session
import synapse.telepath as s_telepath

from synapse.common import *

class Foo:

    def bar(self, x, y):
        return x + y

    def baz(self, x, y):
        raise Exception('derp')

    def speed(self):
        return

    def get(self, prop):
        return s_session.current().get(prop)

    def set(self, prop, valu):
        return s_session.current().set(prop,valu)


class TelePathTest(unittest.TestCase):

    def getFooServ(self):
        dmon = s_daemon.Daemon()

        link = dmon.listen('tcp://127.0.0.1:0/foo')
        dmon.share('foo',Foo())

        return dmon,link

    def test_telepath_basics(self):

        dmon,link = self.getFooServ()

        foo = s_telepath.openlink(link)

        s = time.time()
        for i in range(1000):
            foo.speed()

        e = time.time()

        #print('TIME: %r' % ((e - s),))

        # ensure perf is still good...

        # FIXME: disabled due to travisci boxes
        #self.assertTrue( (e - s) < 0.5 )

        self.assertEqual( foo.bar(10,20), 30 )
        self.assertRaises( JobErr, foo.faz, 10, 20 )
        self.assertRaises( JobErr, foo.baz, 10, 20 )

        foo.fini()
        dmon.fini()

    def test_telepath_chop(self):

        dmon,link = self.getFooServ()

        port = link[1].get('port')

        foo = s_telepath.openurl('tcp://localhost:%d/foo' % (port,))

        self.assertEqual( foo.bar(10,20), 30 )

        foo.fini()
        dmon.fini()

    def test_telepath_nosuchobj(self):
        dmon,link = self.getFooServ()
        port = link[1].get('port')

        newp = s_telepath.openurl('tcp://localhost:%d/newp' % (port,))
        self.assertRaises( JobErr, newp.foo )

        dmon.fini()

    def test_telepath_sess(self):
        dmon,link = self.getFooServ()
        port = link[1].get('port')

        foo = s_telepath.openurl('tcp://localhost:%d/foo' % (port,))

        self.assertIsNone( foo.get('woot') )

        foo.set('woot',10)

        self.assertEqual( foo.get('woot'), 10 )

        foo.fini()
        dmon.fini()

    def test_telepath_call(self):
        dmon,link = self.getFooServ()

        foo = s_telepath.openlink(link)

        job = foo.call('bar', 10, 20)
        self.assertIsNotNone( job )

        self.assertEqual( foo.sync(job), 30 )

        foo.fini()
        dmon.fini()
