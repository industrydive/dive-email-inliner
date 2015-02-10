from flask import Flask, jsonify, render_template, request
import json
import os
app = Flask(__name__)
if os.environ.get('DEBUG_MODE',False):
    app.debug = True

@app.route("/")
def home():
    return render_template("form.html")

@app.route("/robots.txt")
def robotstxt():
    return "User-agent: *\r\nDisallow: /\r\n"

# Tries to inline css, raises exception if it can't
# Pass any Premailer initializer arguements in as keyword arguments
def transform_inline_css(full_html_content, **kwargs):

    # Assume we care about these, set sane defaults
    # Pop because we don't want to pass in 2 keyword
    # arguements with the same names.
    exclude_pseudoclasses = kwargs.pop('exclude_pseudoclasses', True)
    keep_style_tags = kwargs.pop('keep_style_tags', True)
    remove_classes = kwargs.pop('remove_classes', False)
    disable_basic_attributes = kwargs.pop('disable_basic_attributes', ['width','height','align'])
    strip_important = kwargs.pop('strip_important', False)
    # Remove the html value, it has been passed in seperately as full_html_content
    kwargs.pop('html', False)

    # Attempt to inline the CSS
    from premailer import transform, Premailer
    import namedentities
    p = Premailer(html=full_html_content, exclude_pseudoclasses=exclude_pseudoclasses, keep_style_tags=keep_style_tags,
                remove_classes=remove_classes, disable_basic_attributes=disable_basic_attributes, strip_important=strip_important, **kwargs)

    new_content = p.transform(encoding='ascii') # ascii output encoding means unicode is escaped
    # Need to fix the helpful replacements it made
    new_content = new_content.replace('%7B', '{')
    new_content = new_content.replace('%7D', '}')
    # replace unicode or numberic escaped unicode with named entities (where possible)
    new_content = namedentities.named_entities(new_content)

    return new_content


@app.route("/inliner", methods=['POST'])
def inline_html():
    inhtml = request.form['inhtml']
    outhtml = transform_inline_css(inhtml,keep_style_tags=False)
    return render_template("form.html", inhtml=inhtml, outhtml=outhtml)

if __name__ == "__main__":
    app.run()