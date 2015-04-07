import os
import sys
import re
import shutil
import datetime, time
from xml.sax.saxutils import escape #for rss feed
from shutil import copytree, ignore_patterns
from larklib import Util, FileHandler, Category, Post, Site, Parse


#
# get site variables (site.name, site.author, etc)
# 
site = Site().config_vars

# 
#	get Utility object
#
util = Util()

#
#	CHECK FOR config.py && _layouts/
#
util.confirm_layouts( site.layout_path )

#
#	ENSURE site.output_path EXISTS & IS EMPTY
#
util.prepare_output_dir( site.output_path )


#
#	1. GET LOCATION OF ALL DIRECTORIES IN site.root_path THAT HAVE _POSTS SUBDIRECTORY
#	2. COPY ALL OTHER UNEXCEPTED DIRS AND FILES TO site.output_path
#	3. CONFIRM THAT THERE IS AT LEAST ONE _POSTS SUBDIRECTORY
#

# initialize list of all categories/subdirs
categories = []

# check if there is a _POSTS or _PAGES file in rootpath, add to '' category list
if os.path.isdir( os.path.join( site.root_path, '_posts' ) ):
	categories.append( 'root_posts' )

# check if there is a _POSTS or _PAGES file in rootpath, add to '' category list
if os.path.isdir( os.path.join( site.root_path, '_pages' ) ):
	categories.append( 'root_pages' )


# get a list of all items in root path
root_items = os.listdir( site.root_path )

# loop through every item name in root path
for item in root_items:

	# skip files with excepted prefixes (e.g., '_', '.')
	if item[0] in site.excepted_prefixes:
		continue

	# skip files with excepted suffixes (e.g., '.py')
	if item.endswith( tuple(site.excepted_suffixes) ):
		continue

	# set item source path
	item_source_path = os.path.join( site.root_path, item )

	#
	#	Check if item is a directory
	#
	if os.path.isdir( item_source_path ):

		# 
		#	If item is a directory with a _posts subdirectory, then add to 
		#	'category' list but don't copy anything.
		#
		if os.path.exists( os.path.join( item_source_path, '_posts' ) ):
			categories.append( item )

		#
		#	If _posts directory doesnt exist, then copy all contents
		#	recursively into site.output_path.
		#
		else:
			item_layout_path = os.path.join( site.output_path, item )
			if item_source_path.endswith( '/img' ):
				shutil.copytree( item_source_path, item_layout_path, ignore=ignore_patterns( '*.pxm' ) )
			else:
				shutil.copytree( item_source_path, item_layout_path )

	#
	#	Copy all unexcepted files in site.root_path to site.output_path
	#
	elif os.path.isfile( item_source_path ):
		shutil.copy2( item_source_path, os.path.join( site.output_path, item ) )


#
# confirm that there is at least one _posts directory
#
util.confirm_posts( categories )


#
#	PREPARE HTML TEMPLATE. (Retrieves templates & parses snippets.)
#
html_template = util.prep_html_template( site )


#
#
#	LOOP THROUGH EACH CATEGORY (IE, EACH _POSTS SUBDIRECTORY)
#
#

for category_name in categories: 

	# get category object
	category = Category( category_name, site )

	# print category
	print '\n%s' % category.name.upper()

	# initialize variable to store all posts within category in memory
	posts_heap = []

	# loop through each item in /root/category/_posts
	for file_name in category.posts_list:

		# set file_name path, namely: /root/category/_posts/entry
		file_source_path = os.path.join( category.posts_source_path, file_name )

		# verify file_name is a file rather than subdirectory
		if not os.path.isfile( file_source_path ):
			continue 

		# verify file_name has approved file extension
		if not file_name.endswith( '.md' ) and not file_name.endswith( '.markdown' ):
			continue 

		#
		#	CREATE AND WRITE POSTS
		#

		# create post object that returns post.title, post.content, etc
		post = Post( file_source_path, category, site )

		# add site.title_tag, site.banner_url, site.banner_text
		site = Site().set_header_vars( site, post.title, category, index=False  )

		# replace all site tags, e.g. {{ site.url }}
		post_template = Parse().replace_tags( 'site', site, html_template )

		# replace all post tags, e.g. {{ post.title }}
		post_template = Parse().replace_tags( 'post', post, post_template )

		# since this is single post, just delete both content & single entry tags
		post_template = post_template.replace( '{{ content_loop }}', '' )
		post_template = post_template.replace( '{{ single_entry_only }}', '' )

		# for pages, ignore all content between {{ entry_only }} tags
		if category.name == 'root_pages':
			post_template = post_template.split( '{{ entry_only }}' )
			post_template = "%s%s" % ( post_template[0], post_template[2] )
			
		else:
			post_template = post_template.replace( '{{ entry_only }}', '' )

		# replace snippets
		post_template = Parse().replace_tags( 'snippet', site, post_template )

		# write the post_template to file 
		util.write_entry( post_template, category, post, site  )

		# append post itself to heap, for reuse in category & rss files
		posts_heap.append( post )
		


	#
	#	End the pass through the for loop if the current category is "pages"
	#
	if category.name == 'root_pages':
		continue

	#
	#	Sort posts by timestamp
	#
	posts_heap = sorted( posts_heap, key=lambda post: post.date.timestamp, reverse=True )

	#
	#	GENERATE CATEGORY INDEX
	#

	#
	#	Regenerate site.title_tag, site.banner_url, site.banner_link
	#
	# add site.title_tag, site.banner_url, site.banner_text
	site = Site().set_header_vars( site, '', category, index=True  )

	# replace all site tags, e.g. {{ site.url }}
	post_template = Parse().replace_tags( 'site', site, html_template )

	# split category template on content_loop tags
	category_template = post_template.split( "{{ content_loop }}" )

	content_html = category_template[1]
	footer_html = category_template[2]

	category_template = category_template[0]

	count = 0

	for post in posts_heap:

		## for category page, we want everything between {{ entry_only }} tages 
		post_entry_html = content_html.replace( '{{ entry_only }}', '' )

		## break before single_entry_only, since this is index
		post_entry_html = post_entry_html.split( "{{ single_entry_only }}")

		# replace all post tags, e.g. {{ post.title }}
		post_entry_html = Parse().replace_tags( 'post', post, post_entry_html[0] )

		## add latest post to the index file we're building
		category_template += post_entry_html 

		count += 1 

		if count == site.max_index_entries:
			break

	## add footer html to index file
	category_template += footer_html

	## write index file
	util.write_category_index( category.output_directory, category_template )



	#
	#	GENERATE RSS FEED FOR CATEGORY
	#

	with open( os.path.join( site.layout_path, 'feed.xml' ), 'rb' ) as f:
		rss_template = f.read()

	# replace all post tags, e.g. {{ site.name }}
	rss_template = Parse().replace_tags( 'site', site, rss_template )

	# if we're in root, replace accordingly
	if category.name == 'root_posts':
		feed_url = "%s/feed.xml" % site.url
		print feed_url
		rss_template = rss_template.replace( '{{ feed.url }}', feed_url )
		rss_template = rss_template.replace( '{{ category }}', '' )
		rss_template = rss_template.replace( '{{ category.description }}', site.description )

	# if we're in subdirectory, replace with category tags
	else: 
		feed_url = "%s/%s/feed.xml" % ( site.url, category.name ) 

		rss_template = rss_template.replace( '{{ feed.url }}', feed_url )
		rss_template = rss_template.replace( '{{ category }}', category.name )
		rss_template = rss_template.replace( '{{ category.description }}', category.description )


	# split at content loop
	rss_template = rss_template.split( "{{ content_loop }}" )

	rss_content = rss_template[1]
	rss_footer = rss_template[2]
	
	rss_template = rss_template[0]

	count = 0

	for post in posts_heap: 

		# set date format for rss 
		post.date = datetime.datetime.strftime( post.date.published_datetime, "%a, %d %b %Y %H:%M:%S EST" )

		# reformat post.content so html chars are escaped
		post.content = escape( post.content )

		# replace all post tags, e.g. {{ post.title }} with post.title
		post.content = Parse().rss_image_paths( site, post.content )

		# replace all post tags, e.g. {{ post.title }} with post.title
		rss_entry_template = Parse().replace_tags( 'post', post, rss_content )

		# append rss_entry_template to full rss_template
		rss_template += rss_entry_template

		count += 1

		if count == site.max_index_entries:
			break

	# append rss footer back to rss_template
	rss_template += rss_footer

	# write rss_template to file
	util.write_category_feed ( category.output_directory, rss_template )


#
#	One last thing: move config.DEFAULT_INDEX to site.output_path and replace with redirect
#	ex: move /root/_site/default/index.html to root/_site/index.html
#

if site.default_index == '':
	default_directory_path = site.output_path
else:
	default_directory_path = os.path.join( site.output_path, site.default_index )

default_path_index_src = os.path.join( default_directory_path, 'index.html' )
default_path_index_dst = os.path.join( site.output_path, 'index.html' )

if not default_path_index_src == default_path_index_dst:
	shutil.copyfile( default_path_index_src, default_path_index_dst )


# check for css
util.confirm_css( os.path.join( site.root_path, 'css' ) )

print '\nFinishined parsing \"%s\" \n' % site.name
# there was a problem with infinite redirect on s3, though not local. not sure what going on
#redirect_html = '<!DOCTYPE html><html><head><meta http-equiv="content-type" content="text/html; charset=utf-8" /><meta http-equiv="refresh" content="0;url=/{{ path }}" /></head></html>'

#default_redirect_html = redirect_html.replace( '{{ path }}', '' )
#default_directory_redirect_path = os.path.join( default_directory_path, 'index.html' )

#with open( default_directory_redirect_path, 'w' ) as f:
#	f.write( default_redirect_html )
