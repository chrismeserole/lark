
### Another Static Site Engine, Really?

I know, right?

### \*Rolls Eyes\*

OK, so basically Lark came about for three reasons: 

1. **Custom subdirectory structure.** Lark recursively searches through all subdirectories, and builds a blog anywhere it finds a `_posts` subdirectory. This used to be possible, sort-of, using a hack on Jekyll. But the hack broke with an upgrade to Yosemite last fall,  I couldn't get it working again. I also couldn't replicate it via Pelican, Hugo, etc. Ultimately it seemed less time consuming to roll my own. 

2. **Data writing.** I'm building Lark, long-term, to make data analysis and presentation as seemless as possible. At present, Lark can execute python code blocks embedded in posts, and output the result in the resulting html. It's similar to python notebook, except static. There's a lot more I want to do on that front though, and writing your own publishing environment, where you know and can manipulate the entire underlying architecture, will make it a lot easier to realize whatever cool stuff I can dream up.  

3. **Dissertation procrastination.** Why else do something? 


### Enough Already How Do You Install 

To get Lark up and running, first make sure you've got the packages below installed. (You may want to use a virtualenv.) 

	pip install markdown2 pyyaml pymarkdown

Then run the following: 

	git clone https://github.com/chrismeserole/lark.git; cd lark
	python lark.py
	python preview.py

If you open localhost:8000 in your browser, you should now see a skeleton site. 

In the future I may release Lark as a python package, but for now this works fine.

### How Lark Works 

Lark works by scanning the root directory *and all subdirectories* for a _posts folder. 

If you want to host a simple blog at the root of your Lark directory, like Jekyll or most other static site generators, the structure of Lark allows you to do that easily. 

However, by scanning all subdirectories for a _posts folder, Lark also lets you host multiple blogs off the same install. (These are termed 'categories' in the Lark code.)

### Lark's Structure

A simple install of lark will look like the following: 

	lark/
		_drafts/
		_posts/
		_pages/
		_layouts/
		_snippets/
		_site/
		_config.yaml
		css/
		img/
		deploy.py
		lark.py
		larklib.py
		preview.py
		readme.md

The **_drafts/** folder is for files you are not yet ready to publish. Lark does not parse them.

The **_posts/** folder is for files to be published. Lark parses any file there with an `.md` or `.markdown` file type.

The **_pages/** folder is for any files you want to publish off the root. The URL slug will be the same as the title, and will not include a date. The files should be of a `.md` or `.markdown` file type. 

The **_layouts/** folder contains a single html template that is parsed. (Note: in the future Lark may allow for multiple templates.)

The **_snippets/** folder contains any html, js or text snippets you would like to use in your templates. If there is a file named `twitter_script.js` in the _snippets folder, then if you put `{{ snippet.twitter_script }}` in the template layout, it will be parsed. Note that the file name and snippet parse tag must match exactly. 

The **_site/** folder is where Lark publishes the static site you can then upload. 

The **css/** folder is not required, but may be used to store all `.css` files.

The **img/** folder is also not required, but may be used to store all image files. 

The **_config.yaml** file is where you set basic defaults. Within your html template, any value in _config.yaml can be included. For example, the `NAME` field in _config.yaml can be parsed into your template as `{{ site.name }}`. 

The **lark.py** file iteratively builds the site, and calls on several classes in larklib.py to do so. 

The **deploy.py** file calls on the Site class in larklib.py, and deploys to S3. s3cmd must already be installed.

The **preview.py** file calls on the Site class in larklib.py, and previews the files in the directory specified by OUTPATH_PATH in _config.yaml. Viewable in a browser at http://localhost:8000/. (To kill the preview in Terminal, hit Ctrl-C.)

### Excepted Files

With the exception of the folders listed above, Lark does not open, copy or parse any file or subdirectory beginning with `.` or `_` or ending with `.py`, `.pyc`, `.yml` or `.yaml`. The excepted file types can be changed in _config.yaml. 

All other files are copied recursively, with the same directory structure, into the _site/ folder at runtime. 


### Default Settings

PERMALINK_STYLE. The first option is 'date', which corresponds to a permalink structure of `root/[subdirectory/]Year/Month/Day/slug`, with the slug being compiled from the title. The second option is 'no-date', which corresponds to `root/[subdirectory/]slug`.

[TODO: fill out more of the defaults.]


### RSS Images

Lark attempts to use resized images in RSS feeds, so that RSS-to-email packages will not send email with image sizes that far exceed the window of most phone and desktop email clients. 

At present it works primarly by a hack. If a post contains *either* of the following: 

	<img src="http://example.com/img/myimage_1920.jpg 1920" />
	<img src="http://example.com/img/myimage_1920.jpg" />

It will be corrected to:

	<img src="http://example.com/img/myimage_480.jpg" />

Note that to make this work, all original images must have "_1920.jpg" appended as a suffix, and there must also be an identifically named file with "_480.jpg" appended.  


### Deploying to S3

If you've got s3cmd installed, you can either deploy using the following: 

	s3cmd sync _site/ s3://[YOUR-BUCKET]/ --delete-removed

Alternately, you can just run the following, which will deploy to whatever `S3_BUCKET` is specified in _config.yaml: 
	
	python deploy.py

### To-Do

A lot. 
