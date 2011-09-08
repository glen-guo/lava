# Copyright (C) 2011 Calxeda, Inc.
#
# This file is part of LAVA Dispatcher.
#
# LAVA Dispatcher is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LAVA Dispatcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses>.

import pexpect
import sys
from lava_dispatcher.client import LavaClient, SerialIO, OperationFailed
import pxssh


class LavaSSHClient(LavaClient):

    def __init__(self, context, config):
        self.context = context
        self.config = config
        self.sio = SerialIO(sys.stdout)
        try:
            self.proc = pxssh.pxssh(logfile=self.sio)
            self.proc.login(self.hostname, self.username, self.password)
            self.proc.prompt()
        except pxssh.ExceptionPxssh:
            raise OperationFailed()

    @property
    def hostname(self):
        return self.config.get("hostname")

    @property
    def username(self):
        return self.config.get("username")

    @property
    def password(self):
        return self.config.get("password")

    @property
    def master_str(self):
        return self.proc.PROMPT

    @property
    def tester_str(self):
        return self.proc.PROMPT

    def soft_reboot(self):
        self.run_shell_command('reboot', sudo=True)

    def hard_reboot(self):
        """ No way to hard reboot through ssh """
        msg = "hard_reboot is not supported by LavaSSHClient"
        raise OperationFailed(msg)

    def simple_command(self, cmd, timeout=5):
        self.run_shell_command(cmd, timeout=timeout)

    def run_shell_command(self, cmd, response=None, timeout=-1, sudo=False):
        expectations = [pexpect.TIMEOUT if not response else response]
        if sudo:
            cmd = 'sudo ' + cmd
            pw_req = "password for %s:" % self.get_username()
            expectations.append(pw_req)

        self.proc.sendline(cmd)
        i = self.proc.expect(expectations, timeout=timeout)
        if i != 0: # pexpect matched pw_req
            self.proc.sendline(self.get_password())
            self.proc.expect(expectations[:-1], timeout=timeout)
