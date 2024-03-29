#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2013 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2018 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
# Copyright © 2013-2016 Luca Wehrstedt <luca.wehrstedt@gmail.com>
# Copyright © 2016 William Di Luigi <williamdiluigi@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa

import argparse
import chardet
import errno
import itertools
import logging
import netifaces
import os
import sys
import grp

import gevent
import gevent.socket

from cms import ServiceCoord, ConfigError, async_config, config


logger = logging.getLogger(__name__)


def mkdir(path):
    """Make a directory without complaining for errors.

    path (string): the path of the directory to create
    returns (bool): True if the dir is ok, False if it is not

    """
    try:
        os.mkdir(path)
        try:
            os.chmod(path, 0o770)
            cmsuser_gid = grp.getgrnam(config.cmsuser).gr_gid
            os.chown(path, -1, cmsuser_gid)
        except OSError as error:
            os.rmdir(path)
            return False
    except OSError as error:
        if error.errno != errno.EEXIST:
            return False
    return True


# This function is vulnerable to a symlink attack, see:
# https://bugs.python.org/issue4489
# It appears the only bulletproof fix requires the ability to traverse
# directories using file descriptors (like fwalk) which is only in py3.
def rmtree(path):
    """Recursively delete a directory tree.

    Remove the directory at the given path, but first remove the files
    it contains and recursively remove the subdirectories it contains.
    Be cooperative with other greenlets by yielding often.

    path (str): the path to a directory.

    raise (OSError): in case of errors in the elementary operations.

    """
    if os.path.islink(path):
        raise OSError("unsafe to call rmtree on a symlink")

    for dirpath, subdirnames, filenames in os.walk(path, topdown=False):
        for filename in filenames:
            os.remove(os.path.join(dirpath, filename))
            gevent.sleep(0)
        for subdirname in subdirnames:
            subdirpath = os.path.join(dirpath, subdirname)
            if os.path.islink(subdirpath):
                os.remove(subdirpath)
                gevent.sleep(0)
        os.rmdir(dirpath)
        gevent.sleep(0)


def utf8_decoder(value):
    """Decode given binary to text (if it isn't already) using UTF8, and
    falling back to other encodings when possible (using chardet to guess).

    value (string): value to decode.

    return (unicode): decoded value.

    raise (TypeError): if value isn't a string.

    """
    if isinstance(value, str):
        return value
    elif isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return value.decode(chardet.detect(value).get("encoding"))
            except TypeError:
                pass

    raise TypeError("Not a string.")


def get_safe_shard(service, provided_shard):
    """Return a safe shard number for the provided service, or raise.

    service (string): the name of the service trying to get its shard,
        for looking it up in the config.
    provided_shard (int|None): the shard number provided by the admin
        via command line, or None (the default value).

    return (int): the provided shard number if it makes sense,
        otherwise the shard number found matching the IP address with
        the configuration.

    raise (ValueError): if no safe shard can be returned.

    """
    if provided_shard is None:
        addrs = _find_local_addresses()
        computed_shard = _get_shard_from_addresses(service, addrs)
        if computed_shard is None:
            logger.critical("Couldn't autodetect shard number and "
                            "no shard specified for service %s, "
                            "quitting.", service)
            raise ValueError("No safe shard found for %s." % service)
        else:
            return computed_shard
    else:
        coord = ServiceCoord(service, provided_shard)
        if coord not in async_config.core_services:
            logger.critical("The provided shard number for service %s "
                            "cannot be found in the configuration, "
                            "quitting.", service)
            raise ValueError("No safe shard found for %s." % service)
        else:
            return provided_shard


def get_service_address(key):
    """Give the Address of a ServiceCoord.

    key (ServiceCoord): the service needed.
    returns (Address): listening address of key.

    """
    if key in async_config.core_services:
        return async_config.core_services[key]
    elif key in async_config.other_services:
        return async_config.other_services[key]
    else:
        raise KeyError("Service not found.")


def get_service_shards(service):
    """Returns the number of shards that a service has.

    service (string): the name of the service.
    returns (int): the number of shards defined in the configuration.

    """
    for i in itertools.count():
        try:
            get_service_address(ServiceCoord(service, i))
        except KeyError:
            return i


def default_argument_parser(description, cls, ask_contest=None):
    """Default argument parser for services.

    This has two versions, depending on whether the service needs a
    contest_id, or not.

    description (string): description of the service.
    cls (type): service's class.
    ask_contest (function|None): None if the service does not require
        a contest, otherwise a function that returns a contest_id
        (after asking the admins?)

    return (object): an instance of a service.

    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("shard", action="store", type=int, nargs="?")

    # We need to allow using the switch "-c" also for services that do
    # not need the contest_id because RS needs to be able to restart
    # everything without knowing which is which.
    contest_id_help = "id of the contest to automatically load, " \
                      "or ALL to serve all contests"
    if ask_contest is None:
        contest_id_help += " (ignored)"
    parser.add_argument("-c", "--contest-id", action="store",
                        type=utf8_decoder, help=contest_id_help)
    args = parser.parse_args()

    try:
        args.shard = get_safe_shard(cls.__name__, args.shard)
    except ValueError:
        raise ConfigError("Couldn't autodetect shard number and "
                          "no shard specified for service %s, "
                          "quitting." % (cls.__name__,))

    if ask_contest is None:
        return cls(args.shard)
    contest_id = contest_id_from_args(args.contest_id, ask_contest)
    if contest_id is None:
        return cls(args.shard)
    else:
        return cls(args.shard, contest_id)


def contest_id_from_args(args_contest_id, ask_contest):
    """Return a valid contest_id from the arguments or None if multicontest
    mode should be used

    If the passed value is missing, ask the admins with ask_contest.
    If the contest id is invalid, print a message and exit.

    args_contest_id (int|str|None): the contest_id passed as argument.
    ask_contest (function): a function that returns a contest_id.

    """
    assert ask_contest is not None

    if args_contest_id == "ALL":
        return None
    if args_contest_id is not None:
        try:
            contest_id = int(args_contest_id)
        except ValueError:
            logger.critical("Unable to parse contest id '%s'", args_contest_id)
            sys.exit(1)
    else:
        contest_id = ask_contest()

    # Test if there is a contest with the given contest id.
    from cms.db import is_contest_id
    if not is_contest_id(contest_id):
        logger.critical("There is no contest with the specified id. "
                        "Please try again.")
        sys.exit(1)
    return contest_id


def _find_local_addresses():
    """Returns the list of IPv4 and IPv6 addresses configured on the
    local machine.

    returns ([(int, str)]): a list of tuples, each representing a
                            local address; the first element is the
                            protocol and the second one is the
                            address.

    """
    addrs = []
    # Based on http://stackoverflow.com/questions/166506/
    # /finding-local-ip-addresses-using-pythons-stdlib
    for iface_name in netifaces.interfaces():
        for proto in [netifaces.AF_INET, netifaces.AF_INET6]:
            addrs += [(proto, i['addr'])
                      for i in netifaces.ifaddresses(iface_name).
                      setdefault(proto, [])]
    return addrs


def _get_shard_from_addresses(service, addrs):
    """Returns the first shard of a service that listens at one of the
    specified addresses.

    service (string): the name of the service.
    addrs ([(int, str)]): a list like the one returned by
        find_local_addresses().

    returns (int|None): the found shard, or None in case it doesn't
        exist.

    """
    ipv4_addrs = set()
    ipv6_addrs = set()
    for proto, addr in addrs:
        if proto == gevent.socket.AF_INET:
            ipv4_addrs.add(addr)
        elif proto == gevent.socket.AF_INET6:
            ipv6_addrs.add(addr)

    for shard in itertools.count():
        try:
            host, port = get_service_address(ServiceCoord(service, shard))
        except KeyError:
            # No more shards to test.
            return None

        try:
            res_ipv4_addrs = set([x[4][0] for x in
                                  gevent.socket.getaddrinfo(
                                      host, port,
                                      gevent.socket.AF_INET,
                                      gevent.socket.SOCK_STREAM)])
        except (gevent.socket.gaierror, gevent.socket.error):
            pass
        else:
            if not ipv4_addrs.isdisjoint(res_ipv4_addrs):
                return shard

        try:
            res_ipv6_addrs = set([x[4][0] for x in
                                  gevent.socket.getaddrinfo(
                                      host, port,
                                      gevent.socket.AF_INET6,
                                      gevent.socket.SOCK_STREAM)])
        except (gevent.socket.gaierror, gevent.socket.error):
            pass
        else:
            if not ipv6_addrs.isdisjoint(res_ipv6_addrs):
                return shard

def string_formatting(value):
    """
    Returns a formatted string, which does not contain the specified characters.
    :param value: the string to format
    :return: the formatted string
    """
    if isinstance(value, str):
        characters = [" ", "!", "?", "/", ":", "^", "$"]
        for char in characters:
            value = value.replace(char, "")

    return value
