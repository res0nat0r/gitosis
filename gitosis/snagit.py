from gitosis import access

def list_repos(cfg, user, cmd):
    all_repos = []
    secs = cfg.sections()
    for sec in secs:
        for opt in cfg.options(sec):
            if ((str(opt) == "writable") or (str(opt) == "writeable")):
                ws = cfg.get(sec, opt).split()
                for repo in ws:
                    try:
                        all_repos.index(repo)
                    except ValueError, e:
                        all_repos.append(repo)
            elif (str(opt) == "readonly"):
                readonlyies = cfg.get(sec, opt)
                for repo in readonlyies:
                    try:
                        all_repos.index(repo)
                    except ValueError, e:
                        all_repos.append(repo)
    
    readonly_repos = []
    writable_repos = []
    # At this point should have a list of unique repos.    
    for repo in all_repos:
        rs = access.haveAccess(cfg, user, "writable", repo)
        if (rs): # has read and write access
            writable_repos.append(repo)
        else:
            rs = access.haveAccess(cfg, user, "readonly", repo)
            if (rs): # has read only access
                readonly_repos.append(repo)
            else: # has no access
                pass
    
    for repo in writable_repos:
        print "%s, writable" % str(repo)
    for repo in readonly_repos:
        print "%s, readonly" % str(repo)
