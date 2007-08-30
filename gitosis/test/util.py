import os, errno

def mkdir(path):
    try:
        os.mkdir(path)
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
