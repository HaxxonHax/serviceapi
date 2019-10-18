""" ServiceApi and ServiceConfig classes. """
from time import sleep
import os
import dbus
from dbus.exceptions import DBusException

E_FILENOTFOUND = 1
E_INVALIDPERMS = 2
E_PRIVILEGES = 3
E_START = 4
E_STOP = 5
E_INVALIDACTION = 6
E_NOUNIT = 7
E_INACTIVE = 8
E_ACTIVE = 9
E_NOTRUNNING = 10
E_RUNNING = 11

SYSTEMD_BUSNAME = 'org.freedesktop.systemd1'
SYSTEMD_PATH = '/org/freedesktop/systemd1'
SYSTEMD_MANAGER_INTERFACE = 'org.freedesktop.systemd1.Manager'
SYSTEMD_UNIT_INTERFACE = 'org.freedesktop.systemd1.Unit'
SYSTEMD_ACTION_ID = 'org.freedesktop.systemd1.manage-units'


def get_sysd_manager_interface(bus):
    """ Gets the dbus interface for a system manager. """
    proxy = bus.get_object('org.freedesktop.PolicyKit1',
                           '/org/freedesktop/PolicyKit1/Authority')
    authority = dbus.Interface(
        proxy,
        dbus_interface='org.freedesktop.PolicyKit1.Authority'
    )
    system_bus_name = bus.get_unique_name()

    result = authority.CheckAuthorization(
        ('system-bus-name', {'name': system_bus_name}),
        SYSTEMD_ACTION_ID, {}, 1, ''
    )

    if result[1] != 0:
        return None

    systemd_object = bus.get_object(SYSTEMD_BUSNAME, SYSTEMD_PATH)
    systemd_manager = dbus.Interface(systemd_object,
                                     SYSTEMD_MANAGER_INTERFACE)
    return systemd_manager


class ServiceApi:
    """ Class for the configuration files. """
    def __init__(self, servicename):
        self.servicename = servicename
        self.svcname_long = servicename + '.service'
        self.servicepathsrc = '/lib/systemd/system/' + self.svcname_long
        self.servicepathdst = ('/etc/systemd/system/multi-user.target.wants/' +
                               self.svcname_long)
        self.last_result = {}

    def dbus_action(self, action):
        """ Gets a dbusobject. """
        bus = dbus.SystemBus()
        systemd_manager = get_sysd_manager_interface(bus)

        try:
            unit = systemd_manager.GetUnit(self.svcname_long)
        except DBusException:
            return {'status': E_NOUNIT, 'active_state': '', 'sub_state': ''}
        unit_object = bus.get_object(SYSTEMD_BUSNAME, unit)
        if action == 'start':
            systemd_manager.StartUnit(self.svcname_long, 'replace')
        elif action == 'stop':
            unit_interface = dbus.Interface(unit_object,
                                            SYSTEMD_UNIT_INTERFACE)
            unit_interface.Stop('replace')
        elif action == 'restart':
            unit_interface = dbus.Interface(unit_object,
                                            SYSTEMD_UNIT_INTERFACE)
            unit_interface.Restart('replace')

        jobs = systemd_manager.ListJobs()
        while any(self.svcname_long in str(job) for job in jobs):
            sleep(1)
            jobs = systemd_manager.ListJobs()

        prop_unit = dbus.Interface(unit_object,
                                   'org.freedesktop.DBus.Properties')

        active_state = prop_unit.Get(
            'org.freedesktop.systemd1.Unit',
            'ActiveState'
        )
        sub_state = prop_unit.Get('org.freedesktop.systemd1.Unit', 'SubState')

        return {'active_state': active_state, 'sub_state': sub_state}

    def dbus_getstate(self):
        """ Gets a dbusobject. """
        bus = dbus.SystemBus()
        systemd_manager = get_sysd_manager_interface(bus)

        unit = systemd_manager.GetUnit(self.svcname_long)
        unit_object = bus.get_object(SYSTEMD_BUSNAME, unit)

        prop_unit = dbus.Interface(unit_object,
                                   'org.freedesktop.DBus.Properties')

        active_state = prop_unit.Get(
            'org.freedesktop.systemd1.Unit',
            'ActiveState'
        )
        sub_state = prop_unit.Get('org.freedesktop.systemd1.Unit', 'SubState')

        return {'active_state': active_state, 'sub_state': sub_state}

    def enable(self):
        """ Enables the service. """
        result = {'message': [], 'status': 0}
        if not os.path.isfile(self.servicepathsrc):
            result['message'].append(self.servicename +
                                     ' has no service file.')
            result['status'] = E_FILENOTFOUND
        if not os.path.islink(self.servicepathdst):
            try:
                os.symlink(self.servicepathsrc, self.servicepathdst)
                result['message'].append('Enabled ' + self.servicename)
            except FileNotFoundError:
                result['status'] = E_FILENOTFOUND
                result['message'].append('Error enabling ' + self.servicename)
        else:
            result['message'].append('Service ' + self.servicename +
                                     ' already enabled.')
        return result

    def disable(self):
        """ Disables the service. """
        result = {'message': [], 'status': 0}
        if os.path.exists(self.servicepathdst):
            try:
                if os.path.islink(self.servicepathdst):
                    os.unlink(self.servicepathdst)
                result['message'].append('Disabled ' + self.servicename)
            except FileNotFoundError:
                result['status'] = E_FILENOTFOUND
                result['message'].append('Error disabling ' + self.servicename)
        else:
            result['message'].append('Service ' + self.servicename +
                                     ' already disabled.')
        return result

    def start(self):
        """ Starts the service. """
        result = {'message': [], 'status': 0}
        status = self.dbus_action('start')
        if (status['active_state'] == 'active' and
                status['sub_state'] == 'running'):
            result['message'].append('Started ' + self.servicename)
        else:
            result['message'].append('Error starting ' + self.servicename)
            result['status'] = E_START
        return result

    def stop(self):
        """ Stops the service. """
        result = {'message': [], 'status': 0}
        status = self.dbus_action('stop')
        if (status['active_state'] == 'inactive' and
                status['sub_state'] == 'dead'):
            result['message'].append('Stopped ' + self.servicename)
        else:
            result['message'].append('Error stopping ' + self.servicename)
            result['status'] = E_STOP
        return result

    def restart(self):
        """ Restarts the service. """
        result = {'message': [], 'status': 0}
        status = self.dbus_action('restart')
        if (status['active_state'] == 'active' and
                status['sub_state'] == 'running'):
            result['message'].append('Restarted ' + self.servicename)
        else:
            result['message'].append('Error restarting ' + self.servicename)
            result['status'] = E_START
        return result

    def status(self):
        """ Gets the status of the service. """
        result = {'message': [], 'status': 0}
        status = self.dbus_getstate()
        result['message'].append(status['sub_state'] +
                                 '(' + status['sub_state'] + ')')
        result['message'].append('active_state: ' + status['active_state'])
        result['message'].append('sub_state: ' + status['sub_state'])
        return result

    def servicectl(self, action):
        """ Controls service by action parameter. """
        result = {'message': [], 'status': 0}
        if action == 'enable':
            result = self.enable()
        elif action == 'disable':
            result = self.disable()
        elif action == 'start':
            result = self.start()
        elif action == 'stop':
            result = self.stop()
        elif action == 'status':
            result = self.status()
        elif action == 'restart':
            print('restarting')
            result = self.restart()
        else:
            result['message'].append('Invalid action.')
            result['status'] = E_INVALIDACTION

        return result

    def enable_and_start(self):
        """ Enables and starts the service. """
        result = {'message': [], 'status': 0}
        stat = self.enable()
        result['status'] = stat['status']
        result['message'].extend(stat['message'])
        if result['status'] == 0:
            stat = self.start()
            result['status'] = stat['status']
            result['message'].extend(stat['message'])
        return result

    def disable_and_stop(self):
        """ Disables and stops the service. """
        result = {'message': [], 'status': 0}
        stat = self.disable()
        result['status'] = stat['status']
        result['message'].extend(stat['message'])
        if result['status'] == 0:
            stat = self.stop()
            result['status'] = stat['status']
            result['message'].extend(stat['message'])
        return result
