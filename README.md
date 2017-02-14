Usage: 
Tool to export data from a relational database to different formats. Currently it is possible to export
data from oracle, mysql or postgres databases to csv and xml. There will be support for json as soon as
possible. Because a the moment minidom is used to construct the xml, in case of a large result set the
performance will suffer on systems with not enought RAM. have fun... :)
    

Options:
  -h, --help            show this help message and exit
  -o <OUTPUT FILE>, --output=<OUTPUT FILE>
                        output file
  -f <csv|xml|json>, --format=<csv|xml|json>
                        output format [csv, xml, json]
  -s <SQL FILE>, --sql=<SQL FILE>
                        sql file
  -e <TIMESTAMP>, --timestamp=<TIMESTAMP>
                        add timestamp to export file, must be a valid python
                        datetime format
  -z, --force           force overwriting of existing files

  Database options:
    -d <oracle|mysql|postgres>, --database=<oracle|mysql|postgres>
                        database type [oracle, mysql, postgres]
    -u <db username>, --username=<db username>
                        database username
    -w <db password>, --password=<db password>
                        database password
    -b <db hostname>, --host=<db hostname>
                        database hostname
    -n <db name|sid>, --dbname=<db name|sid>
                        database name, in case of oracle it's the sid

  Generic export options:
    -r <dos|unix>, --newline=<dos|unix>
                        newline character used for export, defaults to unix
                        style
    -a <dateformat>, --dateformat=<dateformat>
                        dateformat, it's a valid python date format

  CSV export options:
    -l <DELIMITER>, --delimiter=<DELIMITER>
                        delimiter used for csv export, defaults to ,
    -c <QUOTECHAR>, --quotechar=<QUOTECHAR>
                        quote charcater used for csv export, defaults to "
    -q <NONE|MINIMAL|STRING|ALL>, --quote=<NONE|MINIMAL|STRING|ALL>
                        quote style [none, minimal, string, all]

  XML export options:
    -p, --pretty        pretty print xml
    -i <INDENT CHAR>, --indent=<INDENT CHAR>
                        indent character

  JSON export options:
