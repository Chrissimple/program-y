"""
Copyright (c) 2016-17 Keith Sterling http://www.keithsterling.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
import sleekxmpp

from programy.clients.client import BotClient
from programy.config.sections.client.xmpp import XmppConfiguration

class XmppClient(sleekxmpp.ClientXMPP):

    def __init__(self, bot_client, jid, password):
        self.bot_client = bot_client
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handlers()

    def add_event_handlers(self):
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    def start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):

            question = msg['body']
            userid = msg['from']

            response =  self.bot_client.bot.ask_question(userid, question)
            if response is not None:
                msg.reply(response).send()

    def register_plugins(self, configuration):
        if configuration.client_configuration.xep_0030 is True:
            self.register_plugin('xep_0030')

        if configuration.client_configuration.xep_0004 is True:
            self.register_plugin('xep_0004')

        if configuration.client_configuration.xep_0060 is True:
            self.register_plugin('xep_0060')

        if configuration.client_configuration.xep_0199 is True:
            self.register_plugin('xep_0199')

    def run(self, server, port, block=True):
        if self.connect((server, port)):
            print("Connected, running...")
            self.process(block=block)
        else:
            print("Failed to connect, exiting...")

class XmppBotClient(BotClient):

    def __init__(self, argument_parser=None):
        self.clientid = "xmpp"
        BotClient.__init__(self, argument_parser)

    def set_environment(self, env='xmpp'):
        self.bot.brain.properties.add_property("env", env)
        
    def get_client_configuration(self):
        return XmppConfiguration()

    def get_username_password(self, license_keys):
        username = license_keys.get_key("XMPP_USERNAME")
        password = license_keys.get_key("XMPP_PASSWORD")
        return username, password

    def get_server_port(self, configuration):
        server = configuration.client_configuration.server
        port = configuration.client_configuration.port
        return server, port

    def create_client(self, username, password):
        return XmppClient(self, username, password)

    def run(self):
        if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("XMPP Client is running....")

        username, password = self.get_username_password(self.bot.license_keys)
        server, port = self.get_server_port(self.configuration)

        self._client = self.create_client(username, password)
        self._client.register_plugins(self.configuration)
        self._client.run(server, port, block=True)

if __name__ == '__main__':

    def run():
        print("Loading Xmpp client, please wait. See log output for progress...")
        xmpp_app = XmppBotClient()
        xmpp_app.run()

    run()