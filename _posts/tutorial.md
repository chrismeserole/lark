---
title: about obsval()
date: 2015-04-21
slug: about
---

**obsval()** is an R package that aims to make it much easier to calculate predicted effects in R, particularly when using observed covariate values. It's based on [Hanmer and Kalkan (2013)][hanmer].

To get up and running, see the sections below: 

- [Installing obsval()](#how-install)
- [Using obsval()](#how-use)
- [Why Use Observed Values?](#why-use)


You can also consult the following tutorials:

- Logit (Coming soon)
- Probit (Coming soon)
- Ordinal Logit (Coming soon)
- Ordinal Probit (Coming soon)
- Conditional Logit (Coming soon)
- Multinomial Logit (Coming soon)
- Poisson (Coming soon)
- Negative Binomial (Coming soon)

---------------------------------


#####  <a name="how-install"/></a>How To Install obsval()

At present the package is only available via Github. 

To install it, run the following: 

```r
install.packages("devtools")
library(devtools)
devtools::install_github("chrismeserole/obsval")
library(obsval)
```

That should let you call `obsval()`. If you're seeing any error messages with this, please contact me. 

---------------------------------

##### <a name="how-use"/></a>How to Use obsval()

The example below should make it clear how to use obsval(). 

First, load the libraries below: 

```{r}
library(obsval)
library(mvtnorm)
library(MASS)
```

**Note**: if you get any errors while running this, make sure all the packages are installed by running `install.packages(package_name)`.


The data we'll use comes from a dataset in the MASS package called quine, which contains information about a set of students in Australia, including their gender, ethnicity, age group, and days of school missed. 

In this case, we're interested in the effect of age on the number of days missed. Since that number is probably overdispersed, we'll use a negative binomial model:

```{r}
mod <- obsval( data = quine, 
	specification = 'Days~Eth+Sex+Age', 
	reg_model = "negbin", 
	n_draws = 1000,
	effect_var = "Age", 
	effect_var_low = "F0", 
	effect_var_high = "F3" )
```
That's it. To get the effects, we can then run: 
```{r}
mod$effect_sum
``` 
That's combines information from the following: 
```{r}
mod$effect_mean
mod$effect_low_ci
mod$effect_high_ci
```
You can also get that information by using the `$preds` object, which in this case is a vector of all predicted effects:
```{r}
head(mod$preds)
mean(mod$preds)
quantile(mod$preds, c(0.025,0.975))
```

And that's that.



---------------------------------


##### <a name="why-use"/></a> Why Use Observed Values?

Social scientists rely on statistics in order to tease out the effect of one variable on another, even when other variables ("covariates") might be intervening. 

At present, most software packages calculate effects using the average values of those covariates. However, unless we have a specific theoretical interest in the average case, using average rather observed covariate values will often bias our results. If what we're interested in is the effect of a variable on a given population, then to calculate it we should be using all the information that we have about that population. 

Put differently, for our theory to match our empirics, what we often want is the average effect overall, not the effect on the average case.

For a more in-depth explanation, see the excellent [AJPS paper by Hanmer and Kalkan][hanmer]

---------------------------------

[hanmer]: http://onlinelibrary.wiley.com/doi/10.1111/j.1540-5907.2012.00602.x/abstract;jsessionid=AAADB9AE61EA032F8AA008550E5BB52E.f04t0

