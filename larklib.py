import re
import os
import sys
import markdown2
import datetime, time
import shutil
import yaml
import urllib



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

		if category.name == 'root_pages':
			site.title_tag = '%s > %s' % ( post_title, site.name )
			site.banner_text = site.name.replace(' ', '')
			site.banner_url = '/'

		elif category.name == 'root_posts': 
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

			site.banner_text = '%s &mdash; %s' % ( site.name.replace(' ', ''), category.name.upper() )
			site.banner_url = '/%s/' % ( category.name )

		site.title_tag_encoded = urllib.quote_plus( site.title_tag )

		return site


class Util(object):


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

	def prep_html_template( self, site ):

		snippets = Snippet( site )

		with open( os.path.join( site.layout_path, 'index.html' ), 'rb' ) as f:
			html_template = f.read()

		# replace snippets
		html_template = Parse().replace_tags( 'snippet', snippets.dict, html_template )

		return html_template


	def write_entry( self, my_html, category, post, site ):

		util = Util()
		if category.permalink_style.lower() == "no-date" or category.name == "root_pages":
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


	def write_category_index( self, published_category_directory_path, index_html ):

		published_category_directory_index = os.path.join( published_category_directory_path, 'index.html' )

		with open( published_category_directory_index, 'w' ) as f:
			index_html = index_html.encode("utf-8") # was running into error w/o this with some chars
			f.write( index_html )
			print 'Published %s' % published_category_directory_index


	def write_category_feed( self, published_category_directory_path, rss_feed_xml ):

		published_category_directory_feed = os.path.join( published_category_directory_path, 'feed.xml' )

		with open( published_category_directory_feed, 'w' ) as f:
			rss_feed_xml = rss_feed_xml.encode("utf-8")
			f.write( rss_feed_xml )
			print 'Published %s' % published_category_directory_feed


	def create_redirect( self, old_published_path, new_published_path ):
		old_published_path = ensure_directory( old_published_path )
		old_published_path_index = os.path.join( old_published_path, 'index.html' )

		redirect_html = '<!DOCTYPE html><html><head><meta http-equiv="content-type" content="text/html; charset=utf-8" /><meta http-equiv="refresh" content="0;url=%s" /></head></html>' % new_published_path

		with open( old_published_path_index, 'w' ) as f:
			f.write( redirect_html )


	def confirm_posts( self, cat_list ):
		if not cat_list: 
		 	raise RuntimeError( "ERROR: no _posts directory in root path or subdirectories" )


	def confirm_layouts( self, layout_path ):
		if not os.path.isdir( layout_path ):
		 	raise RuntimeError( "ERROR: no _layouts directory in root path" )


	def confirm_css( self, css_path ):
		if not os.path.isdir( css_path ):
		 	print "\n**\nWARNING: NO CSS DIRECTORY \n**\n"


	# TO-DO: make smart, page-by-page overwriting?
	def prepare_output_dir( self, site_path ):
		if os.path.exists( site_path ):
			shutil.rmtree( site_path )
		os.makedirs( site_path )


class Category(object):


    def __init__( self, category_name, site ):

    	util = Util()

    	# set category name
    	self.name = category_name

    	# set default category style & description to site style & description
    	self.permalink_style = site.permalink_style
    	self.description = site.description

    	# set paths for files in /root/_posts directory
    	if self.name == 'root_posts':
    		self.posts_source_path = os.path.join( site.root_path, '_posts' )
    		self.output_directory = site.output_path

    	# set paths for files in /root/pages directory
    	elif self.name == 'root_pages':
    		self.posts_source_path = os.path.join( site.root_path, '_pages' )
    		self.output_directory = site.output_path

    	else:
    		self.input_path = os.path.join( site.root_path, category_name)
    		self.posts_source_path = os.path.join( self.input_path, '_posts')
    		self.output_directory = util.ensure_directory( os.path.join( site.output_path, self.name ) )
    		self.config_source_path = os.path.join( self.input_path, '_config.md' )


    	# if there is a category config file, import it
    	# todo: use .yaml for this
    	try:
    		with open( self.config_source_path, 'rb' ) as f:
    			self.config_file = f.read()
    			config_split = str.split( self.config_file, '\n' )

    			for line in config_split:

    				split_line = str.split(line, ":", 1)

    				if split_line[0].lower().strip() == 'permalinks':
    					self.permalink_style = split_line[1].lower().strip()

    				if split_line[0].lower().strip() == 'description':
    					self.description = split_line[1].strip()

    	except:
    		pass

    	self.posts_list = os.listdir( self.posts_source_path ) 



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


	def get_url( self, year, month, day, slug, category, category_permalink_style ):

		if category == 'root_pages':
			post_url = '/%s/' % slug

		else:
			if category == 'root_posts' and category_permalink_style.lower() == 'date':
				post_url = '/%s/%s/%s/%s/' % ( year, month, day, slug )
			elif category == 'root_posts' and category_permalink_style.lower() == 'no-date':
				post_url = '/%s/' % ( slug )

			elif category_permalink_style.lower() == 'date':
				post_url = '/%s/%s/%s/%s/%s/' % ( category, year, month, day, slug )
			elif category_permalink_style.lower() == 'no-date':
				post_url = '/%s/%s/' % ( category, slug )
							
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



class Post(object):
    """A simple example class"""

    def __init__( self, file_source_path, category, site ):

    	handler = FileHandler()

    	self.raw_file = handler.SplitRawFile( file_source_path )

        self.title = handler.get_title( self.raw_file.meta_data, file_source_path )

        self.title_encoded = urllib.quote_plus( self.title )

        self.slug = handler.get_slug( self.raw_file.meta_data, self.title )

        self.content = markdown2.markdown( self.raw_file.content )

        self.content = self.content.replace( ' -- ', ' &mdash; ')

        self.date = handler.DateObject( self.raw_file, file_source_path )

        self.date_text = self.date.text # for template parsing

        self.url = handler.get_url( self.date.year, self.date.month, self.date.day, self.slug, category.name, category.permalink_style )

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


