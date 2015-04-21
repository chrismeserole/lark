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

			try: 
				site.banner_text = category.config.banner_title.upper()
			except: 
				site.banner_text = '%s &mdash; %s' % ( site.name.replace(' ', ''), category.name.upper() )
		
			site.banner_url = '/%s/' % ( category.name )

		site.category_name = category.name
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

		if self.name != 'root':
			try: 
				with open( os.path.join( self.category_path, '_config.yaml' ), 'rb') as f:
					config_file = f.read()

				config_dict = yaml.load( config_file )
				config_dict = dict((k.lower(), v) for k,v in config_dict.iteritems())
				self.config = Struct( **config_dict )

			except:
				print "Note: no config file for %s." % self.name.upper()

		self.posts_list = []
		self.pages_list = []

		if self.name == 'root':
			self.posts_source_path = os.path.join( site.root_path, '_posts' )
			self.pages_source_path = os.path.join( site.root_path, '_pages' )
			self.output_directory = site.output_path

			if os.path.isdir( self.posts_source_path ):
				self.posts_list = os.listdir( self.posts_source_path )
				self.posts_list = ['*POST*{0}'.format(i) for i in self.posts_list]
			if os.path.isdir( self.pages_source_path ):
				print self.pages_source_path
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
				print self.pages_source_path
				self.pages_list = os.listdir( self.pages_source_path ) 
				self.pages_list = ['*PAGE*{0}'.format(i) for i in self.pages_list]

		self.content_list = self.posts_list + self.pages_list
		print self.content_list

		try:
			with open( os.path.join( category.config.layout_path, 'index.html' ), 'rb' ) as f:
				html_template = f.read()
		except:
			with open( os.path.join( site.layout_path, 'index.html' ), 'rb' ) as f:
				html_template = f.read()

		try:
			self.snippet_path = self.config.snippet_path
			cat_snippets = Snippet( self )
			html_template = Parse().replace_tags( 'snippet', cat_snippets.dict, html_template )
			print cat_snippets
			sys.exit()
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
			post_slug = re.search('slug:(.*)\\n', raw_meta_data_text.lower() ).group(1)
		
		except:
			post_slug = util.create_slug_from_title( title )

		return post_slug


	def get_url( self, post, site, category ):

		permalink_style = Util().get_permalink_style( category, site )

		print permalink_style

		if category.name == 'root' and post.is_page is True:
			post_url = '/%s/' % post.slug

		else:
			if category.name == 'root' and permalink_style.lower() == 'date':
				post_url = '/%s/%s/%s/%s/' % ( post.date.year, post.date.month, post.date.day, post.slug )
			elif category.name == 'root' and permalink_style.lower() == 'no-date':
				post_url = '/%s/' % ( post.slug )

			elif permalink_style.lower() == 'date':
				post_url = '/%s/%s/%s/%s/%s/' % ( category.name, post.date.year, post.date.month, post.date.day, post.slug )
			elif permalink_style.lower() == 'no-date':
				post_url = '/%s/%s/' % ( category.name, post.slug )
							
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
								stdout=subprocess.PIPE).stdout.read()

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

			print full_file_name
			print outputfile
			
			shutil.copy(full_file_name, outputfile)



		old = "(figure/"
		new = "(/%s/" % site.images_path


		text = text.replace(old, new)
		
		#shutil.rmtree( 'figure' )

		# return the new markdown file! 
		return text


	def highlighter( self, site, text ):

		r_tag = '```{r'

		if r_tag in text:

			text = Parse().parseRBlocks( site, text )


		# pymarkdown processes all '```Python' strings, so we need to escape 
		# the ones we want to appear in html
		# USING .SPLIT() IS A TOTAL HACK

		text_list = text.split('\t```Python')
		
		orig_blocks = []
		replacement_blocks = []

		if len(text_list) > 0: 
			del text_list[0]

			for block in text_list:
				
				block_list = block.split('\t```')

				orig_block = '\t```Python%s\t```' % block_list[0]
				orig_blocks.append( orig_block )

				replacement_block = '\t```Python%s\t```' % block_list[0]
				
				#print escaped_block
				replacement_blocks.append( replacement_block )

		# insert placeholder text while we process the 
		for orig_block in orig_blocks:
			text = text.replace( orig_block, '{{ escaped }}')

		# now that everything's escaped ... 

		# 1. process python code
		text = pymarkdown.process( text )

		# 2. highlight python code
		old_python_blocks = re.findall ( '```Python(.*?)```', text, re.DOTALL)
		new_python_blocks = []

		for block in old_python_blocks:
			block = highlight(block, PythonLexer(), HtmlFormatter())
			new_python_blocks.append( block )

		for old_block, new_block in zip(old_python_blocks, new_python_blocks):
			text = text.replace( old_block, new_block )

		# 3. highlight R code
		old_r_blocks = re.findall ( '```r(.*?)```', text, re.DOTALL)


		new_r_blocks = []

		for block in old_r_blocks:
			block = highlight(block, SLexer(), HtmlFormatter())
			new_r_blocks.append( block )

		for old_block, new_block in zip(old_r_blocks, new_r_blocks):
			text = text.replace( old_block, new_block )



		# now add back in the escaped blocks
		for replacement_block in replacement_blocks: 
			text = text.replace( '{{ escaped }}', replacement_block, 1)


		#----------------------------------------------------------------------
		# delete the ```Python strings for the blocks we actually ran, so they 
		# won't appear in HTML
		#----------------------------------------------------------------------
		old_all_blocks = re.findall ( '\n```(.*?)\n```', text, re.DOTALL)

		old_blocks = []
		new_blocks = []

		for block in old_all_blocks:
			old_block = block
			if block[:6] == 'Python' or block[:1] == 'r':
				new_block = block
			else:
				new_block = '<pre>%s</pre>' % block

			old_blocks.append( old_block )
			new_blocks.append( new_block ) 

		for old_block, new_block in zip(old_blocks, new_blocks):
			text = text.replace( old_block, new_block )

		text = text.replace( u'\n```Python', "" )
		text = text.replace( u'\n```r', "")
		text = text.replace( u'\n```', "")


		#----------------------------------------------------------------------
		# preserve any indented code blocks that you actually want to show 
		#----------------------------------------------------------------------
		
		old_all_blocks = re.findall ( '\t```(.*?)\t```', text, re.DOTALL)

		old_blocks = []
		new_blocks = []

		for block in old_all_blocks:
			old_block = block
			new_block = '<pre>```%s```</pre>' % block
			old_blocks.append( old_block )
			new_blocks.append( new_block ) 

		for old_block, new_block in zip(old_blocks, new_blocks):
			text = text.replace( old_block, new_block )

		text = text.replace( u'\t```', "")


		#----------------------------------------------------------------------


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

		self.content = markdown2.markdown( self.content )

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


