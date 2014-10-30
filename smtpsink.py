#!/usr/bin/env python
import asyncore
import os

from datetime import datetime
from email.parser import Parser
from smtpd import SMTPServer


try:
    from termcolor import colored
except ImportError:
    def colored(message, color):
        return message


class SMTPSink(SMTPServer, object):
    count = 0
    date = None
    files_created = []

    def __init__(self, bindto, port):
        super(SMTPSink, self).__init__(bindto, port)
        self.date = datetime.now().strftime('%Y%m%d%H%M%S')
        self.ensure_directory('smtpsink')

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.count += 1
        message = Parser().parsestr(data)
        print "%d -- Message '%s' from %s to %s" % \
              (self.count, colored(message['subject'], 'green'), mailfrom, colored(rcpttos, 'yellow'))
        self.save_message(data)

    def save_message(self, data):
        filename = 'smtpsink/%s-%d.eml' % (self.date, self.count)
        with open(filename, 'w') as f:
            f.write(data)
            self.files_created.append(filename)

    def cleanup_messages(self):
        print "Cleaning up %d files" % len(self.files_created)
        for f in self.files_created:
            os.remove(f)

    @staticmethod
    def ensure_directory(path):
        if os.path.isfile(path):
            raise RuntimeError("%s is a file not a directory" % path)
        if not os.path.isdir(path):
            os.mkdir(path)


if __name__ == '__main__':
    bindto = 'localhost'
    port = 1025
    smtp_server = SMTPSink((bindto, port), None)
    try:
        print "Starting at %s:%d" % (bindto, port)
        asyncore.loop()
    except KeyboardInterrupt:
        print "Quitting after having processed %d emails" % smtp_server.count
        smtp_server.cleanup_messages()
