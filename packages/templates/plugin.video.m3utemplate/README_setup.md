# plugin.video.m3utemplate

## Setup

Set by step guide to setting up the template for your M3U files

###### Main folder
Copy contents of `plugin.video.m3utemplate` folder and rename  to `plugin.video.<name>` 
	Try to use something unique and close to addon name

###### addon.xml

Edit these lines in the addon.xml
[addon.xml](./addon.xml)

``` xml
<addon id="plugin.video." name="" version="0.0.0" provider-name="">
```

* addon
	* id is the id of the addon eg "plugin.video.m3utemplate"
	* name is the displayed name of the addon
	* version is the version of the addon 0.0.0 is Major.Minor.Patch 


``` xml
<summary lang="en"></summary>
<description lang="en"></description>
<news>v0.0.1 - Kodi 19</news>
```
* summary is a brief description of the addon
* description is a more detailed description
* news can include update info or info for user
Multiple summary and description's can be added for different languages change `lang=""` to suit 

##### uservar.py

[uservar.py](./uservar.py)

Edit file as described in Notes in file
```python
''' 
----------Edit required---------
For online xml for sources, edit the host to the url of the file host='http://something.com/sources.xml'
For local xml file, edit the host to local host='local' and call the file 'sources.xml' and place in the folder
please see sample.xml for layout
on line source can be either https or http
'''

host='local'
```

##### fanart.jpg

[fanart.jpg](./fanart.jpg)

Change fanart to your select, must retain the name fanart.jpg

##### icons

[icons](./icons/)

Change icons to your own design 'icon.png' is the addon icon all the rest are used in the addon for menus names must not be changed only the images itself
* Icons
	* [favorites.png](./resources/icons/favorites.png)

	* [icon.png](./resources/icons/icon.png)

	* [recent.png](./resources/icons/recent.png)

	* [search.png](./resources/icons/search.png])

	* [settings.png](./resources/icons/settings.png)

##### sources.xml

[sources.xml](./sample.xml)

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sources>
	<source>
		<url>https://something.com/that.m3u</url>
		<name>Source 1</name>
		<icon>http://pathtoa.com/icon.jpg</icon>
	</source>
	<source>
		<url>http://another.com/this.m3u</url>
		<name>Source 2</name>
		<icon>special://home/</icon>
	</source>
</sources>
```

Edit the sample.xml to suit 
* url path to on line file
* name of source to be displayed in menu
* icon of source to be displayed in menu

Please see uservar.py notes for more information on location of this file

##### UserGuide

To use the UserGuide add this dir to your repository 

```xml
<dir>
	<info compressed="false">https://raw.githubusercontent.com/bigyidbuilds/xbmc/main/packages/gui/addons.xml</info>
	<checksum>https://raw.githubusercontent.com/bigyidbuilds/xbmc/main/packages/gui/addons.xml.md5</checksum>
	<datadir zip="true">https://raw.githubusercontent.com/bigyidbuilds/xbmc/main/packages/gui/</datadir>
</dir>
```

[Click for more information on script.gui.markdown.syntax.userguide](https://github.com/bigyidbuilds/script.gui.markdown.syntax.userguide#readme)

##### Useful links

[README Converter .md to .html](https://dillinger.io/)
[ISO Country codes](http://geohack.net/gis/wikipedia-iso-country-codes.csv)
