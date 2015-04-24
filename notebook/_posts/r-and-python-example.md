---
title: Example R and Python Code
date: 2015-04-17
---


This post is a demo. All R and Python code are executed at build, including images. 

R is now working. Maplotlib appears to be working, but for some reason isn't saving locally. 

--------------

Here goes. First let's try R. Markdown:

```{r}
x <- rnorm(100)
summary(x)
```

Now let's switch over to Python:

```Python
>>> x = 3
>>> x + 1
[should be 4]
>>> 2 + 2*x
missing or wrong results will be overwritten
```

Ok. Let's try plotting stuff. 

First in R: 

```{r}
plot(cars)
```

Now let's try a plot in Python ... 

```Python
>>> import matplotlib.pyplot as plt

>>> fig = plt.figure()
>>> plt.plot([1, 2, 3, 4, 5], [6, 7, 2, 4, 5])
>>> fig
```

Bummer. Looks like fig object exists, it's just not being passed properly to Lark.

```{r}
x <- rnorm(100)
y <- 2.5 + 2*x + rnorm(100)
plot(y~x)
```

More text.