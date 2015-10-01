#!/usr/bin/env python




# Cheap configuration reader
conf = dict(kv.split('=', 1) 
            for kv in 
            open("env").read().split('\n')
            if kv)

##############################################################################

from boto.s3.connection import S3Connection
conn = S3Connection(conf["AWS_ACCESS_KEY"],
                    conf["AWS_SECRET_KEY"])

bucket = conn.get_bucket(conf["BUCKET"])

##############################################################################

from flask import Flask, Response, request
app = Flask(__name__)

# Warning: we enable debugging if DEBUG is set to anything
# (even "off", "false", "no" :-))
if conf.get("DEBUG"):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.debug = True


PAGESIZE = int(conf.get("PAGESIZE", "20"))


# Throw an exception right away, rather than waiting for the first request
HTTP_USER, HTTP_PASS = conf["HTTP_UESR"], conf["HTTP_PASS"]

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
@auth.verify_password
def verify(login, password):
    return login==HTTP_USER and password==HTTP_PASS


@app.route("/favicon.ico")
def favicon():
    return ""


@app.route("/")
@auth.login_required
def home():
    return serve("")


@app.route("/<path:path>")
@auth.login_required
def serve(path):
    if path=="" or path.endswith('/'):
        return serve_dir(path)
    else:
        return serve_file(path)


def serve_dir(path):
    marker = request.args.get("marker")
    keys = bucket.get_all_keys(prefix=path, delimiter='/', max_keys=PAGESIZE+1, marker=marker)
    preflen = len(path)
    output = '<table>'
    output += '<td><a href="..">..</a></td>'
    for key in keys[:PAGESIZE]:
        output += '<tr>'
        name = key.name[preflen:]
        output += '<td><a href="{0}">{0}</a></td>'.format(name)
        size = getattr(key, "size", "DIR")
        output += '<td>{}</td>'.format(size)
        output += '</tr>'
    output += '</table>'
    if len(keys)==PAGESIZE+1:
        output += '<a href="/{}?marker={}">[Next]</a>'.format(
            path, keys[PAGESIZE-1].name)
    return output


def serve_file(path):
    key = bucket.get_key(path)
    return Response(key.get_contents_as_string(),
                    mimetype=key.content_type)


if __name__ == '__main__':
    app.run(host="0.0.0.0")

