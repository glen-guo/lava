#!/usr/bin/python
from lava.actions import BaseAction
from lava.client import OperationFailed

class cmd_test_abrek(BaseAction):
    def run(self, test_name, timeout=-1):
        print "abrek run %s" % test_name

        #Make sure in test image now, abrek will install in master image
        self.in_test_shell()

        self.test_abrek(self, test_name, timeout)

    def test_abrek(self, test_name, timeout):
        """
        Invoke test suite by abrek
        """
        self.client.run_shell_command('abrek run %s' % test_name,
            response = tester_str, timeout = timeout)

    """
    Define tester_str temply, should be a constant imported from other module
    """
    tester_str = "root@localhost:"

class cmd_deploy_abrek(BaseAction):
    """
    abrek test tool deployment to test image rootfs by chroot
    Would like to implement a new command, may be placed in deploy.py, 
    it can move later
    """
    def run(self):
        #Make sure in master image
        #, or exception can be caught and do boot_master_image()
        master_str = "root@master:"
        self.client.in_master_shell()
        #install bazaar in tester image
        self.client.run_shell_command(
            'mkdir -p /mnt/root',
            response = master_str)
        self.client.run_shell_command(
            'mount /dev/disk/by-label/testrootfs /mnt/root',
            response = master_str)
        #does it need to change to a temp path to install abrek
        #does it need to restore old resolv.conf
        self.client.run_shell_command(
            'cp -L /etc/resolv.conf /mnt/root/etc',
            response = master_str)
        self.client.run_shell_command(
            'cp -L /etc/apt/apt.conf.d/70debconf /mnt/root/etc/apt/apt.conf.d',
            response = master_str)
        self.client.run_shell_command(
            'chroot /mnt/root mount -t proc proc /proc',
            response = master_str)
        #elimite warning: Can not write log, openpty() failed 
        #                   (/dev/pts not mounted?), does not work
        self.client.run_shell_command(
            'chroot /mnt/root mount --rbind /dev /mnt/root/dev',
            response = master_str)
        self.client.run_shell_command(
            'chroot /mnt/root apt-get update',
            response = master_str)
        self.client.run_shell_command(
            'chroot /mnt/root apt-get -y install bzr',
            response = master_str)
        #Two necessary packages for build abrek
        self.client.run_shell_command(
            'chroot /mnt/root apt-get -y install python-distutils-extra',
            response = master_str)
        self.client.run_shell_command(
            'chroot /mnt/root apt-get -y install python-apt',
            response = master_str)
        self.client.run_shell_command(
            'chroot /mnt/root bzr branch lp:abrek',
            response = master_str)
        self.client.run_shell_command(
            'chroot /mnt/root sh -c "cd abrek && python setup.py install"',
            response = master_str)
        #Test if abrek installed
        self.client.run_shell_command(
            'chroot /mnt/root abrek help"',
            response = "list-tests")
        self.client.run_shell_command(
            'chroot /mnt/root umount /proc',
            response = master_str)
