from io import BytesIO
from bs4 import BeautifulSoup

import requests, imgkit
from flask import request, render_template, Response


def LinkPreview() -> str:
    # Parse the HTML response
    soup = BeautifulSoup(requests.get(request.args['url']).text, 'html.parser')

    # Get the website's title and description from its metadata
    title = soup.select('meta[property="og:title"]')[0].attrs['content']
    description = soup.select('meta[property="og:description"]')[0].attrs['content']

    # Render the HTML version of the preview
    preview_html = render_template('preview_card.html', title=title, excerpt=description)

    # Convert the HTML into an image via imgkit, save it to a BytesIO() buffer and return it
    return Response(imgkit.from_string(preview_html, BytesIO()), mimetype='image/png')
