#!/usr/bin/python

from html import parser
from enum import Enum
import sqlite3 as sql
import sys

class SkillParser(parser.HTMLParser):
    def clearall(self):
        self.tagStack=[]
        self.attrStack=[]
        self.stackMatching=[
            (["img","span","h2","div","div","div","body","html"],None,False,"name"),
            (["div","div","div","div","body","html"],None,False,"desc"),
            (["span","td","tr","table","div","div","div","div","body","html"],None,"title","primaryID"),
            (["span","td","tr","table","div","div","div","div","body","html"],None,"title","secondaryID"),
            (["span","td","tr","table","div","div","div","div","body","html"],{"style": "cursor: help;"},False,"multiplier"),
            (["span","td","tr","table","div","div","div","div","body","html"],{"style": "cursor: help;"},False,"cost")
        ]
        self.results=[dict()]
        self.lookingFor=0  
        self.printNext=0
        self.mdata=""
        self.conn=sql.connect("eveSkill.s3db")
        self.c=self.conn.cursor()
        
    def setGroup(self,group):
        r=self.c.execute("SELECT id FROM skillGroup WHERE name LIKE ? ;",(group,))
        f=r.fetchall()
        if not f:
            print("Group not found: %s" % (group) )
            return
        self.groupID=f[0][0]
        self.groupName=group
        
        print("Group ID %i set." % (self.groupID) )
    def handle_starttag(self,tag,attrs):
        self.tagStack.insert(0,tag)
        self.attrStack.insert(0,attrs)
        if self.lookingFor == len(self.stackMatching):
            self.lookingFor=0
            self.processResults()
            self.results.append(dict())
        m=self.stackMatching[self.lookingFor]
        match=False
        if len(self.tagStack) == len(m[0]):
            match=True
            for i in range(len(self.tagStack)):
                if self.tagStack[i] != m[0][i]:
                    match=False
                    break
            if m[1]:
                for j in m[1].keys():
                    a=None
                    for i in attrs:
                        if i[0] == j:
                            a=i
                    if not a:
                        break
                    
                    if not a[1] == m[1][a[0]]:
                        match=False
                        break
                    
        if match:

            
            if m[2]:
                for i in attrs:
                    if m[2]==i[0]:
                        self.results[-1][m[-1]]=i[1]
                        self.lookingFor+=1
                        break
            else:
                self.printNext=2
        
                
    def handle_endtag(self,tag):
        i=self.tagStack.index(tag)
        self.tagStack.pop(i)
        self.attrStack.pop(i)
        if(self.printNext>0):
            self.printNext-=1
            if(self.printNext == 0):
                self.results[-1][self.stackMatching[self.lookingFor][-1]]=self.mdata
                self.mdata=""
                self.lookingFor+=1
                
        
    def handle_data(self,data):
        if self.printNext>0:
            d=data.strip('\n')
            if d:
                self.mdata+=d


    def processResults(self):
        name=self.results[-1]['name']
        desc=self.results[-1]['desc']
        
        primaryAttribute=self.results[-1]['primaryID'].split(' ')[2]
        self.c.execute("SELECT id FROM attribute WHERE name LIKE ? ;",(primaryAttribute,))
        primaryID=self.c.fetchall()[0][0]
        
        secondaryAttribute=self.results[-1]['secondaryID'].split(' ')[2]
        self.c.execute("SELECT id FROM attribute WHERE name LIKE ? ;",(secondaryAttribute,))
        secondaryID=self.c.fetchall()[0][0]
        
        multiplier=self.results[-1]['multiplier'].rstrip('x')
        cost=self.results[-1]['cost'].rstrip('\xa0ISK')
        self.c.execute(
'''
INSERT INTO skill( name, desc, primaryID, secondaryID, groupID, multiplier, cost )
VALUES( ?, ?, ?, ?, ?, ?, ?);
''', ( name, desc, primaryID, secondaryID, self.groupID, multiplier, cost ) )
##        print( "---RESULT:---\nName: %s\n Desc: %s\n Primary: %s [%s]\nSecondary %s [%s]\nMultiplier: %s Cost: %s" %
##               ( name, desc, primaryAttribute, primaryID, secondaryAttribute, secondaryID, multiplier, cost ) )
        self.conn.commit()
                               
        
for file in sys.argv[1:]:
    try:
        print("File: %s" % (file))
        p = SkillParser()
        p.clearall()
        p.setGroup(file.replace('_',' '))
        f = open(file)
        p.feed(f.read())
        f.close()
    except Exception as e:
        print(e)

