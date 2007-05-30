import logging
from ConfigParser import NoSectionError, NoOptionError

def getMembership(config, user, _seen=None):
    """
    Generate groups ``user`` is member of, according to ``config``

    :type config: RawConfigParser
    :type user: str
    :param _seen: internal use only
    """
    log = logging.getLogger('gitosis.group.getMembership')

    if _seen is None:
        _seen = set()

    for section in config.sections():
        GROUP_PREFIX = 'group '
        if not section.startswith(GROUP_PREFIX):
            continue
        group = section[len(GROUP_PREFIX):]
        if group in _seen:
            continue

        try:
            members = config.get(section, 'members')
        except (NoSectionError, NoOptionError):
            members = []
        else:
            members = members.split()

        if user in members:
            log.debug('found %(user)r in %(group)r' % dict(
                user=user,
                group=group,
                ))
            _seen.add(group)
            yield group

            for member_of in getMembership(config, '@%s' % group,
                                           _seen=_seen):
                yield member_of
