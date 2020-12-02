import dateutil

BASEDATE = dateutil.utils.default_tzinfo(
    dateutil.parser.parse("1/1/1970"), dateutil.tz.UTC
)

BASEDIR = "Files"
