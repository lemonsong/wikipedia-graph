from flask import render_template, flash, redirect, session, send_from_directory
from app import app
from app.forms import SearchForm
import requests
import json
import xml.etree.ElementTree as ET
import sys
import re

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home(title='Home'):
    """Home page"""
    form = SearchForm()

    # Get links using Wikipedia's search API
    if form.validate_on_submit():

        search_term = '_'.join(form.data['search_term'].split())
        flash(search_term)
        search_api = 'http://en.wikipedia.org/w/api.php?action=opensearch&search=' + search_term
        headers = {'Host': 'en.wikipedia.org',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                   'Accept': '*/*',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'Accept-Encoding': 'gzip, deflate',
                   'DNT': 1,
                   'Referer': 'http://www.wikipedia.org/',
                   'Connection': 'keep-alive'
        }
        response = json.loads(requests.get(search_api, headers=headers).text)
        session['links'] = response[3]  # store links in a session object to be obtained during next request
        print response
        print response[3]
        return redirect('/search_results')

    return render_template('home.html', title=title, form=form)

@app.route('/search_results')
def search_results(title='Search Results', links=None):
    """Search results, shown after user enters something in the home page"""
    links = session.pop('links', None)
    terms = [link[link.rfind('/')+1:] for link in links]  # strip beginning of link to obtain term
    return render_template('search_results.html', title=title, links=terms)

@app.route('/about')
def about(title='About'):
    """About page"""
    return render_template('about.html', title=title)


@app.route('/contact')
def contact(title='Contact'):
    """Contact page"""
    return render_template('contact.html', title=title)

@app.route('/visualization/<article_title>')
def result(article_title, title='Visualization'):
    """Visualization + a bunch of text parsing"""

    # get xml from wikipedia
    # TODO: put this in a helper function
    link_to_xml = 'http://en.wikipedia.org/wiki/Special:Export/' + article_title
    response = requests.get(link_to_xml).text.encode(sys.stdout.encoding)

    # parse xml
    root = ET.fromstring(response)
    text = root[1][3][7].text.encode(sys.stdout.encoding)  # get the child with article text
    links = re.finditer('\[\[(.+?)\]{2}', text, re.S)  # find links in text
    links = [link.group(1).decode('utf-8') for link in links]  # decode links
    new_links = list()  # create list for cleaned links
    for link in links:
        splitted = link.split("|")
        if not any(splitted[0][:5] in s for s in ["File:", "List of","Category:"]):  # check for special pages
            if splitted[0].rfind('#') == -1:  # if there's a hashtag, only get the main article title
                new_links.append(splitted[0])
            else:
                new_links.append(splitted[0][:splitted[0].rfind('#')])

    return render_template('visualization.html', title=title, links=new_links)

@app.route('/static/<path:filename>')
def server_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run()
