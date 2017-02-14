import sys, os
import export_lib
import database
import traceback
from datetime import datetime
from optparse import OptionParser, OptionGroup

class db_export:

    def __init__(self, options):
        self.NEWLINES  = { 'DOS':export_lib.NEWLINE_DOS,'UNIX':export_lib.NEWLINE_UNIX }
        self.QUOTES    = { 'NONE':export_lib.QUOTE_NONE,'MINIMAL':export_lib.QUOTE_MINIMAL,'STRING':export_lib.QUOTE_STRING,'ALL':export_lib.QUOTE_ALL }
        self.FORMAT    = { 'CSV':self.__export_csv,'XML':self.__export_xml,'JSON':self.__export_json }
        self.DATABASES = { 'ORACLE':database.DB_ORACLE,'MYSQL':database.DB_MYSQL,'POSTGRES':database.DB_POSTGRES }

        self.options = options
        self.sql_file = export_lib.file_handler(self.options.sql, mode="r")

        self.exp_file = self.__construct_outfile()
        print self.exp_file

        # set export function
        self.export = self.FORMAT.pop(options.format.upper())

    def __construct_outfile(self):
        exp_file = None
        if self.options.__dict__['timestamp']:
            a_exp_f = self.options.output.split(".")
            if len(a_exp_f) > 1:
                exp_file = "%s_%s.%s" % (".".join(a_exp_f[0:len(a_exp_f)]), datetime.now().strftime(self.options.timestamp), a_exp_f[-1])
            else:
                exp_file = "%s_%s.%s" % (a_exp_f[0], datetime.now().strftime(self.options.timestamp), self.options.format)
        else:
            exp_file = self.options.output

        return exp_file

    def __get_db_handler(self):
        args = {}
        key_list = ['host','username','password','dbname']
        for k in key_list:
            if self.options.__dict__.has_key(k):
                args[k] = self.options.__dict__[k]
        args['db_type'] = self.DATABASES[self.options.database.upper()]

        db = database.generic_database(**args)

        return db.get_driver()

    def __export_csv(self):
        args = {}
        if self.options.__dict__['newline']:
            args['newline'] = self.NEWLINES.pop(self.options.newline.upper())
        if self.options.__dict__['dateformat']:
            args['date_format'] = self.options.dateformat
        if self.options.__dict__['delimiter']:
            args['delimiter'] = self.options.delimiter
        if self.options.__dict__['quotechar']:
            args['quotechar'] = self.options.quotechar
        if self.options.__dict__['quote']:
            args['quote'] = self.QUOTES.pop(self.options.quote.upper())

        csv_exp = export_lib.csv_helper(**args)
        csv_file = export_lib.file_handler(self.exp_file, mode="w")
        qh = database.query_handler(self.sql_file.read_file(), self.__get_db_handler())
        qh.execute_query()
        headers = qh.get_columns()
        header_line = csv_exp.format_row(headers)
        csv_file.write_encoded_line(header_line)

        for row in qh.get_result():
            line = csv_exp.format_row(row)
            csv_file.write_encoded_line(line)

        csv_file.close()

    def __export_xml(self):
        args = {}
        if self.options.__dict__['dateformat']:
            args['date_format'] = self.options.dateformat
        if self.options.__dict__['pretty']:
            args['pretty'] = self.options.pretty
        if self.options.__dict__['indent']:
            args['indent_char'] = self.options.indent

        xml_file = export_lib.file_handler(self.exp_file, mode="w")
        qh = database.query_handler(self.sql_file.read_file(), self.__get_db_handler())
        qh.execute_query()
        # construct tags
        aTags = qh.get_columns()
        tags = {}
        for idx in range(0,len(aTags)):
            tags[idx] = aTags[idx]

        xml_exp = export_lib.xml_helper(tags, **args)
        for row in qh.get_result():
            xml_exp.append_row(row)
        xml_file.write_text(xml_exp.get_document())
        xml_file.close()

    def __export_json(self):
        sys.write.stderr("ERROR: not yet implemented\n")
        sys.exit(-1)

def main(options):
    export_fname = None

    # sematic check of the command line options
    # basic options
    if os.path.exists(options.output) and not options.force:
        sys.stderr.write("ERROR: file already exists: %s\n" % (options.output))
        sys.exit(-1)

    if not options.format.lower() in ['csv','xml','json']:
        sys.stderr.write("ERROR: invalid format: %s\n" % (options.format))
        sys.exit(-1)

    if not os.path.exists(options.sql):
        sys.stderr.write("ERROR: sql file not exists: %s\n" % (options.sql))
        sys.exit(-1)

    # database options
    if not options.database.lower() in ['oracle','mysql','postgres']:
        sys.stderr.write("ERROR: invalid database type given: %s\n" % (options.database))
        sys.exit(-1)

    exp = db_export(options)
    exp.export()

if __name__ == "__main__":
    usage = """
Tool to export data from a relational database to different formats. Currently it is possible to export
data from oracle, mysql or postgres databases to csv and xml. There will be support for json as soon as
possible. Because a the moment minidom is used to construct the xml, in case of a large result set the
performance will suffer on systems with not enought RAM. have fun... :)
    """
    cmd_parser = OptionParser(usage=usage)

    db_group     = OptionGroup(cmd_parser, 'Database options')
    export_group = OptionGroup(cmd_parser, 'Generic export options')
    csv_group    = OptionGroup(cmd_parser, 'CSV export options')
    xml_group    = OptionGroup(cmd_parser, 'XML export options')
    json_group   = OptionGroup(cmd_parser, 'JSON export options')

    # basic options
    cmd_parser.add_option("-o", "--output", dest="output", metavar="<OUTPUT FILE>", help="output file")
    cmd_parser.add_option("-f", "--format", dest="format", metavar="<csv|xml|json>", help="output format [csv, xml, json]")
    cmd_parser.add_option("-s", "--sql", dest="sql", metavar="<SQL FILE>", help="sql file")
    cmd_parser.add_option("-e", "--timestamp", dest="timestamp", metavar="<TIMESTAMP>", help="add timestamp to export file, must be a valid python datetime format")
    cmd_parser.add_option("-z", "--force", dest="force", default=False, action="store_true", help="force overwriting of existing files")
    # database related options
    db_group.add_option("-d", "--database", dest="database", metavar="<oracle|mysql|postgres>", help="database type [oracle, mysql, postgres]")
    db_group.add_option("-u", "--username", dest="username", metavar="<db username>", help="database username")
    db_group.add_option("-w", "--password", dest="password", metavar="<db password>", help="database password")
    db_group.add_option("-b", "--host", dest="host", metavar="<db hostname>", help="database hostname")
    db_group.add_option("-n", "--dbname", dest="dbname", metavar="<db name|sid>", help="database name, in case of oracle it's the sid")
    # generic export options
    export_group.add_option("-r", "--newline", dest="newline", metavar="<dos|unix>", help="newline character used for export, defaults to unix style")
    export_group.add_option("-a", "--dateformat", dest="dateformat", metavar="<dateformat>", help="dateformat, it's a valid python date format")
    # csv output related options
    csv_group.add_option("-l", "--delimiter", dest="delimiter", metavar="<DELIMITER>", help="delimiter used for csv export, defaults to ,")
    csv_group.add_option("-c", "--quotechar", dest="quotechar", metavar="<QUOTECHAR>", help="quote charcater used for csv export, defaults to \"")
    csv_group.add_option("-q", "--quote", dest="quote", metavar="<NONE|MINIMAL|STRING|ALL>", help="quote style [none, minimal, string, all]")
    # xml output related options
    xml_group.add_option("-p", "--pretty", dest="pretty", default=False, action ="store_true", help="pretty print xml")
    xml_group.add_option("-i", "--indent", dest="indent", metavar="<INDENT CHAR>", help="indent character")
    # json output related options

    cmd_parser.add_option_group(db_group)
    cmd_parser.add_option_group(export_group)
    cmd_parser.add_option_group(csv_group)
    cmd_parser.add_option_group(xml_group)
    cmd_parser.add_option_group(json_group)

    (opts, args) = cmd_parser.parse_args()

    # check mandatory options
    mandatories = ['output','format','sql','database','username','password', 'dbname']
    for m in mandatories:
        if not opts.__dict__[m]:
            sys.stderr.write("ERROR: mandatory option is missing\n")
            cmd_parser.print_help()
            sys.exit(-1)

    main(opts)

    sys.exit(0)

