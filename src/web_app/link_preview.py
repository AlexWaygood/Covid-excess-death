from io import StringIO, BytesIO
from lxml.etree import parse, HTMLParser

import requests, imgkit
from flask import request, render_template, Response


def LinkPreview() -> str:
    page_html = requests.get(request.args['url']).text

    # Parse the HTML response
    tree = parse(StringIO(page_html), HTMLParser())

    # Get the website's title and description from its metadata
    head = tree.xpath('/html/head')[0]
    title = head.xpath('meta[@property="og:title"]/@content')[0]
    description = head.xpath('meta[@property="og:description"]/@content')[0]

    # Render the HTML version of the preview
    preview_html = render_template('preview_card.html', title=title, excerpt=description)

    # Convert the HTML into an image via imgkit, save it to a BytesIO() buffer and return it
    return Response(imgkit.from_string(preview_html, BytesIO()), mimetype='image/png')
