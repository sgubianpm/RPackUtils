##############################################################################
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
##############################################################################
# -*- coding: utf-8 > -*-
__author__ = "Sylvain Gubian"
__copyright__ = "Copyright 2016, PMP SA"
__license__ = "GPL2.0"
__email__ = "Sylvain.Gubian@pmi.com"

import os
from pygments import lex
from pygments.token import *
# R DESCRIPTION file is based on Debian control files syntax
from pygments.lexers.installers import DebianControlLexer

BASE_PACKAGES = [
            'R',
            'utils',
            'mgcv',
            'foreign',
            'survival',
            'tcltk',
            'translations',
            'cluster',
            'MASS',
            'grDevices',
            'nlme',
            'grid',
            'base',
            'compiler',
            'KernSmooth',
            'class',
            'spatial',
            'boot',
            'tools',
            'lattice',
            'nnet',
            'graphics',
            'methods',
            'codetools',
            'stats4',
            'rpart',
            'datasets',
            'stats',
            'splines',
            'parallel',
            'Matrix',
        ]

def enum(**enums):
    return type('Enum', (), enums)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


PackStatus = enum(
        PARSED=0,
        DOWNLOADED=1,
        DOWNLOAD_FAILED=2,
        INSTALLED=3,
        INSTALL_FAILED=4,
        NOT_FOUND=5,
        INVALID=6,
        )


class PackInfo(object):
    def __init__(self, name, version=None):
        self.name = name
        self.version = version
        self.status = None
        self.install_date = None
        self.fullstatus = None
        self.provider = None
        self.repos = None
        self.depends = None
        self.imports = None
        self.author = None
        self.title = None
        self.date = None

    @property
    def fullname(self):
        if self.version:
            return('{0}-{1}'.format(self.name, self.version))
        else:
            return self.name


def update_from_desc(pack, filepath):
    if not os.path.exists(filepath):
        pack.status = PackStatus.INVALID
        pack.fullstatus = 'DESCRIPTION file not FOUND'
        raise(IOError, 'DESCRIPTION file not found')
    desc = parse_description(filepath)
    clean_desc(desc)
    pack.version = desc['version']
    pack.author = desc['author']
    pack.depends = desc['depends']
    pack.imports = desc['imports']
    pack.title = desc['title']
    pack.date = desc['date']

def parse_description(fp):
    code = open(fp, 'r').read()
    context = None
    finished = True
    function = False
    d = {
        'version': None,
        'author': None,
        'depends': None,
        'imports': None,
        'title': None,
        'date': None,
    }
    lexer = DebianControlLexer()
    g = lex(code, lexer)
    for kind, value in g:
        #print('{0} -> {1}'.format(kind, value))
        if kind == Keyword:
            context = value.lower()
            function = False
            finished = False
            d[context] = ''
        elif kind == Text.Whitespace:
            continue
        elif kind == Literal.String or kind == Literal.Number:
            if context:
                if value.endswith(','):
                    finished = False
                    if not function:
                        d[context] += value
                else:
                    finished = True
                    if not function:
                        d[context] += value
                        context = None
        elif kind == Text:
            if value == ': ':
                continue
            if value == '\n':
                if context and not finished:
                    d[context] += value
                else:
                    context = None
                    finished = True
                    continue
            else:
                if context:
                    if function:
                        v = value.strip()
                        if v in [' ', '(']:
                            continue
                        elif v in [',', '),']:
                            d[context] += ','
                    else:
                        if not finished:
                            d[context] += value
        elif kind == Name.Function:
            function = True
            d[context] += value
        if kind == Error:
            if context and not finished:
                d[context] += value
        elif kind == Generic.Strong:
            if context and not finished:
                d[context] += value
    return d

def clean_desc(d):
    for key in d:
        if key in [
            'author', 'description','suggests', 'depends'
            'maintainer', 'title', 'imports']:
            if d[key]:
                d[key].replace(',\n', ',')
                d[key].replace('\n', ' ')

