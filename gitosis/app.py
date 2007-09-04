import os
import sys
import logging
import optparse
import ConfigParser

class App(object):
    name = None

    @classmethod
    def run(class_):
        app = class_()
        return app.main()

    def main(self):
        parser = self.create_parser()
        (options, args) = parser.parse_args()
        cfg = self.read_config(options)
        self.setup_logging(cfg)
        self.handle_args(parser, cfg, options, args)

    def create_parser(self):
        parser = optparse.OptionParser()
        parser.set_defaults(
            config=os.path.expanduser('~/.gitosis.conf'),
            )
        parser.add_option('--config',
                          metavar='FILE',
                          help='read config from FILE',
                          )

        return parser

    def read_config(self, options):
        cfg = ConfigParser.RawConfigParser()
        try:
            conffile = file(options.config)
        except (IOError, OSError), e:
            # I trust the exception has the path.
            print >>sys.stderr, '%s: Unable to read config file: %s' \
                  % (options.get_prog_name(), e)
            sys.exit(1)
        try:
            cfg.readfp(conffile)
        finally:
            conffile.close()
        return cfg

    def setup_logging(self, cfg):
        logging.basicConfig()

        try:
            loglevel = cfg.get('gitosis', 'loglevel')
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError):
            pass
        else:
            try:
                symbolic = logging._levelNames[loglevel]
            except KeyError:
                # need to delay error reporting until we've called
                # basicConfig
                log = logging.getLogger('gitosis.app')
                log.warning(
                    'Ignored invalid loglevel configuration: %r',
                    loglevel,
                    )
            else:
                logging.root.setLevel(symbolic)

    def handle_args(self, parser, options, args):
        if args:
            parser.error('not expecting arguments')
