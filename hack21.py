

import sys
import os
import re
from urllib2 import HTTPError

import mechanize
assert mechanize.__version__ >= (0, 0, 6, "a")

mech = mechanize.Browser()
mech.set_handle_robots(False)
# mech.set_debug_http(True)

# Get the starting search page
try:
    mech.open("https://coinmarketcap.com/")
except HTTPError, e:
    sys.exit("%d: %s" % (e.code, e.msg))

# Select the form, fill the fields, and submit
#mech.select_form(nr=0)
#mech["query"] = "Lester"
#mech["mode"] = ["author"]
#try:
#    mech.submit()
#except HTTPError, e:
#    sys.exit("post failed: %d: %s" % (e.code, e.msg))

# Find the link for "Andy"
#try:
#    mech.follow_link(text_regex=re.compile("Andy"))
#except HTTPError, e:
#    sys.exit("post failed: %d: %s" % (e.code, e.msg))

# Get all the tarballs
#urls = [link.absolute_url for link in
#        mech.links(url_regex=re.compile(r"\.tar\.gz$"))]
#print "Found", len(urls), "tarballs to download"

#if "--all" not in sys.argv[1:]:
#    urls = urls[:1]

urls = ['https://graphs.coinmarketcap.com/currencies/litecoin/1486650841000/1494336841000/']

for url in urls:
    print 'URL =',url
    filename = 'text.txt'#os.path.basename(url)
    f = open(filename, "wb")
    print "%s -->" % filename,
    r = mech.open(url)
    #while 1:
    data = r.read()
    f.write(data)
    f.close()
    print os.stat(filename).st_size, "bytes"
