
import urllib2
import urllib
import urllib2
import re


url='http://booksc.org/s/?q=SAE+f1+aerodynamics&t=0'
website = urllib2.urlopen(url)

#read html code
html = website.read()

#use re.findall to get all the links
links = re.findall('"((http|ftp)s?://.*?)"', html)

#=================================
#FIRST LOOP SELECTS THE LINK TO PDF
#SECOND LOOP SCRAPS FOR PDF
#THIRD LOOP SELECTS PDF LINK ONLY
#THE WEBSITE HAS AN ANTI-SCRAPER
#=================================

for i in range(len(links)):
        link_to_file='http://booksc.org/dl/'
        dummy = str(links[i][0]) 
        if (link_to_file in dummy) == True:

            website2 = urllib2.urlopen(str(links[i][0]))
            html2 = website2.read()
            links2 = re.findall('"((http|ftp)s?://.*?)"', html2)

            for j in range(len(links2)):
                dummy2 = str(links2[j][0])
                if dummy2.endswith('.pdf') == True:
                    print i, dummy2

                    urllib.urlretrieve (links2[j][0], "./"+str(i)+"_"+".pdf")
                    break #there are multiple links, you just want one of them
           

