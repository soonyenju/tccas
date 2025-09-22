#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Songyan Zhu
# Mail: zhusy93@gmail.com
# Created Time:  2025-09-21 23:59
#############################################


from setuptools import setup, find_packages

setup(
	name = "tccas",
	version = "0.0.11",
	keywords = ("Geospatial scientific ML"),
	description = "Terrestrial Carbon Community Assimilation System (TCCAS)",
	long_description = "coming soon",
	license = "MIT Licence",

	url="https://github.com/soonyenju/tccas",
	author = "Songyan Zhu",
	author_email = "zhusy93@gmail.com",

	packages = find_packages(),
	include_package_data = True,
	platforms = "any",
	install_requires=[

	]
)