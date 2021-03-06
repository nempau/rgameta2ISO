# =================================================================
#
# Terms and Conditions of Use
#
# Unless otherwise noted, computer program source code of this
# distribution # is covered under Crown Copyright, Government of
# Canada, and is distributed under the MIT License.
#
# The Canada wordmark and related graphics associated with this
# distribution are protected under trademark law and copyright law.
# No permission is granted to use them outside the parameters of
# the Government of Canada's corporate identity program. For
# more information, see
# http://www.tbs-sct.gc.ca/fip-pcim/index-eng.asp
#
# Copyright title to all 3rd party software distributed with this
# software is held by the respective copyright holders as noted in
# those files. Users are asked to read the 3rd Party Licenses
# referenced with those assets.
#
# Copyright (c) 2016 Government of Canada
# Copyright (c) 2017 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import codecs
from datetime import date, datetime
import logging
import os
import pkg_resources
import re
from xml.dom import minidom

import click
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import yaml

LOGGER = logging.getLogger(__name__)

TEMPLATES = '{}{}templates'.format(os.path.dirname(os.path.realpath(__file__)),
                                   os.sep)

VERSION = pkg_resources.require('pygeometa')[0].version


def get_charstring(option, section_items, language,
                   language_alternate=None):
    """convenience function to return unilingual or multilingual value(s)"""

    section_items = dict(section_items)
    option_value1 = None
    option_value2 = None

    if 'language_alternate' is None:  # unilingual
        option_tmp = '{}_{}'.format(option, language)
        if option_tmp in section_items:
            option_value1 = section_items[option_tmp]
        else:
            try:
                option_value1 = section_items[option]
            except KeyError:
                pass  # default=None
    else:  # multilingual
        option_tmp = '{}_{}'.format(option, language)
        if option_tmp in section_items:
            option_value1 = section_items[option_tmp]
        else:
            try:
                option_value1 = section_items[option]
            except KeyError:
                pass  # default=None
        option_tmp2 = '{}_{}'.format(option, language_alternate)
        if option_tmp2 in section_items:
            option_value2 = section_items[option_tmp2]

    return [option_value1, option_value2]


def get_distribution_language(section):
    """derive language of a given distribution construct"""

    try:
        return section.split('_')[1]
    except IndexError:
        return 'en'


def normalize_datestring(datestring, format_='default'):
    """groks date string into ISO8601"""

    today_and_now = datetime.utcnow()

    re1 = r'\$Date: (?P<year>\d{4})'
    re2 = r'\$Date: (?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2})'
    re3 = r'(?P<start>.*)\$Date: (?P<year>\d{4}).*\$(?P<end>.*)'

    try:
        if isinstance(datestring, date):
            datestring2 = datestring.strftime('%Y-%m-%dT%H:%M:%SZ')
            if datestring2.endswith('T00:00:00Z'):
                datestring2 = datestring2.replace('T00:00:00Z', '')
            return datestring2
        if datestring == '$date$':  # $date$ magic keyword
            return today_and_now.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif datestring == '$year$':  # $year$ magic keyword
            return today_and_now.strftime('%Y')
        elif '$year$' in datestring:  # $year$ magic keyword embedded
            return datestring.replace('$year$', today_and_now.strftime('%Y'))
        elif datestring.startswith('$Date'):  # svn Date keyword
            if format_ == 'year':
                mo = re.match(re1, datestring)
                return mo.group('year')
            else:  # default
                mo = re.match(re2, datestring)
                return '%sT%s'.format(mo.group('date', 'time'))
        elif '$Date' in datestring:  # svn Date keyword embedded
            if format_ == 'year':
                mo = re.match(re3, datestring)
                return '%s%s%s'.format(mo.group('start', 'year', 'end'))
    except AttributeError:
        raise RuntimeError('Invalid datestring: {}'.format(datestring))
    return datestring


def read_mcf(mcf):
    """returns dict of YAML file from filepath"""

    mcf_list = []
    mcf_dict = {}

    def __to_dict(mcf_object):
        """normalize mcf input into dict"""

        dict_ = None

        if isinstance(mcf_object, dict):
            LOGGER.debug('mcf object is already a dict')
            dict_ = mcf_object
        elif 'metadata' in mcf_object:
            LOGGER.debug('mcf object is a string')
            dict_ = yaml.load(mcf_object)
        else:
            LOGGER.debug('mcf object is likely a filepath')
            with codecs.open(mcf_object, encoding='utf-8') as fh:
                dict_ = yaml.load(fh)

        return dict_

    def makelist(mcf2):
        """recursive function for MCF by reference inclusion"""

        c = __to_dict(mcf2)

        LOGGER.debug('reading {}'.format(mcf2))
        for key, value in c.items():
            if 'base_mcf' in value:
                base_mcf_path = get_abspath(mcf, c[key]['base_mcf'])
                makelist(base_mcf_path)
                mcf_list.append(mcf2)
            else:  # leaf
                mcf_list.append(mcf2)

    makelist(mcf)

    for mcf_file in mcf_list:
        LOGGER.debug('reading {}'.format(mcf_file))
        c_dict = __to_dict(mcf_file)

        for section in c_dict.keys():
            if section not in mcf_dict:  # add the whole section
                LOGGER.debug('section {} does not exist. Adding'.format(
                             section))
                mcf_dict[section] = c_dict[section]
            else:
                LOGGER.debug('section {} exists. Adding options'.format(
                             section))
                for key, value in c_dict[section].items():
                    mcf_dict[section][key] = value

    try:
        LOGGER.info('MCF version: {}'.format(mcf_dict['mcf']['version']))
    except KeyError:
        LOGGER.info('no MCF version specified')

    return mcf_dict


def pretty_print(xml):
    """clean up indentation and spacing"""

    LOGGER.debug('pretty-printing XML')
    val = minidom.parseString(xml)
    return '\n'.join([l for l in
                      val.toprettyxml(indent=' '*2).split('\n') if l.strip()])


def render_template(mcf, schema=None, schema_local=None):
    """
    convenience function to render Jinja2 template given
    an mcf file, string, or dict
    """

    LOGGER.debug('Evaluating schema path')
    if schema is None and schema_local is None:
        msg = 'schema or schema_local required'
        LOGGER.exception(msg)
        raise RuntimeError(msg)
    if schema_local is None:  # default templates dir
        abspath = '{}{}{}'.format(TEMPLATES, os.sep, schema)
    elif schema is None:  # user-defined
        abspath = schema_local

    LOGGER.debug('Setting up template environment {}'.format(abspath))
    env = Environment(loader=FileSystemLoader([abspath, TEMPLATES]))
    env.filters['normalize_datestring'] = normalize_datestring
    env.filters['get_distribution_language'] = get_distribution_language
    env.filters['get_charstring'] = get_charstring
    env.globals.update(zip=zip)
    env.globals.update(get_charstring=get_charstring)
    env.globals.update(normalize_datestring=normalize_datestring)

    try:
        LOGGER.debug('Loading template')
        template = env.get_template('main.j2')
    except TemplateNotFound:
        msg = 'Missing metadata template'
        LOGGER.exception(msg)
        raise RuntimeError(msg)

    LOGGER.debug('Processing template')
    xml = template.render(record=read_mcf(mcf),
                          software_version=VERSION).encode('utf-8')
    return pretty_print(xml)


def get_supported_schemas():
    """returns a list of supported schemas"""

    LOGGER.debug('Generating list of supported schemas')
    dirs = os.listdir(TEMPLATES)
    dirs.remove('common')
    return dirs


def get_abspath(mcf, filepath):
    """helper function absolute file access"""

    abspath = os.path.dirname(os.path.realpath(mcf))
    return os.path.join(abspath, filepath)


@click.command()
@click.pass_context
@click.option('--mcf',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to metadata control file (.yml)')
@click.option('--output', type=click.File('w', encoding='utf-8'),
              help='Name of output file')
@click.option('--schema',
              type=click.Choice(get_supported_schemas()),
              help='Metadata schema')
@click.option('--schema_local',
              type=click.Path(exists=True, resolve_path=True,
                              dir_okay=True, file_okay=False),
              help='Locally defined metadata schema')
def generate_metadata(ctx, mcf, schema, schema_local, output):
    if mcf is None or (schema is None and schema_local is None):
        raise click.UsageError('Missing arguments')
    else:
        content = render_template(mcf, schema=schema,
                                  schema_local=schema_local)
        if output is None:
            click.echo_via_pager(content)
        else:
            output.write(content)
