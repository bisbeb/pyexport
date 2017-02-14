import datetime
import os
import codecs
import traceback
from xml.dom import minidom
import json

QUOTE_NONE=0x0
QUOTE_MINIMAL=0x1
QUOTE_STRING=0x2
QUOTE_ALL=0x3

NEWLINE_DOS="\r\n"
NEWLINE_UNIX="\n"

class csv_helper:
    """
    general csv helper functions
    """
    def __init__(self, **args):
        QUOTE_FX_LOOKUP     = { QUOTE_NONE:self.__quote_none,QUOTE_MINIMAL:self.__quote_minimal,QUOTE_STRING:self.__quote_string,QUOTE_ALL:self.__quote_all }
        self.quote_fx  = None
        self.quotechar = args.pop('quotechar', "\"")
        self.newline   = args.pop('newline', NEWLINE_UNIX)
        self.delimiter = args.pop('delimiter', ",")
        self.dt_format = args.pop('date_format', "%d.%m.%Y %H:%M:%S")
        quote          = args.pop('quote', QUOTE_MINIMAL)

        self.quote_fx = QUOTE_FX_LOOKUP[quote]

    def __quote_none(self, row):
        fx_none   = lambda s: str(s) if s else ''
        fx_date   = lambda d: d.strftime(self.dt_format) if isinstance(d, datetime.datetime) else d
        return [ fx_none(fx_date(r)) for r in row ]

    def __quote_minimal(self, row):
        fx_none   = lambda s: str(s) if s else ''
        fx_quote  = lambda s: '%s%s%s' % (self.quotechar,s,self.quotechar) if isinstance(s, str) and s.find("\n") >= 0 else s
        fx_escape = lambda s: s.replace(self.quotechar, 2*self.quotechar) if isinstance(s, str) and s.find("\n") >= 0 else s
        fx_date   = lambda d: d.strftime(self.dt_format) if isinstance(d, datetime.datetime) else d
        return [ fx_none(fx_date(fx_quote(fx_escape(r)))) for r in row ]

    def __quote_string(self, row):
        fx_none   = lambda s: str(s) if s else ''
        fx_quote  = lambda s: '%s%s%s' % (self.quotechar,s,self.quotechar) if isinstance(s, str) else s
        fx_escape = lambda s: s.replace(self.quotechar, 2*self.quotechar) if isinstance(s, str) else s
        fx_date   = lambda d: d.strftime(self.dt_format) if isinstance(d, datetime.datetime) else d
        return [ fx_none(fx_date(fx_quote(fx_escape(r)))) for r in row ]

    def __quote_all(self, row):
        fx_quote  = lambda s: '%s%s%s' % (self.quotechar,s,self.quotechar) if s else ''
        fx_escape = lambda s: s.replace(self.quotechar, 2*self.quotechar) if isinstance(s, str) else s
        fx_date   = lambda d: d.strftime(self.dt_format) if isinstance(d, datetime.datetime) else d
        return [ fx_date(fx_quote(fx_escape(r))) for r in row ]

    def format_row(self, row=[]):
        return "%s%s" % (self.delimiter.join(self.quote_fx(row)), self.newline)

class xml_helper:
    """
    class to create xml files from result set
    """
    def __init__(self, tags={}, **args):
        self.pretty     = args.pop('pretty', True)
        self.ident_char = args.pop('indent_char', "\t")
        self.dt_format  = args.pop('date_format', "%d.%m.%Y %H:%M:%S")
        self.encoding   = args.pop('encoding', "utf-8")
        self.__tags     = tags
        self.__doc      = minidom.Document()
        self.__root     = self.__doc.createElement('records')

    def append_row(self, row=[]):
        recordNode = self.__doc.createElement('record')
        for idx in range(0,len(row)):
            # ommit None values ...
            # and add empty tag
            if row[idx]:
                tmpNode = self.__doc.createElement(self.__tags[idx])
                if isinstance(row[idx], datetime.datetime):
                    value = self.__doc.createTextNode(row[idx].strftime(self.dt_format))
                else:
                    value = self.__doc.createTextNode(str(row[idx]))
                tmpNode.appendChild(value)
                recordNode.appendChild(tmpNode)
        self.__root.appendChild(recordNode)

    def get_document(self):
        self.__doc.appendChild(self.__root)
        if self.pretty:
            return self.__doc.toprettyxml(encoding=self.encoding, indent=self.ident_char)
        else:
            return self.__doc.toxml(encoding=self.encoding, indent=self.ident_char)
        return None

class json_helper:
    """
    generall json generator class
    """
    pass

class file_handler:
    """
    General file handler
    """
    def __init__(self, filename, mode="r", encoding="utf-8"):
        self.__filename = filename
        self.__mode = mode
        self.__encoding = encoding
        self.__file_handler = codecs.open(self.__filename, self.__mode, self.__encoding)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__file_handler and not self.__file_handler.closed:
            self.__file_handler.close()

    def touch(self, filename):
        touch = open(filename, "w")
        touch.close()

    def read_file(self):
        return self.__file_handler.read()

    def close(self):
        if self.__file_handler and not self.__file_handler.closed:
            self.__file_handler.close()

    def write_encoded_line(self, text):
        self.__file_handler.write(text.decode(self.__encoding))

    def write_text(self, text):
        self.__file_handler.write(text)

