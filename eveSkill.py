#!/usr/bin/python

from html import parser
from enum import Enum
import sqlite3 as sql


f=open("Spaceship Command.eveuni.html")
DEBUG=False
class SkillType(Enum):
    none = 1
    name = 2
    desc = 3
    multiplier = 4
    primaryID = 5
    secondaryID = 6
    groupID = 7
    
class SkillParser(parser.HTMLParser):
    def clearall(self):
        self.tagStack=[]
        self.attrStack=[]
        self.stackMatching=[
            (["img","span","h2","div","div","div","body","html"],None,False,"name"),
            (["div","div","div","div","body","html"],None,False,"desc"),
            (["span","td","tr","table","div","div","div","div","body","html"],None,"title","primaryAttribute"),
            (["span","td","tr","table","div","div","div","div","body","html"],None,"title","secondaryAttribute"),
            (["span","td","tr","table","div","div","div","div","body","html"],{"style": "cursor: help;"},False,"multiplier"),
            (["span","td","tr","table","div","div","div","div","body","html"],{"style": "cursor: help;"},False,"cost")
        ]
        self.results=[]
        self.lookingFor=0  
        self.printNext=0
        
    def handle_starttag(self,tag,attrs):
        self.tagStack.insert(0,tag)
        self.attrStack.insert(0,attrs)
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
##                    print("testing for %s in:" % (str(j)))
##                    print(attrs)
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
##            print("Match: %s" % (m[-1]))
            self.lookingFor+=1
            if self.lookingFor == len(self.stackMatching):
                self.lookingFor=0
            self.results.append(dict())
            
            if m[2]:
                for i in attrs:
                    if m[2]==i[0]:
                        print(i[1])
                
            self.printNext=2
        
                
    def handle_endtag(self,tag):
        i=self.tagStack.index(tag)
        self.tagStack.pop(i)
        self.attrStack.pop(i)
        if(self.printNext>0):
            self.printNext-=1
        
    def handle_data(self,data):
        if self.printNext>0:
            d=data.strip('\n')
            if d:
                print(d)
        
parser = SkillParser()
parser.clearall()

