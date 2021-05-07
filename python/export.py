#!/usr/bin/env python

import StringIO
import datetime
import json
import os
import pdb
import pprint
import re
import setuptools
import scribus
import shutil
import struct
import sys
import urllib2
import uuid

import boto3
import botocore

from bs4 import BeautifulSoup
from dotmap import DotMap
from xml.etree import ElementTree as et

DOMAIN = os.environ['APLUS_DOMAIN']
EMAIL = os.environ['APLUS_USER']
PASSWORD = os.environ['APLUS_PASS']
BUCKET = os.environ['BUCKET']
S3_RESOURCE = boto3.resource('s3')
CURRENT_PATH = os.path.dirname(os.path.realpath('__file__'))
TEMP_PATH = os.path.join(CURRENT_PATH, 'tmp/')
HEX = uuid.uuid4().hex
MM_FACTOR = 2.83464566929134
BLEED = str(5 * MM_FACTOR)
FONTS = []

def byteify(input):
  if isinstance(input, dict):
    return {byteify(key): byteify(value)
      for key, value in input.iteritems()}
  elif isinstance(input, list):
    return [byteify(element) for element in input]
  elif isinstance(input, unicode):
    return input.encode('utf-8')
  else:
    return input

def make_dirs(key):
  path = os.path.dirname(key)
  try:
    os.makedirs(path)
  except OSError:
    if not os.path.isdir(path):
      raise

def download_img(key):
  clean_key = urllib2.unquote(str(key[:key.find("?")]))
  new_file = os.path.join(TEMP_PATH, clean_key)
  if os.path.isfile(new_file): return new_file

  make_dirs(new_file)
  S3_RESOURCE.meta.client.download_file(BUCKET, clean_key, new_file)
  return new_file

def download_eps(eps):
  new_file = os.path.join(TEMP_PATH, eps.filename)
  if os.path.isfile(new_file): return new_file

  make_dirs(new_file)
  S3_RESOURCE.meta.client.download_file(BUCKET, eps.key, new_file)
  return new_file

def upload(low_local, low_key, high_local, high_key):
  S3_RESOURCE.meta.client.upload_file(low_local, BUCKET, low_key)
  S3_RESOURCE.meta.client.upload_file(high_local, BUCKET, high_key)

def apply_font(fonts, font, frame):
  try:
    scribus.setFont(font, frame)
  except ValueError, e:
    apply_font(fonts, "Helvetica Neue LT Std 65 Medium", frame)
  else:
    fonts.append(font)

def stylise(style, frame, fonts):
  if style.size:
    scribus.setFontSize(float(style.size), frame)
  if style.colour:
    scribus.setTextColor(new_colour(style.colour), frame)
  if style.alignment:
    align = eval("scribus.ALIGN_{}".format(style.alignment.upper()))
    scribus.setTextAlignment(align, frame)
  if style.line_height:
    scribus.setLineSpacing(float(style.line_height), frame)
  if style.font:
    apply_font(fonts, style.font, frame)

def new_colour(col):
  if type(col) == str:
    if '(' in col:
      name, _val = col.split(' (')
      if name == 'CLIENT1' or name == 'CLIENT2': return name
      val = _val.rstrip(')')
      if val is not None:
        colour = map(int, val.split(','))
        scribus.defineColorCMYKFloat(name, *colour)
      return name
    else:
      return col
  else:
    for name, val in col.items():
      if name == 'CLIENT1' or name == 'CLIENT2': return name
      if val is not None:
        colour = map(int, val.split(','))
        scribus.defineColorCMYKFloat(name, *colour)
      return name

def frame_and_image_width(frame):
  fw, fh = scribus.getSize(frame)
  scribus.setScaleFrameToImage(frame)
  iw, ih = scribus.getSize(frame)
  scribus.sizeObject(fw, fh, frame)
  return fw, iw

def right_align_image(frame):
  fw, iw = frame_and_image_width(frame)
  scribus.setScaleFrameToImage(frame)
  scribus.moveObject(float(fw - iw), 0.0, frame)

# NOTE: Expansion methods cannot be called from each other. Suspect a memory
# overflow of some sort.
def expand_frame_from_bottom(frame):
  w, h = scribus.getSize(frame)
  while (scribus.textOverflows(frame) == 0 and h > 0):
    h -= 10
    scribus.sizeObject(w, h, frame)

  # Expansion methods fail to reduce without this hack.
  h -= 10
  scribus.sizeObject(w, h, frame)

  while (scribus.textOverflows(frame) > 0):
    h += 1
    scribus.sizeObject(w, h, frame)

  x, y = scribus.getPosition(frame)
  scribus.moveObjectAbs(x, float(y - h), frame)

# NOTE: Same notes above apply.
def expand_frame_from_top(frame):
  w, h = scribus.getSize(frame)
  while (scribus.textOverflows(frame) == 0 and h > 0):
    h -= 10

  h -= 10
  scribus.sizeObject(w, h, frame)

  while (scribus.textOverflows(frame) > 0):
    h += 1
    scribus.sizeObject(w, h, frame)

def formatted_designator(var):
  if 'caps' in var.designator:
    return var.name.upper()
  elif 'word' in var.designator:
    return var.name
  elif 'initial' in var.designator:
    return var.name[0]
  elif 'icon' in var.designator:
    return var.name.capitalize()
  else:
    return ''

def formatted_frame_var(var):
  designator = formatted_designator(var)
  gsub_body = re.sub(' \\r\\n', '\\r\\n', var.body)
  body = gsub_body.rstrip()
  str = ''

  if 'tab' in var.designator:
    str = "{0} \t {1}".format(designator, body)
  elif designator != '':
    str = "{0} {1}".format(designator, body)
  else:
    str = body

  if var.suffix == "double_return":
    return "{0}\n\n".format(str)
  elif var.suffix == "space" and var.designator == "icon":
    return "{0}\n".format(str)
  elif var.suffix == "space":
    return "{0}".format(str)
  else:
    return "{0}\n".format(str)

# NOTE: Placement inserts a new page and switches back to the first. It is
# unclear where the spare page is inserted so I figure it's n + 1. Also, moving
# things manually won't work so _always sort in the JSON first_.
def place_snippet(eps, eps_count, total):
  eps_file = download_eps(eps)
  scribus.setActiveLayer('eps')
  scribus.placeVectorFile(eps_file)
  scribus.applyMasterPage('MASTER', scribus.currentPage())
  orig = scribus.getPageItems()[0][0]
  scribus.moveObjectAbs(eps.x, eps.y, orig)
  x, y = scribus.getPosition(orig)
  w, h = scribus.getSize(orig)
  pw, ph = scribus.getPageSize()

  # make up for empty space manually
  if eps.page_number > 1 and w < 124 and w > 118:
    scribus.moveObject(20, 20, orig)
  delete_excess_pages(total)

def delete_excess_pages(total):
  while (int(scribus.pageCount()) > int(total)):
    scribus.deletePage(scribus.pageCount())

def pdf(path, pages, fonts):
  pdf = scribus.PDFfile()
  pdf.compress = True
  pdf.compressmtd = 1
  pdf.file = path
  pdf.pages = list(pages)
  pdf.fonts = fonts
  pdf.pageLayout = 1
  pdf.fontEmbedding = 1
  pdf.version = 15
  return pdf

def select_text(i, j, frame):
  try:
    scribus.selectText(i, j, frame)
  except IndexError:
    scribus.selectText(0, j, frame)

def main(argv):
  document_id = argv[1]
  creds = { 'email': EMAIL, 'password': PASSWORD }
  req = urllib2.Request('{0}/api/v4/users/sign_in/'.format(DOMAIN))
  req.add_header('Content-Type', 'application/json')
  resp = urllib2.urlopen(req, json.dumps(creds)).read()
  token = json.loads(resp)["response"]
  req = urllib2.Request("{0}/api/v4/documents/{1}/".format(DOMAIN, document_id))
  req.add_header('Authorization', "Bearer {0}".format(token))
  resp = urllib2.urlopen(req).read()
  json_resp = byteify(json.loads(resp))
  document = DotMap(json_resp).document
  resource_size = 0
  document_file = json.loads(resp)

  json_file = "json/{0}.json".format(document_id)
  json_file_path = os.path.join(TEMP_PATH, json_file)
  with open(json_file_path, "w+") as data_file:
    json.dump(document_file, data_file, indent=4, sort_keys=True)

  start = datetime.datetime.now().replace(microsecond = 0)
  low_key = "pdf/{0}/{1}/{2}_{3}_low.pdf".format(document_id, HEX, document_id, HEX)
  high_key = "pdf/{0}/{1}/{2}_{3}_high.pdf".format(document_id, HEX, document_id, HEX)
  low_path = os.path.join(TEMP_PATH, low_key)
  high_path = os.path.join(TEMP_PATH, high_key)
  sla_path = os.path.join(TEMP_PATH, "sla/{0}_{1}.sla".format(document_id, HEX))
  cursor_on_first = filter(lambda f: f.content_type == 'component_cursor' and f.page_number == 1, document.frames)

  if document.template_page_size_preset.startswith('PAPER'):
    scribus.newDocument(
      eval("scribus.{0}".format(document.template_page_size_preset)),
      (0, 0, 0, 0), scribus.PORTRAIT, 1, scribus.UNIT_MILLIMETERS,
      scribus.PAGE_1, 0, document.total_pages)
  else:
    width = float(document.template_page_width)
    height = float(document.template_page_height)
    if width > height: orientation = 'LANDSCAPE'
    else: orientation = 'PORTRAIT'
    scribus.newDocument(
      (width, height), (0, 0, 0, 0), scribus.PORTRAIT, 1,
      scribus.UNIT_MILLIMETERS, scribus.PAGE_1, 0, document.total_pages)

  make_dirs(sla_path)
  scribus.createLayer('eps')
  scribus.createLayer('frames')

  colours1 = map(int, document.colour1.split(','))
  colours2 = map(int, document.colour2.split(','))

  scribus.defineColorCMYKFloat('CLIENT1', *colours1)
  scribus.defineColorCMYKFloat('CLIENT2', *colours2)
  scribus.createMasterPage('MASTER')
  scribus.saveDocAs(sla_path)
  scribus.closeDoc()

  tree = et.parse(sla_path)
  xml = tree.find('DOCUMENT')
  xml.set('BleedTop', BLEED)
  xml.set('BleedBottom', BLEED)
  xml.set('BleedLeft', BLEED)
  xml.set('BleedRight', BLEED)
  tree.write(sla_path)
  scribus.openDoc(sla_path)

  for component in reversed(document.components):
    for eps in reversed(component.snippets):
      if eps.key is not None:
        place_snippet(eps, len(component.snippets), document.total_pages)
        resource_size += eps.size

  scribus.saveDoc()

  if len(cursor_on_first) > 0:
    scribus.newPage(1)
    scribus.applyMasterPage('MASTER', 1)
    delete_excess_pages(document.total_pages)

  for frame in document.frames:
    if frame.page_number == 0:
      scribus.editMasterPage('MASTER')
    else:
      scribus.gotoPage(frame.page_number)
      scribus.applyMasterPage('MASTER', frame.page_number)

    scribus.setActiveLayer('frames')
    key = "frame_{0}".format(frame.name.replace(' ', '_').lower())

    if frame.cmyk_colour: new_colour(frame.cmyk_colour)

    if frame.content_type == 'text':
      globals()[key] = scribus.createText(
        float(frame.x), float(frame.y), float(frame.width), float(frame.height),
        key)

      if frame.frame_style: stylise(frame.frame_style, key, FONTS)

      for var in frame.frame_variables:
        if var.html_tag != 'img' and var.body:
          html = formatted_frame_var(var)
          soup = BeautifulSoup(html, 'html.parser')

          # within html
          if soup.b:
            print 'SOUP B {0}'.format(soup.b)
            indicies = []
            tag_len = 3

            for tag in soup.find_all('b'):
              cursor = 0
              inner_text = tag.string.extract()
              inner_text_len = len(inner_text)

              # adds the cursor position
              for el in tag.previous_siblings:
                # print el.string
                # print '---start---'
                # print len(el.string)
                # print len(repr(el.string))
                # print '---end---'
                cursor = cursor + len(el.string)

              indicies.append([cursor, inner_text_len])
              print '{0} {1}'.format(cursor, inner_text_len)
              cursor = cursor + inner_text_len
              tag.replace_with(inner_text)

            new_html = str(soup)
            scribus.insertText(new_html, -1, key)
            frame_len = scribus.getTextLength(key)
            var_len = len(new_html)
            designator_len = len(formatted_designator(var))

            # testing to see if -1 is needed two lines down
            if var.variable_style:
              select_text(min(0, frame_len - var_len), min(frame_len, var_len - tag_len), key)
              stylise(var.variable_style, key, FONTS)

            for i in indicies:
              select_text(i[0] - i[1], i[1], key)
              apply_font(FONTS, 'Helvetica Neue LT Std 75 Bold', key)

            if designator_len > 0:
              select_text(frame_len - var_len + designator_len + 2, designator_len, key) # space
              apply_font(FONTS, 'Helvetica Neue LT Std 75 Bold', key)

          else:
            scribus.insertText(html, -1, key)

            frame_len = scribus.getTextLength(key)
            white_len = len(html.split('\n')) + len(html.split('\r'))
            var_len = len(html)
            designator_len = len(formatted_designator(var))

            if var.variable_style:
              select_text(frame_len - var_len, min(frame_len, var_len), key)
              stylise(var.variable_style, key, FONTS)

            if designator_len > 0:
              select_text(frame_len - var_len, designator_len, key)
              apply_font(FONTS, 'Helvetica Neue LT Std 75 Bold', key)

            if var.html_tag == 'strong':
              select_text(0, min(frame_len, var_len), key)
              apply_font(FONTS, 'Helvetica Neue LT Std 75 Bold', key)

        elif var.html_tag == 'img' and var.body:
          expand_frame_from_top(key)
          adjust = scribus.getSize(key)
          img_key = "{0}_{1}".format(key, var.id)
          img = download_img(var.key)
          resource_size += os.path.getsize(img)
          scribus.createImage(
            float(frame.x), float(frame.y + adjust[1] + 3), float(frame.width),
            float(frame.width), img_key)
          scribus.textFlowMode(img_key, 2)
          scribus.loadImage(img, img_key)
          scribus.setScaleImageToFrame(1, 1, img_key)
          scribus.setScaleFrameToImage(img_key)
          scribus.insertText(" \n", -1, key)

      if frame.direction == 'up':
        expand_frame_from_bottom(key)
      elif frame.height > 0:
        expand_frame_from_top(key)

    elif frame.content_type == 'image':
      for variable in frame.frame_variables:
        if variable.key is not None:
          img = download_img(variable.key)
          resource_size += os.path.getsize(img)
          globals()[key] = scribus.createImage(
            float(frame.x), float(frame.y), float(frame.width),
            float(frame.height), key)
          scribus.loadImage(img, key)
          scribus.setScaleImageToFrame(1, 1, key)
          if frame.frame_style:
            if frame.frame_style.alignment == 'right': right_align_image(key)

    elif frame.content_type == 'vector':
      globals()[key] = scribus.createRect(
        float(frame.x), float(frame.y), float(frame.width), float(frame.height),
        key)
      if frame.frame_style:
        scribus.setFillColor(new_colour(frame.frame_style.colour), key)
        scribus.setLineColor(new_colour(frame.frame_style.colour), key)

    elif frame.content_type == 'line':
      globals()[key] = scribus.createLine(
        float(frame.x), float(frame.y),
        float(frame.x + frame.width), float(frame.y + frame.height),
        key)
      scribus.setLineWidth(float(frame.width), key)
      if frame.frame_style:
        scribus.setFillColor(new_colour(frame.frame_style.colour), key)

    if frame.page_number == 0: scribus.closeMasterPage()

  pi = 1
  pr = scribus.pageCount()
  while (pi <= pt):
    scribus.gotoPage(pi)
    scribus.applyMasterPage('MASTER', pi)
    pi += 1

  scribus.saveDoc()

  pages = list(range(1, document.total_pages + 1))
  fonts = list(set(FONTS))

  make_dirs(low_path)
  low = pdf(low_path, list(pages), fonts)
  low.outdst = 0
  low.quality = 2
  low.resolution = 144
  low.useDocBleeds = False
  low.save()

  high = pdf(high_path, list(pages), fonts)
  high.cropMarks = True
  high.doClip = False
  high.outdst = 1
  high.quality = 1
  high.resolution = 300
  high.useDocBleeds = True
  high.save()

  upload(low_path, low_key, high_path, high_key)

  result = { 'pdf_result': {
    'press_ready_url': high_key, 'low_resolution_url': low_key,
    'error_code': None, 'created': True
  } }

  req = urllib2.Request("{0}/api/v4/documents/{1}/".format(DOMAIN, document_id))
  req.get_method = lambda: 'PATCH'
  req.add_header('Authorization', "Bearer {0}".format(token))
  req.add_header('Content-Type', 'application/json')
  resp = urllib2.urlopen(req, json.dumps(result)).read()

  finish = datetime.datetime.now().replace(microsecond = 0)
  interval = (finish - start).total_seconds()

  print "[pdf] Sent {0}b {1} {2}/{3} in {4}s".format(resource_size, document.template, document_id, HEX, interval)
  return 0

if __name__ == '__main__': main(sys.argv)

