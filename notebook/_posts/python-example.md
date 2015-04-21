---
title: Python Scripting Demo
date: 2015-04-15
---


Lark now executes wrapped python code when it builds the site. 

Markdown:

	```Python
	>>> x = 3
	>>> x + 1
	[should be 4]
	>>> 2 + 2*x
	missing or wrong results will be overwritten
	```

HTML: 

```Python
>>> x = 3
>>> x + 1
[should be 4]
>>> 2 + 2*x
missing or wrong results will be overwritten
```
------------------


Markdown:

	```Python
	>>> animals = ["cat","dog","horse"]
	>>> animals[1]
	```

HTML: 


```Python
>>> animals = ["cat","dog","horse"]
>>> animals[1]
```

------------------


Markdown*: 

	```Python
	>>> y = 10
	>>> x + y
	```

HTML: 


```Python
>>> y = 10
>>> x + y
```
--------------------

*All blocks in a file are run cumulatively, as a single script. 

**Code blocks thus remember state/inherit  values**. 