### Installing Lark 

To get Lark up and running, first make sure you've got the modules below installed. (You may want to use a virtualenv.) 

	pip install markdown2 yaml xml

Then run the following: 

	mkdir ~/lark
	cd ~/lark
	git clone https://github.com/chrismeserole/lark.git
	python lark.py
	cd _site; python -m SimpleHTTPServer; cd ..

If you open localhost:8000 in your browser, you should now see a skeleton site. 

In the future I may release Lark as a python module, but for now this works fine.

### How Lark Works 

Lark works by scanning the root directory *and all subdirectories* for a _posts folder. 

If you want to host a simple blog at the root of your Lark directory, like Jekyll or most other static site generators, the structure of Lark allows you to do that easily. 

However, by scanning all subdirectorys for a _posts folder, Lark also lets you host multiple blogs off the same install. (These are termed 'categories' in the Lark code.)

### Lark's Structure

A simple install of lark will look like the following: 

	lark/
		_drafts
		_posts
		_pages
		_layouts
		_snippets
		_site
		_config.yaml
		lark.py
		larklib.py
		readme.md

The **_drafts** folder is for files you are not yet ready to publish. Lark does not parse them.

The **_posts** folder is for files to be published. Lark parses any file there with an `.md` or `.markdown` file type.

The **_pages** folder is for any files you want to publish off the root. The URL slug will be the same as the title, and will not include a date. The files should be of a `.md` or `.markdown` file type. 

The **_layouts** folder contains a single html template that is parsed. (Note: in the future Lark may allow for multiple templates.)

The **_snippets** folder contains any html, js or text snippets you would like to use in your templates. If there is a file named `twitter_script.js` in the _snippets folder, then if you put `{{ snippet.twitter_script }}` in the template layout, it will be parsed. Note that the file name and snippet parse tag must match exactly. 

The **_site** folder is where Lark publishes the static site you can then upload. 

The **_config.yaml** file is where you set basic defaults. Within your html template, any value in **_config.yaml** can be included. For example, the `NAME` field in _config.yaml can be parsed into your template as `{{ site.name }}`. 

The lark.py file iteratively builds the site, and calls on several classes in larklib.py to do so. 


### Default Settings

PERMALINK_STYLE. The first option is 'date', which defaults to a permalink structure of root/[category/]Year/Month/Day/slug, with the slug being compiled from the title. The second option is 'no-date', which defaults to root/[category/]slug.

[TODO: fill out more of the defaults.]


### Deploying to S3

If you've got s3cmd installed, you can deploy using the following: 

	s3cmd sync _site/ s3://[YOUR-BUCKET]/ --delete-removed


