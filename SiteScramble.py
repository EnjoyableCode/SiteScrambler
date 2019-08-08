'''
SiteScrambler class
Authored by Colin Nicholson
06/2018
'''
from bs4 import BeautifulSoup

from random import randint

import requests

import re

import os

class SiteScramble:
    def __init__(self, html, noise_level, filenum, url):
        self.filenum = filenum
        self.soup = BeautifulSoup(html)
        self.noise_level = noise_level
        self.url = url
        self.css_file_list = []
        self.att_dict = None
        self.cwd = os.getcwd()
        self.html = ''

    def _change_image_hrefs(self):
        '''
        Changes hrefs in HTML so they have absolute paths instead
        of relative for images.
        This way we can open the file locally with the right path.  
        @returns: str - html with absolute paths 
        '''
        imgEls = self.soup.findAll("img")
        for el in imgEls:
            try:
                if el["src"] and el["src"][0] == '/':
                    el["src"] = url + el["src"]
            except:
                pass
        #return str(self.soup).decode('utf-8')
        return str(self.soup)

    def _get_color(self,html_text):
        '''
        Extracts CSS color code from HTML
        @param html_text - HTML fragment with CSS in it   
        @returns: str - CSS color code 
        '''
        color = None
        text_split = html_text.split(';')
        color = [x for x in text_split if 'color' in x]

        if color:
            color = color[0].split(':')[1]
        return color

    def _get_atts_to_change(self):
        '''
        Searches through HTML for colors, images, and font-sizes we
        want to change later.
        '''

        self.html = self._change_image_hrefs()

        att_dict = {}
        colors = []
        images = []
        font_sizes = []

        if self.soup.findAll('body')[0].get('bgcolor'):
             colors.append(self.soup.findAll('body')[0]['bgcolor'])

        pEls = self.soup.findAll('p')

        for p in pEls:
            if p.get('style') and 'color' in p['style']:
                c = self._get_color(p['style'])
                if c not in colors:
                     colors.append(c)

        imgEls = self.soup.findAll('img')

        for img in imgEls:
            if img.get('height') and img.get('width') and [img.get('height'),img.get('width')] not in images:
                 images.append([img.get('height'),img.get('width')])

        allEls = self.soup.findAll()

        #print len(allEls)
        for el in allEls:
        
            if el.get('style') and 'font-size' in el.get('style'):
                font_sizes.append(el.get('style'))

        if colors:
            att_dict['colors'] = colors
        if images:
            att_dict['images'] = images
        if font_sizes:
            att_dict['font-sizes'] = font_sizes
        self.att_dict = att_dict

    def check_valid_css(self,html_string):
        '''
        Checks to see if string of HTML is a valid CSS code
        '''

        valid_chars = ['a', 'b', 'c', 'd', 'e', 'f']
        valid_chars = valid_chars + [str(x) for x in range(10)]
        is_valid = True

        for h in html_string:
            if h not in valid_chars:
                is_valid = False

        return is_valid
    

    def _change_css(self,css_file, index, num):
        '''
        Goes through a CSS file and replaces color with
        a new one
        @param css_file - CSS file
        @param index - Index of file we are on
        '''
        if not self.att_dict:
            self._get_atts_to_change()

        if 'http' not in css_file:
            css_file = self.url + css_file
        r = requests.get(css_file)
        css_html = r.text
        all_matches = re.findall(r'#.{6}', css_html, re.MULTILINE)
        valid_css = list(set(x for x in all_matches if self.check_valid_css(x.replace('#',''))))
        
        for val in valid_css:
            new_color = self._change_color(val, self.noise_level)
            css_html = css_html.replace(val, new_color)
        with open('output/newcss' + str(num) + str(index) + '.css', 'w') as f:
            #f.write(css_html.encode('utf-8'))
            f.write(str(css_html))

    def get_css(self):
        '''
        Extracts CSS files from HTML
        '''

        allEls = self.soup.findAll('head')[0].findChildren()
        css_file_list = []
        index = 0

        for p in allEls:
            if p.get('href') and '.css' in p.get('href'):
                self._change_css(p.get('href'), index, self.filenum)
                css_file_list.append(p.get('href'))
                index += 1
        self.css_file_list = css_file_list

    

    def _change_color(self,orig_color, color_range):
        '''
        Scrambles CSS color code to produce new color
        @param orig_color - original color used by HTML 
        @param color_range - maximum range of change to CSS color 
        @returns: str - new color code 
        '''
        hex_list = list(orig_color.replace('#','').lower())
        color_num = {'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15,
                10:'a', 11:'b', 12:'c', 13:'d', 14:'e', 15:'f'}
        new_color = []

        try:
            for hex_val in hex_list:
                if hex_val.isalpha():
                    hex_val = color_num[hex_val]
                bump = randint(0,color_range)
                new_val = (int(hex_val) + bump) % 16
                if new_val > 9:
                   new_val = color_num[new_val]
                new_color.append(new_val)

            return '#' + ''.join(str(n) for n in new_color)
        except Exception as e:
            print('error changing color' + str(e))
            return orig_color

    def change_image_hrefs(self):
        '''
        Appends main URL to relative image hrefs to make them 
        absolute
        '''    
        imgEls = self.soup.findAll("img")
        for el in imgEls:
            try:
                if el["src"] and el["src"][0] == '/':
                     el["src"] = self.url + el["src"]
            except:
                 pass
        html = str(self.soup.decode('utf-8'))

    def change_css_files(self):
        '''
        Makes new CSS files and replaces the paths with the old
        CSS files with the new ones
        '''
        for index,css_file in enumerate(self.css_file_list):
            newfile = 'file://' + self.cwd + '/output/' + 'newcss' + str(self.filenum) + str(index) + '.css'
            self.html = self.html.replace(css_file,newfile)

    def _change_font_size(self,fs):
        '''
        Scrambles CSS font size to produce new font size
        @param fs - original font size used by HTML 
        @returns: str - new font size (or old one if we error)
        '''
        negate = randint(0,1)
        change_level = randint(0,self.noise_level)
        font_size_split = fs.split(';')
        size = ''
        px = False
        pt = False
        percent = False
        for fss in font_size_split:
            if 'font-size' in fss:
                size = fss.replace('font-size:','')
                if '%' in size:
                    size = size.replace('%','')
                    percent = True
                if 'pt' in size:
                    size = size.replace('pt','').strip()
                    pt = True
                if 'px' in size:
                    size = size.replace('px','').strip()
                    px = True
        if size:
            try:
                new_size = int(size)
            except:        
                size = randint(1,9)
            new_fs = int(size) * change_level
            if negate == 0:
                new_fs = new_fs + int(size)
            new_fs = 'font-size: ' + str(new_fs)
            if percent:
                new_fx = new_fs + '%'
            if px:
                new_fs = new_fs + 'px'
            if pt:
                new_fs = new_fs + 'pt'
        else:
            new_fs = fs
        return new_fs


    def _change_image_size(self,im):
        '''
        Scrambles image size to produce new size
        @param im - original image size by HTML 
        @returns: str - new image size 
        '''
        negate = randint(0,1)
        change_level = randint(0,self.noise_level)
        new_height = im[0] * change_level
        new_width = im[1] * change_level
        if negate == 0:
            new_height = new_height + im[0]
            new_width = new_width + im[0]
        return (int(new_height), int(new_width))


    def scramble_colors(self):
        '''
        Scrambles CSS colors in HTML
        '''
        self.get_css()
        if not self.att_dict:
            self._get_atts_to_change()
        self.change_css_files()
        if 'colors' in self.att_dict:
            for c in self.att_dict['colors']:
                newc = self._change_color(c,self.noise_level)
                self.html = self.html.replace(c,newc)

    def scramble_image_sizes(self):
        '''
        Scrambles image sizes in HTML
        '''
        if not self.att_dict:
            self._get_atts_to_change()
            
        if 'images' in self.att_dict:
            for im in self.att_dict['images']:
                newim = self._change_images(im)
                self.html = self.html.replace('height="' + im[0],'height="' + str(newim[0]))
                self.html = self.html.replace('width="' + im[1],'width="' + str(newim[1]))


    def scramble_font_sizes(self):
        '''
        Scrambles font sizes in HTML
        '''
        if not self.att_dict:
            self._get_atts_to_change()
            
        if 'font-sizes' in self.att_dict:
            for fs in self.att_dict['font-sizes']:
                newfs = self._change_font_size(fs)
                self.html = self.html.replace(fs,newfs)
