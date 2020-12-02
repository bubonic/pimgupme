#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
Upload image file or image URL to the ptpimg.me image hosting.

Usage:
    python3 pimgupme.py image-file.jpg
    python3 pimgupme.py https://i.imgur.com/00000.jpg
    find ./ -maxdepth 1 -type f \( -iname \*.jpg -o -iname \*.png -o -iname \*.jpeg \) -print0 | xargs --null  pimgupme.py --bbcode --thumbnails -k ptpimgAPIkey
"""

import contextlib
import mimetypes
import os
from io import BytesIO
from sys import stdout
from PIL import Image
import sys

import requests

mimetypes.init()


class UploadFailed(Exception):
    def __str__(self):
        msg, *args = self.args
        return msg.format(*args)


class PtpimgUploader:
    """ Upload image or image URL to the ptpimg.me image hosting """

    def __init__(self, api_key, timeout=None):
        self.api_key = api_key
        self.timeout = timeout

    @staticmethod
    def _handle_result(res):
        image_url = 'https://ptpimg.me/{0}.{1}'.format(
            res['code'], res['ext'])
        return image_url

    def _perform(self, files=None, **data):
        # Compose request
        headers = {'referer': 'https://ptpimg.me/index.php'}
        data['api_key'] = self.api_key
        url = 'https://ptpimg.me/upload.php'

        resp = requests.post(
            url, headers=headers, data=data, files=files, timeout=self.timeout)
        # pylint: disable=no-member
        if resp.status_code == requests.codes.ok:
            try:
                # print('Successful response', r.json())
                # r.json() is like this: [{'code': 'ulkm79', 'ext': 'jpg'}]
                return [self._handle_result(r) for r in resp.json()]
            except ValueError as e:
                raise UploadFailed(
                    'Failed decoding body:\n{0}\n{1!r}', e, resp.content
                ) from None
        else:
            raise UploadFailed(
                'Failed. Status {0}:\n{1}', resp.status_code, resp.content)

    def upload_files(self, *filenames):
        """ Upload files using form """
        # The ExitStack closes files for us when the with block exits
        with contextlib.ExitStack() as stack:
            files = {}
            for i, filename in enumerate(filenames):
                open_file = stack.enter_context(open(filename, 'rb'))
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type or mime_type.split('/')[0] != 'image':
                    raise ValueError(
                        'Unknown image file type {}'.format(mime_type))

                name = os.path.basename(filename)
                try:
                    # until https://github.com/shazow/urllib3/issues/303 is
                    # resolved, only use the filename if it is Latin-1 safe
                    name.encode('latin1')
                except UnicodeEncodeError:
                    name = 'justfilename'
                files['file-upload[{}]'.format(i)] = (
                    name, open_file, mime_type)
            return self._perform(files=files)

    def upload_urls(self, *urls):
        """ Upload image URLs by downloading them before """
        with contextlib.ExitStack() as stack:
            files = {}
            for i, url in enumerate(urls):
                resp = requests.get(url, timeout=self.timeout)
                if resp.status_code != requests.codes.ok:
                    raise ValueError(
                        'Cannot fetch url {} with error {}'.format(url, resp.status_code))

                mime_type = resp.headers['content-type']
                if not mime_type or mime_type.split('/')[0] != 'image':
                    raise ValueError(
                        'Unknown image file type {}'.format(mime_type))
                open_file = stack.enter_context(BytesIO(resp.content))
                files['file-upload[{}]'.format(i)] = (
                    'file-{}'.format(i), open_file, mime_type)

            return self._perform(files=files)


def _partition(files_or_urls):
    files, urls = [], []
    for file_or_url in files_or_urls:
        if os.path.exists(file_or_url):
            files.append(file_or_url)
        elif file_or_url.startswith('http'):
            urls.append(file_or_url)
        else:
            raise ValueError(
                'Not an existing file or image URL: {}'.format(file_or_url))
    return files, urls


def upload(api_key, files_or_urls, timeout=None):
    uploader = PtpimgUploader(api_key, timeout)
    files, urls = _partition(files_or_urls)
    results = []
    if files:
        results += uploader.upload_files(*files)
    if urls:
        results += uploader.upload_urls(*urls)
    return results

def cthumbs(args):
    Imagethumbs = []
    print("Creating thumbnails for \033[30;106;52m%s\033[0m images..." %  len(args.images))
    for img in args.images:
        
        if img.startswith('http'):
            print("No support for URLs yet....Skipping....")
            continue
        
        img = img.replace('./', '')
        #print(img)
        image = Image.open(img)
        imgName, ext = img.split('.', 1)
        if args.max_scale:
            tmbheight = tmbwidth = int(args.max_scale)
            
            if int(image.size[1]) > int(image.size[0]) and int(image.size[1]) > int(args.max_scale):
                hpercent = (tmbheight/float(image.size[1]))
                wsize = int((float(image.size[0])*float(hpercent)))
                image = image.resize((wsize, tmbheight), Image.ANTIALIAS)
                #print(imgName + '_' + str(wsize) + 'x' + str(tmbheight) + '.' + ext)
                tmbName = imgName + '_' + str(wsize) + 'x' + str(tmbheight) + '.' + ext
            else:
                wpercent = (tmbwidth/float(image.size[0]))
                hsize = int((float(image.size[1])*float(wpercent)))
                image = image.resize((tmbwidth,hsize), Image.ANTIALIAS)
                #print(imgName + '_' + str(tmbwidth) + 'x' + str(hsize) + '.' + ext)
                tmbName = imgName + '_' + str(tmbwidth) + 'x' + str(hsize) + '.' + ext
        elif args.xlarge:
            tmbheight = tmbwidth = 640
            if int(image.size[1]) > int(image.size[0]) and int(image.size[1]) > 640:
                hpercent = (tmbheight/float(image.size[1]))
                wsize = int((float(image.size[0])*float(hpercent)))
                image = image.resize((wsize, tmbheight), Image.ANTIALIAS)
                #print(imgName + '_' + str(wsize) + 'x' + str(tmbheight) + '.' + ext)
                tmbName = imgName + '_' + str(wsize) + 'x' + str(tmbheight) + '.' + ext
            else:
                wpercent = (tmbwidth/float(image.size[0]))
                hsize = int((float(image.size[1])*float(wpercent)))
                image = image.resize((tmbwidth,hsize), Image.ANTIALIAS)
                #print(imgName + '_' + str(tmbwidth) + 'x' + str(hsize) + '.' + ext)
                tmbName = imgName + '_' + str(tmbwidth) + 'x' + str(hsize) + '.' + ext
        elif args.large:
            tmbheight = tmbwidth = 480
            if int(image.size[1]) > int(image.size[0]) and int(image.size[1]) > 480:
                hpercent = (tmbheight/float(image.size[1]))
                wsize = int((float(image.size[0])*float(hpercent)))
                image = image.resize((wsize, tmbheight), Image.ANTIALIAS)
                #print(imgName + '_' + str(wsize) + 'x' + str(tmbheight) + '.' + ext)
                tmbName = imgName + '_' + str(wsize) + 'x' + str(tmbheight) + '.' + ext
            else:
                wpercent = (tmbwidth/float(image.size[0]))
                hsize = int((float(image.size[1])*float(wpercent)))
                image = image.resize((tmbwidth,hsize), Image.ANTIALIAS)
                #print(imgName + '_' + str(tmbwidth) + 'x' + str(hsize) + '.' + ext)
                tmbName = imgName + '_' + str(tmbwidth) + 'x' + str(hsize) + '.' + ext
        else:
            tmbheight = tmbwidth = 320
            if int(image.size[1]) > int(image.size[0]) and int(image.size[1]) > 320:
                hpercent = (tmbheight/float(image.size[1]))
                wsize = int((float(image.size[0])*float(hpercent)))
                image = image.resize((wsize, tmbheight), Image.ANTIALIAS)
                #print(imgName + '_' + str(wsize) + 'x' + str(tmbheight) + '.' + ext)
                tmbName = imgName + '_' + str(wsize) + 'x' + str(tmbheight) + '.' + ext
            else:
                wpercent = (tmbwidth/float(image.size[0]))
                hsize = int((float(image.size[1])*float(wpercent)))
                image = image.resize((tmbwidth,hsize), Image.ANTIALIAS)
                #print(imgName + '_' + str(tmbwidth) + 'x' + str(hsize) + '.' + ext)
                tmbName = imgName + '_' + str(tmbwidth) + 'x' + str(hsize) + '.' + ext                
        Imagethumbs.append(tmbName)
        image.save(tmbName)
    print("Uploading thumbs.... \033[30;106;52m%s\033[0m" % len(Imagethumbs))
    thmb_urls = upload(args.api_key, Imagethumbs)
    print("Uploading images.... \033[30;106;52m%s\033[0m" % len(args.images))
    image_urls = upload(args.api_key, args.images)
    print("-------------------------------------URLs---------------------------------------------")

    if args.bbcode:
        printed_urls = ['[img]{}[/img]'.format(image_url) for image_url in image_urls]
        printedthmb_urls = ['[img]{}[/img]'.format(thmb_url) for thmb_url in thmb_urls]
    else:
        printed_urls = image_urls
        printedthmb_urls = thmb_urls
    print("----fullsize----")
    print(*printed_urls, sep='\n\n')
    print("-----thumbs-----")
    print(*printedthmb_urls, sep='\n\n')
    print("------------------------------------[url][/url]----------------------------------------")
    k=0
    while k < len(thmb_urls):
        print("\n[url=%s][img]%s[/img][/url]" % (image_urls[k], thmb_urls[k]), end=' ')
        try:
            print("[url=%s][img]%s[/img][/url]" % (image_urls[k+1], thmb_urls[k+1]), end='\n')
        except IndexError as e:
            pass
        k += 2
    print("\n\n")
    sys.exit()

def main():
    import argparse

    try:
        import pyperclip
    except ImportError:
        pyperclip = None

    parser = argparse.ArgumentParser(description="PTPImg uploader")
    parser.add_argument('images', metavar='filename|url', nargs='+')
    parser.add_argument('-k', '--api-key', default=os.environ.get('PTPIMG_API_KEY'),help='PTPImg API key (or set the PTPIMG_API_KEY environment variable)')
    if pyperclip is not None:
        parser.add_argument('-n', '--dont-copy', action='store_false', default=True, dest='clipboard', help='Do not copy the resulting URLs to the clipboard')
    parser.add_argument('-b', '--bbcode', action='store_true', default=False, help='Output links in BBCode format (with [img] tags)')
    parser.add_argument('--nobell', action='store_true', default=False, help='Do not bell in a terminal on completion')
    parser.add_argument('--thumbnails', action='store_true', default=False, help='Convert images to thumbnails and provide a [url=][img][/img][/url] with url to full image and [img] of thumbnail. Default width is 320px.')
    parser.add_argument('--large', action='store_true', default=False, help='Used in conjunction with --thumbnails. Creates large thumbnails, w|h <= 480')
    parser.add_argument('--xlarge', action='store_true', default=False, help='Used in conjunction with --thumbnails. Creates extra-large thumbnails, w|h <= 640')
    parser.add_argument('--max-scale', help='--max-scale <m>. Used in conjunction with --thumbnails. Will create thumbnails with max width or height equal to m pixels.')

    args = parser.parse_args()

    
    if not args.api_key:
        parser.error('Please specify an API key')
    try:
        if args.thumbnails: 
            cthumbs(args)
        else:
            
            image_urls = upload(args.api_key, args.images)
            if args.bbcode:
                printed_urls = ['[img]{}[/img]'.format(image_url) for image_url in image_urls]
            else:
                printed_urls = image_urls
            print(*printed_urls, sep='\n\n')
            # Copy to clipboard if possible
            if getattr(args, 'clipboard', False):
                pyperclip.copy('\n'.join(image_urls))
            # Ring a terminal if we are in terminal and allowed to do this
            if not args.nobell and stdout.isatty():
                stdout.write('\a')
                stdout.flush()
    except (UploadFailed, ValueError) as e:
        parser.error(e.getMessage())


if __name__ == '__main__':
    main()
