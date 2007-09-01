from nose.tools import eq_ as eq

import errno
import os
import stat

def mkdir(*a, **kw):
    try:
        os.mkdir(*a, **kw)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

def maketemp():
    tmp = os.path.join(os.path.dirname(__file__), 'tmp')
    mkdir(tmp)
    me = os.path.splitext(os.path.basename(__file__))[0]
    tmp = os.path.join(tmp, me)
    mkdir(tmp)
    return tmp

def writeFile(path, content):
    tmp = '%s.tmp' % path
    f = file(tmp, 'w')
    try:
        f.write(content)
    finally:
        f.close()
    os.rename(tmp, path)

def readFile(path):
    f = file(path)
    try:
        data = f.read()
    finally:
        f.close()
    return data

def check_mode(path, mode, is_file=None, is_dir=None):
    st = os.stat(path)
    if is_dir:
        assert stat.S_ISDIR(st.st_mode)
    if is_file:
        assert stat.S_ISREG(st.st_mode)

    got = stat.S_IMODE(st.st_mode)
    eq(got, mode, 'File mode %04o!=%04o for %s' % (got, mode, path))
