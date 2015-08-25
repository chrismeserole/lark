---
title: Lark Now Runs Python
date: 2015-04-17
---

One reason I've been writing [Lark](https://github.com/chrismeserole/lark/), the static site generator that now powers this site, was to have the freedom to cook up unique ways of merging writing and data analysis. 

Thankfully, I'm glad to say I hit the first milestone on that path today. It took a bit of hacking, but thanks to Matthew Rocklin's great new [pymarkdown](https://github.com/mrocklin/pymarkdown) module, [Lark now executes Python code blocks in posts](https://github.com/chrismeserole/lark/blob/master/_posts/python-example.md) when it builds the site.

The end result? I can now stick this in a post ... 

	```Python
	>>> x = 3
	>>> x + 1
	[should be 4]
	>>> 2 + 2*x
	missing or wrong results will be overwritten
	```

... and have it show up as this:  

```Python
>>> x = 3
>>> x + 1
[should be 4]
>>> 2 + 2*x
missing or wrong results will be overwritten
```

Lark still needs a lot of work, but it's fun to think about the possibilities this opens up.  