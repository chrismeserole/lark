This sets up a basic blog. Create a virtualenv first that has markdown2 installed:

	cd ~
	virtualenv mezpress/ENV
	source mezpress/ENV/bin/activate
	pip install markdown2


In terminal, go to the directory you want to set up the blog in. 

Either the root directory or a subdirectory should include a `_posts' subdirectory. 

The root directory should also include a '_layouts' subdirectory and also a config.py and mezpress.py file. 

Run: 

	python mezpress.py

That will cycle through all _posts subdirectories and produce a root/_site subdirectory containing the static site. 

To view the output locally, run: 

	cd _site; python -m SimpleHTTPServer; cd ..

Then got to 'localhost:8000' in a browser.

### DEFAULT SETTINGS

DEFAULT_INDEX. Set this to '' if you want to create a blog at the root of your site. Otherwise specify the relevant category/subdirectory that you want to appear at the root. 

ROOT_PATH. If this is not set, it defaults to the current directory in terminal. 

PERMALINK_STYLE. Either 'date', which defaults to root/[category/]Year/Month/Day/slug. Or 'no-date', which defaults to root/slug.

### _POSTS CONFIG.MD FILE
Each category/subdirectory with a _posts subdirectory can also have a '_config.md' file. 

You can use this to set DESCRIPTION and PERMALINK_STYLE for each individual category.

### PAGES

Mezpress also allows for pages. All markdown files in '../root/pages/_posts/' will produce pages at root.

