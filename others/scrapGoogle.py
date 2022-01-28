#===============================================================================================
#===============================================================================================
"""
What? Automatically download pdf, ppt, doc, docx from Google search. 

Run on a Windows machine!

References:
https://www.geeksforgeeks.org/performing-google-search-using-python-code/
https://stackoverflow.com/questions/29382709/urllib-request-module-fails-to-install-in-my-system
"""
#===============================================================================================
#===============================================================================================


#==============
#IMPORT MODULES
#==============
import google
from googlesearch import search
import urllib
from bs4 import BeautifulSoup
import os
import urllib3 as urllib
#from HTMLParser import HTMLParseError


#==============
#CREATE FOLDERS
#==============
newpath = './testFolder' 
try:
    if os.path.exists(newpath) == False:
        os.makedirs(newpath, mode = 755)
except WindowsError:
    pass


#===============
#SCRAP ON GOOGLE
#===============
def google_scrape(url):
    thepage = urllib.urlopen(url)
    soup = BeautifulSoup(thepage, "html.parser")    
    try:
        soup.title.text != []              
        return soup.title.text    
    except (HTMLParseError, AttributeError) as e:
        print ('\n Either a HTMLParseError or attribute error ### \n')
        pass


#====================
#TYPE HERE YOUR QUERY
#====================
query = 'Learn machine learning'


#===============================
#SELECT ONLY PDF, PPT, DOC, DOCX
#===============================
i = 1
for url in search(query, stop = 10):
    try:
        a = google_scrape(url)
    except IOError:
        print('\n ### IOError ### \n')
        pass   
    try:
        print(str(i) + ". " + a)
    except TypeError:
        print('\n ### typerror ### \n')
        pass
    print ('\nurl being downloaded\n'),url
    i += 1  

    #SAVING THE FILES BASED ON THEIR EXTENTION
    if url.endswith('.ppt') == True:
        print ("downloading ppt No.="+str(i))
        try:
            urllib.urlretrieve (url, newpath+"/"+str(i)+".ppt")
        except IOError:
            print ('\n ### IOError ### \n')
            pass        
        
    if url.endswith('.pdf') == True:
        print ("downloading pdf No.="+str(i))           
        try:
            urllib.urlretrieve (url, newpath+"/"+str(i)+".pdf")
        except IOError:
            print ('\n ### IOError ### \n')
            pass 

    if url.endswith('.doc') == True:
        print ("downloading doc No.="+str(i))           
        try:
            urllib.urlretrieve (url, newpath+"/"+str(i)+".doc")
        except IOError:
            print ('\n ### IOError ### \n')
            pass 

    if url.endswith('.docx') == True:
        print ("downloading docx No.="+str(i))           
        try:
            urllib.urlretrieve (url, newpath+"/"+str(i)+".docx")
        except IOError:
            print ('\n ### IOError ### \n')
            pass 

                
#===
#EoF
#=== 
