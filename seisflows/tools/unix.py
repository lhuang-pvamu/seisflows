
import os
import errno
import random
import shutil
import socket
import subprocess
import sys
import time

from os.path import abspath, basename, isdir, isfile, join
from seisflows.tools.tools import iterable

debug_print = False

def cat(src, *dst):
    f = open(src, 'r')
    contents = f.read()
    f.close()

    if not dst:
        print( contents )
    else:
        f = open(dst, 'w')
        f.write(contents)
        f.close()


def cd(path):
    if debug_print:
        print( " cd " + path )
    os.chdir(path)


def cp(src='', dst=''):
    if isinstance(src, (list, tuple)):
        if len(src) > 1:
            assert isdir(dst)

        for sub in src:
            cp(sub, dst)
        return

    if isdir(dst):
        dst = join(dst, basename(src))
        if isdir(dst):
            for sub in ls(src):
                cp(join(src, sub), dst)
            return

    if isfile(src):
        if debug_print:
            print( "  copying file " + src )
            print( "   to " + dst )
        shutil.copy(src, dst)

    elif isdir(src):
        if debug_print:
            print( "  copying directory " + src )
            print( "   to " + dst )
        shutil.copytree(src, dst)


def hostname():
    return socket.gethostname().split('.')[0]


def ln(src, dst):
    dst = abspath(dst)
    if os.path.isdir(dst):
        for name in iterable(src):
            s = abspath(name)
            d = join(dst, basename(name))
            os.symlink(s, d)
    else:
        os.symlink(src, dst)


def ls(path):
    dirs = os.listdir(path)
    for dir in dirs:
        if dir[0] == '.':
            dirs.remove(dir)
    return dirs


def mkdir(dirs):
    for dir in iterable(dirs):
        try:
            if debug_print:
                print( "  mkdir " + dir )
            os.makedirs(dir)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(dir):
                pass
            else:
                raise

def mv(src='', dst=''):
    if isinstance(src, (list, tuple)):
        if len(src) > 1:
            assert isdir(dst)
        for sub in src:
            mv(sub, dst)
        return

    if isdir(dst):
        dst = join(dst, basename(src))
    if debug_print:
        print( "  moving " + src )
        print( "   to " + dst )
    shutil.move(src, dst)


def rename(old, new, names):
    for name in iterable(names):
        if name.find(old) >= 0:
            if debug_print:
                print( "  renaming " + old )
                print( "   to " + new )
            os.rename(name, name.replace(old, new))


def rm(path=''):
    for name in iterable(path):
        if os.path.isfile(name):
            if debug_print:
                print( "  removing file " + name )
            os.remove(name)
        elif os.path.islink(name):
            if debug_print:
                print( "  removing link " + name )
            os.remove(name)
        elif os.path.isdir(name):
            if debug_print:
                print( "  removing  tree " + name )
            shutil.rmtree(name)


def select(items, prompt=''):
    while True:
        if prompt:
            print( prompt )
        for i, item in enumerate(items):
            print("%2d) %s" % (i + 1, item))
        try:
            reply = int(raw_input().strip())
            status = (1 <= reply <= len(items))
        except (ValueError, TypeError, OverflowError):
            status = 0
        if status:
            return items[reply - 1]


def touch(filename, times=None):
    with open(filename, 'a'):
        os.utime(filename, times)



def which(name):
    def isexe(file):
        return os.path.isfile(file) and os.access(file, os.X_OK)

    dirname, filename = os.path.split(name)
    if dirname:
        if isexe(name):
            return name

    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        fullname = os.path.join(path, name)
        if isexe(fullname):
            return fullname
    else:
        return None

