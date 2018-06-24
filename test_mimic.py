from helga_mimic import MimicPlugin, bot_say


class TestBotSayEndpoint(object):

    def setup(self):
        pass

    def test_uninitiated_brain(self):

        resp = bot_say()

        assert 'I dont know enough' in resp

    def test_thing(self):
        assert True

class TestMimicPlugin(object):

    def setup(self):

        self.plugin = MimicPlugin()

    def test_plugin(self):

        assert True
