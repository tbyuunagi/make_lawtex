import requests
import os
import xml.etree.ElementTree as ET
import re

# egovのxmlの構造はPart：編、Chapter：章、Section：節、Subsection：款、Subsubsection：目、Article：条、Paragraph：項、Item：号、Subitem:イロハ

# 法令リストを取得してxmlファイルを保存、更新するときだけ使う
def  get_lawlist():
    r = requests.get('https://elaws.e-gov.go.jp/api/1/lawlists/1')
    root = ET.fromstring(r.text)
    tree = ET.ElementTree(element=root)
    if not os.path.exists('laws/'):
        os.mkdir('laws')
    tree.write('laws/lawlist.xml', encoding='utf-8', xml_declaration=True)
    return

# 法令名一覧から特定の法律をキーワードで検索した上で法令の正式名称と法令番号を返す関数
def search_Laws(key):
    tree = ET.parse('laws/lawlist.xml')
    root = tree.getroot()
    LawName_list = []
    LawNo_list = []
    for child in root[1]:
        if child.tag != 'Category':
            if key in child[0].text:
                LawName_list.append(child[0].text)
                LawNo_list.append(child[1].text)
    return LawName_list, LawNo_list

# 入出力
def get_Law(search_Laws):
    LawName_list = search_Laws[0]
    LawNo_list = search_Laws[1]
    if len (LawName_list) == 0:
        print('当てはまる法令がありません')
        return None
    if len(LawName_list) == 1:
        return LawName_list[0], LawNo_list[0]
    for i,x in enumerate(LawName_list):
        print(i+1,x)
    print('どれですか？')
    input_num = int(input())-1
    LawName = LawName_list[input_num]
    LawNo = LawNo_list[input_num]
    return LawName, LawNo

# get_Lawの結果を用いて内容を取得し、当該法令名で保存
def get_LawContent(get_Law):
    LawName = get_Law[0]
    LawNo = get_Law[1]
    r = requests.get('https://elaws.e-gov.go.jp/api/1/lawdata/'+LawNo)
    root = ET.fromstring(r.text)
    tree = ET.ElementTree(element=root)
    if not os.path.exists('laws/'):
        os.mkdir('laws')
    tree.write('laws/' + LawName + '.xml', encoding='utf-8', xml_declaration=True)

    with open('laws/' + LawName + '.xml',mode='r',encoding='utf-8') as f:
        text=f.read()
    with open('laws/' + LawName + '.xml',mode='w',encoding='utf-8') as f:
        f.write(delete_ruby(text))
    return LawName

# 検索して保存
def search_get_LawContent():
    print('検索したいキーワードを入れてください')
    key = input()
    search_Results = search_Laws(key)
    get_Result = get_Law(search_Results)
    if get_Result == None:
        print('キーワードに合致する法令が見つかりません')
        return
    get_Content = get_LawContent(get_Result)
    return get_Content

def delete_ruby(text):
    text = re.sub('\\<Rt\\>.+?\\<\\/Rt\\>','',text)
    text = re.sub('\\<Ruby\\>','',text)
    text = re.sub('\\<\\/Ruby\\>','',text)
    return text

def delete_new_line(text):
    text = re.sub('\\n', '', text)
    return text

# xmlをtexの形式にする。
def Part_to_tex(f, Partiter):
    for Part in Partiter:
        for i in Part.find('PartTitle').itertext():
            f.write('\\part*{' + delete_new_line(i) + '}\n\\addcontentsline{toc}{part}{' + delete_new_line(i) + '}\n')
        if Part.find('.//Chapter') != None:
            Chapter_to_tex(f, Part.findall('Chapter'))
        else:
            Article_to_tex(f, Part.findall('Article'))
    return

def Chapter_to_tex(f, Chapteriter):
    for Chapter in Chapteriter:
        for i in Chapter.find('ChapterTitle').itertext():
            f.write('\\section*{' + delete_new_line(i) + '}\n\\addcontentsline{toc}{section}{' + delete_new_line(i) + '}\n')
        if Chapter.find('.//Section') != None:
            Section_to_tex(f, Chapter.findall('Section'))
        else:
            Article_to_tex(f, Chapter.findall('Article'))
    return

def Section_to_tex(f, Sectioniter):
    for Section in Sectioniter:
        for i in Section.find('SectionTitle').itertext():
            f.write('\\subsection*{' + delete_new_line(i) + '}\n\\addcontentsline{toc}{subsection}{' + delete_new_line(i) + '}\n')
        if Section.find('.//Subsection') != None:
            Subsection_to_tex(f, Section.findall('Subsection'))
        else:
            Article_to_tex(f, Section.findall('Article'))
    return

def Subsection_to_tex(f, Subsectioniter):
    for Subsection in Subsectioniter:
        for i in Subsection.find('SubsectionTitle').itertext():
            f.write('\\subsubsection*{' + delete_new_line(i) + '}\n\\addcontentsline{toc}{subsubsection}{' + delete_new_line(i) + '}\n')
        if Subsection.find('.//Division') != None:
            Division_to_tex(f, Subsection.findall('Division'))
        else:
            Article_to_tex(f, Subsection.findall('Article'))
    return

def Division_to_tex(f, Divisioniter):
    for Division in Divisioniter:
        for i in Division.find('DivisionTitle').itertext():
            f.write('\\subsubsubsection*{' + delete_new_line(i) + '}\n{' + delete_new_line(i) + '}\n')
        Article_to_tex(f, Division.findall('Article'))
    return

def Article_to_tex(f, Articleiter):
    for Article in Articleiter:
        if Article.find('ArticleCaption') != None:
            a = ""
            for i in Article.find('ArticleCaption').itertext():
                a += delete_new_line(i)
            f.write('\\noindent\\hspace{10pt}' + a + '\n')
        para = 1
        for Paragraph in Article.findall('Paragraph'):
            if len(Article.findall('Paragraph')) > 1:
                if para == 1:
                    f.write('\\begin{description}\n\\item[' + delete_new_line(Article.find('ArticleTitle').text) + ']')
                    para += 1
                    Paragraph_to_tex(f, Paragraph)
                else:
                    f.write('\item[\\rensuji{' + str(para) + '}]')
                    para += 1
                    Paragraph_to_tex(f, Paragraph)
            else:
                f.write('\\begin{description}\n\\item[' + delete_new_line(Article.find('ArticleTitle').text) + ']')
                Paragraph_to_tex(f, Paragraph)
        f.write('\\end{description}\n')
    return

def Paragraph_to_tex(f, Paragraph):
    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:                     
        return                                                                             
    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:                     
        return                                                                                   
    for i in Paragraph.find('ParagraphSentence').findall('Sentence'):                 
        f.write(delete_new_line(i.text))                                                                  
    f.write('\n')                                                                                
    if Paragraph.find('.//Item') != None:                                                        
        f.write('\\begin{description}\n')                                                        
        Item_to_tex(f, Paragraph.findall('.//Item'))
        f.write('\\end{description}\n')
    return

def Item_to_tex(f, Itemiter):
    for Item in Itemiter:
        f.write('\item[' + delete_new_line(Item.find('.//ItemTitle').text) + ']')
        if Item.find('.//ItemSentence').find('.//Column') != None:               
            for Column in Item.find('.//ItemSentence').findall('.//Column'):     
                for i in Column.findall('Sentence'):                             
                    f.write(delete_new_line(i.text))                                 
                f.write('  ')                                                    
            f.write('\n')
            if Item.find('.//Subitem1') != None:
                f.write('\\begin{description}\n')
                Subitem1_to_tex(f, Item.findall('.//Subitem1'))
                f.write('\\end{description}\n')
        else:
            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                break                                                   
            for i in Item.find('.//ItemSentence').findall('Sentence'):  
                f.write(delete_new_line(i.text))                            
            f.write('\n')                                               
            if Item.find('.//Subitem1') != None:
                f.write('\\begin{description}\n')              
                Subitem1_to_tex(f, Item.findall('.//Subitem1'))
                f.write('\\end{description}\n')                
    return
    
def Subitem1_to_tex(f, Subitem1iter):
    for Subitem1 in Subitem1iter:
        f.write('\item[' + delete_new_line(Subitem1.find('Subitem1Title').text) + ']')
        if Subitem1.find('.//Subitem1Sentence').find('.//Column') != None:          
            for Column in Subitem1.find('.//Subitem1Sentence').findall('.//Column'):
                for i in Column.findall('Sentence'):                                
                    f.write(delete_new_line(i.text))                                    
                f.write('  ')                                                       
            f.write('\n')
            if Subitem1.find('.//Subitem2') != None:
                f.write('\\begin{description}\n')
                Subitem2_to_tex(f, Subitem1.findall('Subitem2'))
                f.write('\\end{description}\n')
        else:                                                                       
            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:    
                break                                                               
            for i in Subitem1.find('.//Subitem1Sentence').findall('Sentence'):      
                f.write(delete_new_line(i.text))                                        
            f.write('\n')
            if Subitem1.find('.//Subitem2') != None:
                f.write('\\begin{description}\n')
                Subitem2_to_tex(f, Subitem1.findall('Subitem2'))
                f.write('\\end{description}\n')
    return

def Subitem2_to_tex(f, Subitem2iter):
    for Subitem2 in Subitem2iter:
        f.write('\item[' + delete_new_line(Subitem2.find('Subitem2Title').text) + ']')
        if Subitem2.find('.//Subitem2Sentence').find('.//Column') != None:
            for Column in Subitem2.find('.//Subitem2Sentence').findall('.//Column'):
                for i in Column.findall('Sentence'):    
                    f.write(delete_new_line(i.text))    
                f.write('  ')                       
            f.write('\n')
        else:
            if Subitem2.find('.//Subitem2Sentence').find('.//Sentence') == None:
                break                                                           
            for i in Subitem2.find('.//Subitem2Sentence').findall('Sentence'):  
                f.write(delete_new_line(i.text))                                    
            f.write('\n')                                                       
    return

def xml_to_tex(Law_Name):
    if not os.path.exists('laws/' + Law_Name + '.xml'):
        return None
    tree = ET.parse('laws/' + Law_Name + '.xml')
    root = tree.getroot()
    with open('laws/' + Law_Name + '.tex', 'w', encoding='utf-8') as f:
        f.write('\\documentclass[twocolumn,a4j,10pt]{ltjtarticle}\n\\title{' + delete_new_line(Law_Name) + '}\n\\author{}\n\\date{}\n\\renewcommand{\\baselinestretch}{0.8}\n\\setlength{\columnseprule}{.4pt}\n\\usepackage{enumitem}\n\\setlist[description]{topsep=3pt,parsep=0pt,partopsep=0pt,itemsep=3pt,leftmargin=10pt,labelsep=5pt,labelsep=10pt}\n\\makeatletter\n\\newcommand{\\subsubsubsection}{\\@startsection{paragraph}{4}{\\z@}%\n  {1.0\\Cvs \\@plus.5\\Cdp \\@minus.2\\Cdp}%\n  {.1\\Cvs \\@plus.3\\Cdp}%\n  {\\reset@font\\sffamily\\normalsize}\n}\n\\makeatother\n\\setcounter{secnumdepth}{4}\n\\begin{document}\n\\maketitle\n\\tableofcontents\n')
        if root.find('.//MainProvision').find('.//Part') != None:
            Part_to_tex(f, root.find('.//MainProvision').iter('Part'))
        elif root.find('.//MainProvision').find('.//Chapter') != None:
            Chapter_to_tex(f, root.find('.//MainProvision').findall('Chapter'))
        else:
            Article_to_tex(f, root.find('.//MainProvision').iter('Article'))
        f.write('\\end{document}\n')
    return Law_Name


def main():
    get_lawlist()
    Law_Name = search_get_LawContent()
    result = xml_to_tex(Law_Name)
    return result

if __name__ == '__main__':
    main()
