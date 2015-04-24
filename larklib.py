import re
import os
import sys
import subprocess
import markdown2
import datetime, time
import shutil
import yaml
import urllib
import pymarkdown
from pygments import highlight
from pygments.lexers import PythonLexer, SLexer
from pygments.formatters import HtmlFormatter

class Struct:
	def __init__(self, **entries): 
		self.__dict__.update(entries)

class Site(object):

	def __init__( self ):

		util = Util()

		# get root path
		root_path = os.getcwd()

		# load _config.yaml
		try:
			with open( os.path.join( root_path, '_config.yaml' ), 'rb') as f: 
				config_file = f.read()
		except: 
			raise RuntimeError( "Could not find or read _config.yaml file" )

		# load yaml config file
		config_dict = yaml.load( config_file )

		# make all keys lowercase
		config_dict = dict((k.lower(), v) for k,v in config_dict.iteritems())

		# convert all dict keys to attributes in site.global_vars object
		self.config_vars = Struct( **config_dict )

		# add further globals
		self.config_vars.root_path = root_path
		self.config_vars.layout_path = os.path.join( root_path, self.config_vars.layout_path )
		self.config_vars.output_path = os.path.join( root_path, self.config_vars.output_path )
		self.config_vars.url = self.config_vars.site_url
		self.config_vars.url_encoded = urllib.quote_plus( self.config_vars.url )

		util.confirm_home_page( self.config_vars )


	def set_header_vars( self, site, post_title, category, index=False ):




		if category.name == 'root':
			if index is True:
				site.title_tag = '%s' % ( site.name )
			else:
				site.title_tag = '%s > %s ' % ( post_title, site.name )

			site.banner_text = site.name.replace(' ', '')
			site.banner_url = '/'

		else:
			if index is True: 
				site.title_tag = '%s > %s' % ( site.name, category.name )
			else:
				site.title_tag = '%s > %s > %s' % ( post_title, category.name, site.name )

			#print category.config.banner_title

			try: 
				site.banner_text = category.config.banner_title.upper()
			except: 
				site.banner_text = '%s &mdash; %s' % ( site.name.replace(' ', ''), category.name.upper() )
		
			site.banner_url = '/%s/' % ( category.name )

			print site.banner_text
			print category.name 

		site.category_name = category.name

		print site.category_name

		site.title_tag_encoded = urllib.quote_plus( site.title_tag )

		return site

class Util(object):


	def confirm_css( self, css_path ):
		if not os.path.isdir( css_path ):
			print "\n**\nWARNING: NO CSS DIRECTORY \n**\n"


	def confirm_home_page( self, site ):
		if site.default_index == '':
			if not os.path.exists( os.path.join( site.root_path, '_posts' ) ):
				print "ERROR: No home page specified: If there is no _posts subdirectory in the root path, set DEFAULT_INDEX in _config.yaml to another subdirectory."		
				sys.exit()
		else: 
			if not os.path.exists( os.path.join( site.root_path, site.default_index ) ):
				pages_path = os.path.join( site.root_path, '_pages' )
				page_path = os.path.join( pages_path, site.default_index ) 
				page_path = "%s.md" % page_path
				if not os.path.exists( page_path ):
					print "ERROR: The default index specified does not exist. Revise DEFAULT_INDEX in _config.yaml."		
					sys.exit()							


	def confirm_layouts( self, layout_path ):
		if not os.path.isdir( layout_path ):
			raise RuntimeError( "ERROR: no _layouts directory in root path" )


	def confirm_posts( self, cat_list ):
		if not cat_list: 
			raise RuntimeError( "ERROR: no _posts directory in root path or subdirectories" )


	def create_redirect( self, old_published_path, new_published_path ):
		old_published_path = ensure_directory( old_published_path )
		old_published_path_index = os.path.join( old_published_path, 'index.html' )

		redirect_html = '<!DOCTYPE html><html><head><meta http-equiv="content-type" content="text/html; charset=utf-8" /><meta http-equiv="refresh" content="0;url=%s" /></head></html>' % new_published_path

		with open( old_published_path_index, 'w' ) as f:
			f.write( redirect_html )

	def create_slug_from_title( self, title ):
		post_slug = title.strip().lower()

		post_slug = post_slug.replace( " ", "-")
		post_slug = post_slug.replace( "/", "-")
		post_slug = post_slug.replace( ".", "")

		post_slug = post_slug.replace( "'", "")
		post_slug = post_slug.replace( ":", "")
		post_slug = post_slug.replace( ";", "")
		post_slug = post_slug.replace( "!", "")
		post_slug = post_slug.replace( ",", "")
		post_slug = post_slug.replace( "?", "")
		post_slug = post_slug.replace( "\"", "")
		post_slug = post_slug.replace( "(", "")
		post_slug = post_slug.replace( ")", "")
		post_slug = post_slug.replace( "#", "")
		post_slug = post_slug.replace( "\\", "-")
		post_slug = post_slug.replace( "&", "-and-")

		return post_slug

	def ensure_directory( self, directory ):
		if not os.path.exists( directory ):
			os.makedirs( directory )
		return directory

	def get_description( self, category, site ):

		try: 
			description = category.config.description
		except: 
			description = site.description

		return description 


	def get_permalink_style( self, category, site ):

		try: 
			permalink_style = category.config.permalink_style
		except: 
			permalink_style = site.permalink_style

		return permalink_style 


	def prep_html_template( self, site ):

		snippets = Snippet( site )

		with open( os.path.join( site.layout_path, 'index.html' ), 'rb' ) as f:
			html_template = f.read()

		# replace snippets
		html_template = Parse().replace_tags( 'snippet', snippets.dict, html_template )

		return html_template


	# TO-DO: make smart, page-by-page overwriting?
	def prepare_output_dir( self, site_path ):
		if os.path.exists( site_path ):
			shutil.rmtree( site_path )
		os.makedirs( site_path )

	def set_file_src_path (self, category, file_name ):

		if '*PAGE*' in file_name:
			file_name = file_name.replace( '*PAGE*', '' )
			file_source_path = os.path.join( category.pages_source_path, file_name )
		if '*POST*' in file_name: 
			file_name = file_name.replace( '*POST*', '')
			file_source_path = os.path.join( category.posts_source_path, file_name )

		return file_source_path

	def set_page_status (self, file_src_path ):

		file_is_page = False
		if '_pages/' in file_src_path:
			file_is_page = True
		return file_is_page


	def write_category_feed( self, published_category_directory_path, rss_feed_xml ):

		published_category_directory_feed = os.path.join( published_category_directory_path, 'feed.xml' )

		with open( published_category_directory_feed, 'w' ) as f:
			rss_feed_xml = rss_feed_xml.encode("utf-8")
			f.write( rss_feed_xml )
			print 'Published %s' % published_category_directory_feed

	def write_category_index( self, published_category_directory_path, index_html ):

		published_category_directory_index = os.path.join( published_category_directory_path, 'index.html' )

		with open( published_category_directory_index, 'w' ) as f:
			index_html = index_html.encode("utf-8") # was running into error w/o this with some chars
			f.write( index_html )
			print 'Published %s' % published_category_directory_index

	def write_entry( self, my_html, category, post, site ):

		util = Util()

		permalink_style = util.get_permalink_style( category, site )

		if permalink_style.lower() == "no-date" or post.is_page is True:
			entry_output_path = util.ensure_directory( os.path.join( category.output_directory, post.slug ) )

		else:		
			entry_output_path = util.ensure_directory( os.path.join( category.output_directory, post.date.year ) )
			entry_output_path = util.ensure_directory( os.path.join( entry_output_path, post.date.month ) )
			entry_output_path = util.ensure_directory( os.path.join( entry_output_path, post.date.day ) )
			entry_output_path = util.ensure_directory( os.path.join( entry_output_path, post.slug ) )

		entry_output_path_index = os.path.join( entry_output_path, 'index.html' )

		with open( entry_output_path_index, 'w' ) as f:
			my_html = my_html.encode("utf-8") # was running into error w/o this with some chars
			f.write( my_html )
			print 'Published %s' % entry_output_path_index	

		return




class Category(object):


	def __init__( self, category_name, site ):

		util = Util()

		# set category name
		self.name = category_name
		self.category_path = os.path.join( site.root_path, self.name )


		print '\n\n%s' % self.name.upper()


		# if we're not at root, parse the category's _config.yaml file if present
		if self.name != 'root':
			try: 

				configpath = os.path.join( self.category_path, '_config.yaml' )

				with open( os.path.join( self.category_path, '_config.yaml' ), 'rb') as f:
					config_file = f.read()

				config_dict = yaml.load( config_file )
				config_dict = dict((k.lower(), v) for k,v in config_dict.iteritems())
				self.config = Struct( **config_dict )

			except:
				print "Note: no config file for %s." % self.name.upper()


		self.posts_list = []
		self.pages_list = []

		# set paths for all posts and pages in category, and get all post/page names
		# also set output path
		if self.name == 'root':
			self.posts_source_path = os.path.join( site.root_path, '_posts' )
			self.pages_source_path = os.path.join( site.root_path, '_pages' )
			self.output_directory = site.output_path

			if os.path.isdir( self.posts_source_path ):
				self.posts_list = os.listdir( self.posts_source_path )
				self.posts_list = ['*POST*{0}'.format(i) for i in self.posts_list]
			if os.path.isdir( self.pages_source_path ):
				self.pages_list = os.listdir( self.pages_source_path )
				self.pages_list = ['*PAGE*{0}'.format(i) for i in self.pages_list]
		else:
			self.input_path = os.path.join( site.root_path, category_name)
			self.posts_source_path = os.path.join( self.input_path, '_posts')
			self.pages_source_path = os.path.join( self.input_path, '_pages')
			self.output_directory = util.ensure_directory( os.path.join( site.output_path, self.name ) )
			self.config_source_path = os.path.join( self.input_path, '_config.md' )

			if os.path.isdir( self.posts_source_path ):
				self.posts_list = os.listdir( self.posts_source_path )
				self.posts_list = ['*POST*{0}'.format(i) for i in self.posts_list]

			if os.path.isdir( self.pages_source_path ):
				self.pages_list = os.listdir( self.pages_source_path ) 
				self.pages_list = ['*PAGE*{0}'.format(i) for i in self.pages_list]

		# merge list of files 
		self.content_list = self.posts_list + self.pages_list

		try:
			with open( os.path.join( category.config.layout_path, 'index.html' ), 'rb' ) as f:
				html_template = f.read()
		except:
			with open( os.path.join( site.layout_path, 'index.html' ), 'rb' ) as f:
				html_template = f.read()

		try:
			self.snippet_path = os.path.join( site.root_path, self.config.snippet_path )
			cat_snippets = Snippet( self )
			
			html_template = Parse().replace_tags( 'snippet', cat_snippets.dict, html_template )
		except: 
			pass

		try:
			site_snippets = Snippet( site )
			html_template = Parse().replace_tags( 'snippet', site_snippets.dict, html_template )

		except:
			pass

		self.template = html_template


class FileHandler(object):

	class SplitRawFile(object):

		def __init__(self, file_source_path ):

			with open( file_source_path, 'rb') as f: 
				file_text = f.read()

				print "Parsing %s ... " % file_source_path

				if '---\n' in file_text: 
					split_file = str.split(file_text, '---\n', 2)
				elif '---\r\n' in file_text:  
					split_file = str.split(file_text, '---\r\n', 2)

				try: 
					self.meta_data = str(split_file[1])
					self.content = str(split_file[2])
				
				except IndexError: 
					raise RuntimeError('Post meta data isn\'t formatted properly: \n %s' % file_source_path)


	def get_title( self, raw_meta_data_text, file_source_path ):

		try:
			title = re.search('itle:(.*)\\n', raw_meta_data_text ).group(1)

		except: 
			raise RuntimeError("This post lacks a title: %s" % file_source_path )

		return title


	def get_slug( self, raw_meta_data_text, title ):

		util = Util()

		try: 
			post_slug = re.search('slug: (.*)\\n', raw_meta_data_text.lower() ).group(1)
		
		except:
			post_slug = util.create_slug_from_title( title )

		return post_slug


	def get_url( self, post, site, category ):

		permalink_style = Util().get_permalink_style( category, site )

		if category.name == 'root' and post.is_page is True:
			post_url = '/%s/' % post.slug

		else:
			if category.name == 'root' and permalink_style.lower() == 'date':
				post_url = '/%s/%s/%s/%s/' % ( post.date.year, post.date.month, post.date.day, post.slug )
			elif category.name == 'root' and permalink_style.lower() == 'no-date':
				post_url = '/%s/' % ( post.slug )
			elif post.is_page is True or permalink_style.lower() == 'no-date':
				post_url = '/%s/%s/' % ( category.name, post.slug )
			elif permalink_style.lower() == 'date':
				post_url = '/%s/%s/%s/%s/%s/' % ( category.name, post.date.year, post.date.month, post.date.day, post.slug )
							
		return post_url



	class DateObject(object):
		"""
			Provides date object for each object. This is horrendously inelegant. I'm sure
			python provides better ways to do this.
		"""
		def __init__(self, raw, entry_source_path ):

			self.undated = False

			try:
				date_text = re.search('date:(.*)\\n', raw.meta_data.lower() ).group(1).strip()
			except: 
				date_text = str(datetime.datetime.now())
				self.undated == True

			post_date_split = date_text.split( "-", 2 )
			
			self.year = post_date_split[0]
			self.month = post_date_split[1]

			if ' ' in date_text[2]:
				post_day_split = date_text[2].split( " ", 1 )
				self.day = post_day_split[0].strip()
			else:
				self.day = post_date_split[2]


			try: 
				post_hour_split = post_day_split[1].split( ":", 1 )
				post_minute_split = post_hour_split[1].split( ":" )
				self.hour = post_hour_split[0].strip()
				self.minute = post_minute_split[0].strip()

			except:
				self.hour = '0'
				self.minute = '0'

			self.published_datetime = datetime.datetime( int( self.year ), int( self.month ), int( self.day ), int( self.hour ), int( self.minute ) )
			self.y = datetime.datetime( 1970, 1, 1 )
			self.timestamp = ( self.published_datetime - self.y ).total_seconds()

			self.day_text = self.day

			if self.day_text[0] == '0':
				self.day_text = self.day_text[1:]
			
			self.month_text = datetime.datetime.fromtimestamp( int( self.timestamp ) ).strftime( '%B' )

			self.text = "%s %s, %s" % ( self.month_text, self.day_text, self.year )

			#
			#	If we forgot to date initial post, we need to re-write 
			# 	post with a date added so that it doesn't keep getting published 
			#	under the current date. 
			#
			if self.undated == True:

				raw.meta += u'Date: %s-%s-%s %s:%s\n' % ( self.year, self.month, self.day, self.hour, self.minute )

				new_file = "---\n".join( [ raw.meta, raw.content ] )

				with open( entry_source_path, 'w' ) as f:
					new_file = new_file.encode("utf-8")
					f.write( new_file )

class Parse(object):

	def replace_tags(self, tag, var_obj, html_template ):

		if isinstance(var_obj, Struct) or isinstance(var_obj, Post):
			var_dictionary = var_obj.__dict__
		else:
			var_dictionary = var_obj

		# amend template
		for key in var_dictionary:
			html_tag = "{{ %s.%s }}" % ( tag, key )
			html_text = str( var_dictionary[ key ] )
			html_template = html_template.replace( html_tag, html_text )

		return html_template

	def rss_image_paths( self, site, rss_content ):

		# delet srcset, which messes with mailchimp to rss
		rss_content = re.sub(r'srcset=\".*?\"', '', rss_content)

		# for initial paths
		abs_path = "src=\"%s/img/" % site.url
		rss_content = rss_content.replace( "src=\"/img/", abs_path )

		# for secondary paths on srcset
		rss_content = rss_content.replace( "_1920.jpg 1920w" , "_480.jpg" )
		rss_content = rss_content.replace( "_1920.jpg  1920w" , "_480.jpg" )
		rss_content = rss_content.replace( "_1920.jpg" , "_480.jpg" )

		return rss_content



	def parseRBlocks( self, site, text ):

		# current 
		currdir = os.getcwd()

		# write the file as .rmd to it
		with open( 'lark-tmp.rmd', 'w') as rmd:
			rmd.write( text )

		# set rmdcall call
		rmdcall = "Rscript -e \"library(knitr); knit('lark-tmp.rmd')\"" 

		# call knitr, which processes the r code & creates and saves .md file
		print subprocess.Popen( rmdcall, 
								shell=True, 
								stdout=subprocess.PIPE ).stdout.read()

		# read in the newly created .md file
		with open( 'lark-tmp.md', 'rb' ) as f:
			text = f.read()

		# remove the files we created  
		os.remove( 'lark-tmp.rmd' )
		os.remove( 'lark-tmp.md' )

		print site.images_path

		src_files = os.listdir('figure')

		for file_name in src_files:
			src = os.path.join( os.getcwd(), 'figure')
			full_file_name = os.path.join(src, file_name)

			imgs_path = os.path.join( site.root_path, site.images_path )
			outputfile = os.path.join( imgs_path, file_name )

			shutil.copy(full_file_name, outputfile)



		old = "(figure/"
		new = "(/%s/" % site.images_path


		text = text.replace(old, new)
		
		#shutil.rmtree( 'figure' )

		# return the new markdown file! 
		return text


	def reformatRPost( self, text ):

#		text = '<div class="cell"><div class="txtr">&nbsp;</div><div class="outputr">%s</div></div>' % text

		text = text.replace( '<p><div class="rwrap">', '</div></div><div class="rwrap">' )
#		text = text.replace( '<div class="rwrap">', '</div></div><div class="rwrap">' )

		text = text.replace( '<!-- end rwrap --></p>', '<!-- end rwrap --><div class="cell"><div class="txtr">&nbsp;</div><div class="outputr">\n')
		text = text.replace( '<!-- end rwrap --> </p>', '<!-- end rwrap --><div class="cell"><div class="txtr">&nbsp;</div><div class="outputr">\n')
		text = text.replace( '<!-- end rwrap -->\n', '<!-- end rwrap --><div class="cell"><div class="txtr">&nbsp;</div><div class="outputr">\n')

		text = text.replace( '</p>\n\n<div class="rwrap">', '</p></div></div><!-- ends .cell -->\n\n<div class="rwrap">')

		text = text.replace( '</div>\n</div><div class="txtr2">', '</div></div><div class="txtr2">')

		return text


	def reformatRHTML( self, text ):

		if '<div class="rwrap">' in text: 

			text = text.replace( '<h2 class="entry-title">', '<div class="cell"><div class="txtr">&nbsp;</div><div class="outputr"><h2 class="entry-title">' )
			text = text.replace( '</a></h2>', '</a></h2></div></div><!-- ends cell -->' )

			text = text.replace( '<div class="entry-content">', '<div class="entry-content"><div class="cell"><div class="txtr">&nbsp;</div><div class="outputr">')			
			text = text.replace( '</div><!-- ends .entry-content -->', '</div></div><!-- ends cell --><!-- ends .entry-content -->' )

			text = text.replace( '<div class="entry-footer">', '<div class="entry-footer"><div class="cell"><div class="txtr">&nbsp;</div><div class="outputr">' )
			text = text.replace( '<!-- ends .entry-footer -->' , '<!-- ends .entry-footer -->')

			text = text.replace( 'href="/css/style.css"/>', 'href="/css/style.css"/><style type="text/css">#content, #footer-info {max-width: 820px;}</style>')

		return text

	def delSubstrInclusive( self, text, str1, str2 ):

		regx = '%s(.*?)%s' % (str1, str2)
		regx_blox = re.findall( regx, text, re.DOTALL )
		for block in regx_blox:
			block = '%s%s%s' % (str1, block, str2 )
			text = text.replace( block, '' )
		return text

	def removeKnitrHashes( self, text ):
		# get rid of kntr ##s
		code_blox = re.findall ( r'\n```r\n(.*?)\n```\n\n```\n(.*?)\n```\n', text, re.DOTALL)

		#print code_blox
		i=0
		for block in code_blox:
			for blck in block:
				for b in block: 
					if i % 2 == 1:
						txt = '\n```\n%s\n```\n' % b
						txtrep = txt.replace('\n## ','\n')
						text = text.replace( txt, txtrep )
					i=i+1
		return text 

	def highlighter( self, site, text ):

		#
		#	** THIS FUNCTION IS A TOTAL MESS AND I BOW MY HEAD IN SHAME **
		#

		#
		#	ESCAPE EXAMPLE PYTHON CODE -------------------------------------------
		#
		if '\t```Python' in text:
			code_blox = re.findall ( r'\t```Python(.*?)\t```', text, re.DOTALL)
			orig_blox = []
			esc_py_blox = []

			for block in code_blox:
				orig_block = '\t```Python%s\t```' % block
				orig_blox.append( orig_block )

				# run through pygments
				block = '<pre>\t```Python%s\t```</pre>' % block
				esc_py_blox.append( block )

			for block in orig_blox: 
				text=text.replace( block, '<div class="escpy">{{ esc-py-block }}</div>')


		#
		#	PROCESS PYTHON CODE ----------------------------------------------------
		# 
		python_tag = '```Python'
		if python_tag in text:

			# process markdown
			text = pymarkdown.process( text )

			# get everything wrapped in Python marker
			code_blox = re.findall ( '```Python(.*?)```', text, re.DOTALL)
			
			# initialize lists to store original & pygmentized code  
			orig_blox = []
			py_blox = []

			# loop through all python code blocks
			for block in code_blox:

				# recreate original
				orig = '```Python%s```' % block
				orig_blox.append( orig )

				# pygmentize and wrap
				pyg = highlight(block, PythonLexer(), HtmlFormatter())
				py_blox.append( pyg )
				#pyg = '<div class="py-block">%s</div>' % pyg
				#pyg_blox.append( pyg )

			# replace original blox with pygmentized version
			for orig in orig_blox: 

				text=text.replace( orig, '<div class="py-block">{{ py-block }}</div>' )


		#
		#	PROCESS R CODE ----------------------------------------------------
		# 
		r_tag = '```{r'

		if r_tag in text:

			# process R code, which relies on Knitr
			text = Parse().parseRBlocks( site, text )
			text = Parse().removeKnitrHashes( text )

			# get everything wrapped as input-output R code
			code_blox = re.findall ( r'(?<=[\n```r\n])(.*?)\n```\n\n```\n(.*?)\n```\n', text, re.DOTALL)

			r_input_blox = []
			r_output_blox = []
			r_io_str_blox = []

			# ok, so above regex matches on second to last (i think?) ```r before 
			# the sequence we want ... couldn't figure out how to tweak it, so 
			# what we do is take the first element of the first list returned, then
			# split it on the *last* instance of the string, which always be the one
			# we want ... then we could do our crazy thing with the strings and the divs
			# god i hate myself right now
			for blk in code_blox:

				i=0
				for it in blk:
					if i % 2 == 0:
						blerg = it.rsplit( '\n```r\n', 1 )
						r_input = blerg[1] 
					else: 
						r_output = it
					i=i+1

				r_input_blox.append( r_input )
				r_output_blox.append( r_output )
				r_orig_str = '\n```r\n%s\n```\n\n```\n%s\n```\n' % (r_input, r_output )

				text = text.replace( r_orig_str, '\n\n{{ r-i/o-block }}\n\n')
				r_io_str = '<div class="rwrap"><div class="txtr"><p>In [i]:</p></div><div class="outputr">'
				pyg_r_input = highlight(r_input, SLexer(), HtmlFormatter())

				r_io_str = '%s%s' % (r_io_str, pyg_r_input )
				r_io_str = '%s</div><!-- end outputr></div><!-- end rwrap -->' % r_io_str
				r_io_str = '%s<div class="rwrap"><div class="txtr2"><p>Out [i]:</p></div><div class="outputr2">' % r_io_str
				pyg_r_output = highlight(r_output, SLexer(), HtmlFormatter())
				r_io_str = '%s%s</div></div><!-- end rwrap -->\n' % (r_io_str, pyg_r_output)
				r_io_str_blox.append( r_io_str )


			# get everything wrapped as input R code
			code_blox = re.findall ( r'```r(.*?)```', text, re.DOTALL)

			r_blox = []
			for block in code_blox:

				# recreate original string, for use in .replace()		
				match_str = '```r%s```' % block

				if match_str in text: 
					print 'applause!'

				# p tags and trailing line breaks are important ... markdown won't always 
				# parse subsequent text correctly w/o them
				text = text.replace( match_str, '\n\n<p>{{ r-block }}</p>\n\n' )

				# pygmentize block & wrap 
				r_input = highlight(block, SLexer(), HtmlFormatter())
				r_input = '<div class="rwrap"><div class="txtr"><p>In [i]:</p></div><div class="outputr">%s' % r_input 
				r_input = '%s</div></div><!-- end rwrap -->' % r_input
				r_blox.append( r_input )


		# PROCESS NON-R and NON_PYTHON CODE -------------------------------------
		
		if '```' in text:
			code_blox = re.findall ( '```(.*?)```', text, re.DOTALL)
			orig_blox = []
			mod_blox = []
			replacement_code_blocks = []

			for block in code_blox:		
				orig = '```%s```' % block
				orig_blox.append( orig )

				block = '<pre>%s</pre>' % block
				replacement_code_blocks.append( block )

				block = '<div class="codeblock">{{ code-block }}</div>'
				mod_blox.append( block )

			# insert placeholder text while we process markdown 
			for orig, mod in zip(orig_blox, mod_blox):
				text = text.replace( orig, mod )




		# PROCESS MARKDOWN !! ----------------------------------------------------

		text = markdown2.markdown( text )


		# clean up images that markdown missed b/c R

		if '{{ r-block }}' in text or '{{ r-i/o-block }}' in text:

			r_pix_blox = re.findall( r'{{ r-block }}</p>\n\n<p><img src="(.*?)" alt="(.*?)" /> </p>', text, re.DOTALL )

			for img_blox in r_pix_blox: 
				
				img_title = img_blox[0]
				img_src = img_blox[1]
				match_str = '{{ r-block }}</p>\n\n<p><img src="%s" alt="%s" /> </p>' % (img_title, img_src)
				repl_str = '{{ r-block }}</p>\n\n<img src="%s" alt="%s" style="width:360px;" />' % (img_title, img_src)

				# <div class="rwrap"><div class="txtr"></div><div class="outputr"></div></div><!-- end rwrap -->
				text = text.replace( match_str, repl_str )



		# REINSERT ANY CODE WE ESCAPED ---------------------------------------

		# ---- r code blocks ----
		try: 
			for block in r_io_str_blox: 
				text = text.replace( '{{ r-i/o-block }}', block, 1)
			text = Parse().reformatRPost( text )

		except:
			pass

		# ---- r code blocks ----
		try: 
			for block in r_blox: 
				text = text.replace( '{{ r-block }}', block, 1)
			text = Parse().reformatRPost( text )

		except:
			pass


		# ---- py code blocks ----
		try: 
			for block in py_blox: 
				text = text.replace( '{{ py-block }}', block, 1)
			text = Parse().reformatRPost( text )

		except:
			pass

		# ---- non-r code blocks ----
		try:
			for block in replacement_code_blocks: 
				text = text.replace( '{{ code-block }}', block, 1)
		except:
			pass

		# ---- example python code blocks ----
		try:
			for block in esc_py_blox: 
				text = text.replace( "{{ esc-py-block }}", block, 1 )
		except: 
			pass


		# if there was input/output code, number it
		if 'In [i]' in text: 
			num = text.count( 'In [i]' )+1
			i = 1
			while i < num: 

				s1 = text.find( 'In [i]' )
				s2 = text.find( 'Out [i]' )
				beg = s1+1
				s3 = text.find( 'In [i]', beg )

				InTxt = 'In [%d]' % i
				OutTxt = 'Out [%d]' % i

				text = text.replace( "In [i]", InTxt, 1)

				if s2 > -1 and s3 > -1: 
					if s2 < s3:
						text = text.replace( "Out [i]", OutTxt, 1)
				if s2 > -1 and s3 == -1: 
					text = text.replace( "Out [i]", OutTxt, 1)
				i=i+1


		# finally, fix markdown bug ... i don't understand what's happening to 
		# the leading <p> here ... markdown enclosed {{ r-block }} in p tags, but 
		# sometimes only the trailing one remains after pygments does its thing?
		text = text.replace( '<div class="outputr">\n</p>', '<div class="outputr">\n' )

		# RETURN AT LONG LAST! ---------------------------------------------------	
		return text

class Post(object):

	def __init__( self, file_source_path, category, site ):

		handler = FileHandler() # handles raw .md file
		parser = Parse() # parses python & r

		self.raw_file = handler.SplitRawFile( file_source_path )

		self.is_page = Util().set_page_status( file_source_path )

		self.title = handler.get_title( self.raw_file.meta_data, file_source_path )

		self.title_encoded = urllib.quote_plus( self.title )

		self.slug = handler.get_slug( self.raw_file.meta_data, self.title )

		self.content = parser.highlighter( site, self.raw_file.content )

		#self.content = markdown2.markdown( self.content )

		self.content = self.content.replace( ' -- ', ' &mdash; ')

		self.date = handler.DateObject( self.raw_file, file_source_path )

		self.date_text = self.date.text # for template parsing

		self.url = handler.get_url( self, site, category )

		self.url_encoded = urllib.quote_plus( "%s%s" % (site.url, self.url ) )

class Snippet(object):

	def __init__( self, site ):

		# get a list of all items in root path
		self.files = os.listdir( site.snippet_path )

		self.dict = {}

		for file in self.files:

			if file[0] == '.' or file[0] == '_':
				continue	

			with open( os.path.join( site.snippet_path, file ), 'rb' ) as f:
				raw_file = f.read()

			file_split = file.split( "." )
			file_name = file_split[0]

			self.dict[file_name] = raw_file
