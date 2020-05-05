import requests
import os
import xml.etree.ElementTree as ET

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


# xmlをtexの形式にする。単純化の余地がある。
def xml_to_tex(Law_Name):
    if not os.path.exists('laws/' + Law_Name + '.xml'):
        return None
    tree = ET.parse('laws/' + Law_Name + '.xml')
    root = tree.getroot()
    with open('laws/' + Law_Name + '.tex', 'w', encoding='utf-8') as f:
        f.write('\\documentclass[twocolumn,a4j,10pt]{ltjtarticle}\n\\title{' + Law_Name + '}\n\\author{}\n\\date{}\n\\renewcommand{\\baselinestretch}{0.8}\n\\setlength{\columnseprule}{.4pt}\n\\usepackage{enumitem}\n\\setlist[description]{topsep=3pt,parsep=0pt,partopsep=0pt,itemsep=3pt,leftmargin=10pt,labelsep=5pt,labelsep=10pt}\n\\makeatletter\n\\newcommand{\\subsubsubsection}{\\@startsection{paragraph}{4}{\\z@}%\n  {1.0\\Cvs \\@plus.5\\Cdp \\@minus.2\\Cdp}%\n  {.1\\Cvs \\@plus.3\\Cdp}%\n  {\\reset@font\\sffamily\\normalsize}\n}\n\\makeatother\n\\setcounter{secnumdepth}{4}\n\\begin{document}\n\\maketitle\n\\tableofcontents\n')

        
        if root.find('.//MainProvision').find('.//Part') != None:
            for Part in root.find('.//MainProvision').iter('Part'):
                for i in Part.find('PartTitle').itertext():
                    f.write('\\part*{' + i + '}\n\\addcontentsline{toc}{part}{' + i + '}\n')
    
                if Part.find('.//Chapter') != None:
                    for Chapter in Part.findall('Chapter'):
                        for i in Chapter.find('ChapterTitle').itertext():
                            f.write('\\section*{' + i + '}\n\\addcontentsline{toc}{section}{' + i + '}\n')
                            
                        if Chapter.find('.//Section') != None:
                            for Section in Chapter.findall('Section'):
                                for i in Section.find('SectionTitle').itertext():
                                    f.write('\\subsection*{' + i + '}\n\\addcontentsline{toc}{subsection}{' + i + '}\n')
                                    
                                if Section.find('.//Subsection') != None:
                                    for Subsection in Section.findall('Subsection'):
                                        for i in Subsection.find('SubsectionTitle').itertext():
                                            f.write('\\subsubsection*{' + i + '}\n\\addcontentsline{toc}{subsubsection}{' + i + '}\n')
                                            
                                        if Subsection.find('.//Division') != None:
                                            for Division in Subsection.findall('Division'):
                                                for i in Division.find('DivisionTitle').itertext():
                                                    f.write('\\subsubsubsection*{' + i + '}\n{' + i + '}\n')
                                                    
                                                    for Article in Division.findall('Article'):
                                                        if Article.find('ArticleCaption') != None:
                                                            for i in Article.find('ArticleCaption').itertext():
                                                                f.write('\\noindent\\hspace{10pt}' + i + '\n')
                        
                                                        para = 1
                                                        for Paragraph in Article.findall('Paragraph'):
                                                            if len(Article.findall('Paragraph')) > 1:
                                                                if para == 1:
                                                                    f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                                    para += 1
                                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                        break
                                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                                        break
                                                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                    if Paragraph.find('.//Item') != None:
                                                                        f.write('\\begin{description}\n')
                                                                        for Item in Paragraph.findall('.//Item'):
                                                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                                break
                                                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                                f.write(i)
                                                                            f.write('\n')
                                                                            if Item.find('.//Subitem1') != None:
                                                                                f.write('\\begin{description}\n')
                                                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                                        break
                                                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                                        f.write(i)
                                                                                    f.write('\n')
                                                                                f.write('\\end{description}\n')
                                                                        f.write('\\end{description}\n')
                                                                else:
                                                                    f.write('\item[\\rensuji{' + str(para) + '}]')
                                                                    para += 1
                                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                        break
                                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                                        break
                                                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                    if Paragraph.find('.//Item') != None:
                                                                        f.write('\\begin{description}\n')
                                                                        for Item in Paragraph.findall('.//Item'):
                                                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                                break
                                                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                                f.write(i)
                                                                            f.write('\n')
                                                                            if Item.find('.//Subitem1') != None:
                                                                                f.write('\\begin{description}\n')
                                                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                                        break
                                                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                                        f.write(i)
                                                                                    f.write('\n')
                                                                                f.write('\\end{description}\n')
                                                                        f.write('\\end{description}\n')
                                                            else:
                                                                f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                                if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                        break
                                                                if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                                    break
                                                                for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                                    f.write(i)
                                                                f.write('\n')
                                                                if Paragraph.find('.//Item') != None:
                                                                    f.write('\\begin{description}\n')
                                                                    for Item in Paragraph.findall('.//Item'):
                                                                        f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                        if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                            break
                                                                        for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                            f.write(i)
                                                                        f.write('\n')
                                                                        if Item.find('.//Subitem1') != None:
                                                                            f.write('\\begin{description}\n')
                                                                            for Subitem1 in Item.findall('.//Subitem1'):
                                                                                f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                                if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                                    break
                                                                                for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                                    f.write(i)
                                                                                f.write('\n')
                                                                            f.write('\\end{description}\n')
                                                                    f.write('\\end{description}\n')
                                                        f.write('\\end{description}\n')
                                        else:
                                            for Article in Subsection.findall('Article'):
                                                if Article.find('ArticleCaption') != None:
                                                    for i in Article.find('ArticleCaption').itertext():
                                                        f.write('\\noindent\\hspace{10pt}' + i + '\n')
                            
                                                para = 1
                                                for Paragraph in Article.findall('Paragraph'):
                                                    if len(Article.findall('Paragraph')) > 1:
                                                        if para == 1:
                                                            f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                            para += 1
                                                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                break
                                                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                                break
                                                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                            if Paragraph.find('.//Item') != None:
                                                                f.write('\\begin{description}\n')
                                                                for Item in Paragraph.findall('.//Item'):
                                                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                        break
                                                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                    if Item.find('.//Subitem1') != None:
                                                                        f.write('\\begin{description}\n')
                                                                        for Subitem1 in Item.findall('.//Subitem1'):
                                                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                                break
                                                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                                f.write(i)
                                                                            f.write('\n')
                                                                        f.write('\\end{description}\n')
                                                                f.write('\\end{description}\n')
                                                        else:
                                                            f.write('\item[\\rensuji{' + str(para) + '}]')
                                                            para += 1
                                                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                break
                                                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                                break
                                                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                            if Paragraph.find('.//Item') != None:
                                                                f.write('\\begin{description}\n')
                                                                for Item in Paragraph.findall('.//Item'):
                                                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                        break
                                                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                    if Item.find('.//Subitem1') != None:
                                                                        f.write('\\begin{description}\n')
                                                                        for Subitem1 in Item.findall('.//Subitem1'):
                                                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                                break
                                                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                                f.write(i)
                                                                            f.write('\n')
                                                                        f.write('\\end{description}\n')
                                                                f.write('\\end{description}\n')
                                                    else:
                                                        f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                        if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                break
                                                        if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                            break
                                                        for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                            f.write(i)
                                                        f.write('\n')
                                                        if Paragraph.find('.//Item') != None:
                                                            f.write('\\begin{description}\n')
                                                            for Item in Paragraph.findall('.//Item'):
                                                                f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                    break
                                                                for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                    f.write(i)
                                                                f.write('\n')
                                                                if Item.find('.//Subitem1') != None:
                                                                    f.write('\\begin{description}\n')
                                                                    for Subitem1 in Item.findall('.//Subitem1'):
                                                                        f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                        if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                            break
                                                                        for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                            f.write(i)
                                                                        f.write('\n')
                                                                    f.write('\\end{description}\n')
                                                            f.write('\\end{description}\n')
                                                f.write('\\end{description}\n')
                                else:
                                    for Article in Section.findall('Article'):
                                        if Article.find('ArticleCaption') != None:
                                            for i in Article.find('ArticleCaption').itertext():
                                                f.write('\\noindent\\hspace{10pt}' + i + '\n')
                        
                                        para = 1
                                        for Paragraph in Article.findall('Paragraph'):
                                            if len(Article.findall('Paragraph')) > 1:
                                                if para == 1:
                                                    f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                    para += 1
                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                        break
                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                        break
                                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                    if Paragraph.find('.//Item') != None:
                                                        f.write('\\begin{description}\n')
                                                        for Item in Paragraph.findall('.//Item'):
                                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                break
                                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                            if Item.find('.//Subitem1') != None:
                                                                f.write('\\begin{description}\n')
                                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                        break
                                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                f.write('\\end{description}\n')
                                                        f.write('\\end{description}\n')
                                                else:
                                                    f.write('\item[\\rensuji{' + str(para) + '}]')
                                                    para += 1
                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                        break
                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                        break
                                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                    if Paragraph.find('.//Item') != None:
                                                        f.write('\\begin{description}\n')
                                                        for Item in Paragraph.findall('.//Item'):
                                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                break
                                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                            if Item.find('.//Subitem1') != None:
                                                                f.write('\\begin{description}\n')
                                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                        break
                                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                f.write('\\end{description}\n')
                                                        f.write('\\end{description}\n')
                                            else:
                                                f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                        break
                                                if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                    break
                                                for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                    f.write(i)
                                                f.write('\n')
                                                if Paragraph.find('.//Item') != None:
                                                    f.write('\\begin{description}\n')
                                                    for Item in Paragraph.findall('.//Item'):
                                                        f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                        if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                            break
                                                        for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                            f.write(i)
                                                        f.write('\n')
                                                        if Item.find('.//Subitem1') != None:
                                                            f.write('\\begin{description}\n')
                                                            for Subitem1 in Item.findall('.//Subitem1'):
                                                                f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                    break
                                                                for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                    f.write(i)
                                                                f.write('\n')
                                                            f.write('\\end{description}\n')
                                                    f.write('\\end{description}\n')
                                        f.write('\\end{description}\n')
                        else:
                            for Article in Chapter.findall('Article'):
                                if Article.find('ArticleCaption') != None:
                                    for i in Article.find('ArticleCaption').itertext():
                                        f.write('\\noindent\\hspace{10pt}' + i + '\n')
    
                                para = 1
                                for Paragraph in Article.findall('Paragraph'):
                                    if len(Article.findall('Paragraph')) > 1:
                                        if para == 1:
                                            f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                            para += 1
                                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                break
                                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                break
                                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                            if Paragraph.find('.//Item') != None:
                                                f.write('\\begin{description}\n')
                                                for Item in Paragraph.findall('.//Item'):
                                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                        break
                                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                    if Item.find('.//Subitem1') != None:
                                                        f.write('\\begin{description}\n')
                                                        for Subitem1 in Item.findall('.//Subitem1'):
                                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                break
                                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                        f.write('\\end{description}\n')
                                                f.write('\\end{description}\n')
                                        else:
                                            f.write('\item[\\rensuji{' + str(para) + '}]')
                                            para += 1
                                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                break
                                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                break
                                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                            if Paragraph.find('.//Item') != None:
                                                f.write('\\begin{description}\n')
                                                for Item in Paragraph.findall('.//Item'):
                                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                        break
                                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                    if Item.find('.//Subitem1') != None:
                                                        f.write('\\begin{description}\n')
                                                        for Subitem1 in Item.findall('.//Subitem1'):
                                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                break
                                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                        f.write('\\end{description}\n')
                                                f.write('\\end{description}\n')
                                    else:
                                        f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                        if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                            break
                                        if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                            break
                                        for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                            f.write(i)
                                        f.write('\n')
                                        if Paragraph.find('.//Item') != None:
                                            f.write('\\begin{description}\n')
                                            for Item in Paragraph.findall('.//Item'):
                                                f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                    break
                                                for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                    f.write(i)
                                                f.write('\n')
                                                if Item.find('.//Subitem1') != None:
                                                    f.write('\\begin{description}\n')
                                                    for Subitem1 in Item.findall('.//Subitem1'):
                                                        f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                        if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                            break
                                                        for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                            f.write(i)
                                                        f.write('\n')
                                                    f.write('\\end{description}\n')
                                            f.write('\\end{description}\n')
                                f.write('\\end{description}\n')
    
                else:
                    for Article in Part.findall('Article'):
                        if Article.find('ArticleCaption') != None:
                            for i in Article.find('ArticleCaption').itertext():
                                f.write('\\noindent\\hspace{10pt}' + i + '\n')
    
                        para = 1
                        for Paragraph in Article.findall('Paragraph'):
                            if len(Article.findall('Paragraph')) > 1:
                                if para == 1:
                                    f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                    para += 1
                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                        break
                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                        break
                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                        f.write(i)
                                    f.write('\n')
                                    if Paragraph.find('.//Item') != None:
                                        f.write('\\begin{description}\n')
                                        for Item in Paragraph.findall('.//Item'):
                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                break
                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                            if Item.find('.//Subitem1') != None:
                                                f.write('\\begin{description}\n')
                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                        break
                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                f.write('\\end{description}\n')
                                        f.write('\\end{description}\n')
                                else:
                                    f.write('\item[\\rensuji{' + str(para) + '}]')
                                    para += 1
                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                        break
                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                        break
                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                        f.write(i)
                                    f.write('\n')
                                    if Paragraph.find('.//Item') != None:
                                        f.write('\\begin{description}\n')
                                        for Item in Paragraph.findall('.//Item'):
                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                break
                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                            if Item.find('.//Subitem1') != None:
                                                f.write('\\begin{description}\n')
                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                        break
                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                f.write('\\end{description}\n')
                                        f.write('\\end{description}\n')
                            else:
                                f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                    break
                                if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                    break
                                for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                    f.write(i)
                                f.write('\n')
                                if Paragraph.find('.//Item') != None:
                                    f.write('\\begin{description}\n')
                                    for Item in Paragraph.findall('.//Item'):
                                        f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                        if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                            break
                                        for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                            f.write(i)
                                        f.write('\n')
                                        if Item.find('.//Subitem1') != None:
                                            f.write('\\begin{description}\n')
                                            for Subitem1 in Item.findall('.//Subitem1'):
                                                f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                    break
                                                for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                    f.write(i)
                                                f.write('\n')
                                            f.write('\\end{description}\n')
                                    f.write('\\end{description}\n')
                        f.write('\\end{description}\n')
        elif root.find('.//MainProvision').find('.//Chapter') != None:
            for Chapter in root.find('.//MainProvision').findall('Chapter'):
                for i in Chapter.find('ChapterTitle').itertext():
                    f.write('\\section*{' + i + '}\n\\addcontentsline{toc}{section}{' + i + '}\n')
                    
                if Chapter.find('.//Section') != None:
                    for Section in Chapter.findall('Section'):
                        for i in Section.find('SectionTitle').itertext():
                            f.write('\\subsection*{' + i + '}\n\\addcontentsline{toc}{subsection}{' + i + '}\n')
                            
                        if Section.find('.//Subsection') != None:
                            for Subsection in Section.findall('Subsection'):
                                for i in Subsection.find('SubsectionTitle').itertext():
                                    f.write('\\subsubsection*{' + i + '}\n\\addcontentsline{toc}{subsubsection}{' + i + '}\n')
                                    
                                if Subsection.find('.//Division') != None:
                                    for Division in Subsection.findall('Division'):
                                        for i in Division.find('DivisionTitle').itertext():
                                            f.write('\\subsubsubsection*{' + i + '}\n{' + i + '}\n')
                                            
                                            for Article in Division.findall('Article'):
                                                if Article.find('ArticleCaption') != None:
                                                    for i in Article.find('ArticleCaption').itertext():
                                                        f.write('\\noindent\\hspace{10pt}' + i + '\n')
                
                                                para = 1
                                                for Paragraph in Article.findall('Paragraph'):
                                                    if len(Article.findall('Paragraph')) > 1:
                                                        if para == 1:
                                                            f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                            para += 1
                                                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                break
                                                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                                break
                                                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                            if Paragraph.find('.//Item') != None:
                                                                f.write('\\begin{description}\n')
                                                                for Item in Paragraph.findall('.//Item'):
                                                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                        break
                                                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                    if Item.find('.//Subitem1') != None:
                                                                        f.write('\\begin{description}\n')
                                                                        for Subitem1 in Item.findall('.//Subitem1'):
                                                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                                break
                                                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                                f.write(i)
                                                                            f.write('\n')
                                                                        f.write('\\end{description}\n')
                                                                f.write('\\end{description}\n')
                                                        else:
                                                            f.write('\item[\\rensuji{' + str(para) + '}]')
                                                            para += 1
                                                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                break
                                                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                                break
                                                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                            if Paragraph.find('.//Item') != None:
                                                                f.write('\\begin{description}\n')
                                                                for Item in Paragraph.findall('.//Item'):
                                                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                        break
                                                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                    if Item.find('.//Subitem1') != None:
                                                                        f.write('\\begin{description}\n')
                                                                        for Subitem1 in Item.findall('.//Subitem1'):
                                                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                                break
                                                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                                f.write(i)
                                                                            f.write('\n')
                                                                        f.write('\\end{description}\n')
                                                                f.write('\\end{description}\n')
                                                    else:
                                                        f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                        if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                                break
                                                        if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                            break
                                                        for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                            f.write(i)
                                                        f.write('\n')
                                                        if Paragraph.find('.//Item') != None:
                                                            f.write('\\begin{description}\n')
                                                            for Item in Paragraph.findall('.//Item'):
                                                                f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                                if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                    break
                                                                for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                    f.write(i)
                                                                f.write('\n')
                                                                if Item.find('.//Subitem1') != None:
                                                                    f.write('\\begin{description}\n')
                                                                    for Subitem1 in Item.findall('.//Subitem1'):
                                                                        f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                        if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                            break
                                                                        for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                            f.write(i)
                                                                        f.write('\n')
                                                                    f.write('\\end{description}\n')
                                                            f.write('\\end{description}\n')
                                                f.write('\\end{description}\n')
                                else:
                                    for Article in Subsection.findall('Article'):
                                        if Article.find('ArticleCaption') != None:
                                            for i in Article.find('ArticleCaption').itertext():
                                                f.write('\\noindent\\hspace{10pt}' + i + '\n')
                    
                                        para = 1
                                        for Paragraph in Article.findall('Paragraph'):
                                            if len(Article.findall('Paragraph')) > 1:
                                                if para == 1:
                                                    f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                    para += 1
                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                        break
                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                        break
                                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                    if Paragraph.find('.//Item') != None:
                                                        f.write('\\begin{description}\n')
                                                        for Item in Paragraph.findall('.//Item'):
                                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                break
                                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                            if Item.find('.//Subitem1') != None:
                                                                f.write('\\begin{description}\n')
                                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                        break
                                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                f.write('\\end{description}\n')
                                                        f.write('\\end{description}\n')
                                                else:
                                                    f.write('\item[\\rensuji{' + str(para) + '}]')
                                                    para += 1
                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                        break
                                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                        break
                                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                    if Paragraph.find('.//Item') != None:
                                                        f.write('\\begin{description}\n')
                                                        for Item in Paragraph.findall('.//Item'):
                                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                                break
                                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                            if Item.find('.//Subitem1') != None:
                                                                f.write('\\begin{description}\n')
                                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                        break
                                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                        f.write(i)
                                                                    f.write('\n')
                                                                f.write('\\end{description}\n')
                                                        f.write('\\end{description}\n')
                                            else:
                                                f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                                if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                        break
                                                if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                    break
                                                for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                    f.write(i)
                                                f.write('\n')
                                                if Paragraph.find('.//Item') != None:
                                                    f.write('\\begin{description}\n')
                                                    for Item in Paragraph.findall('.//Item'):
                                                        f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                        if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                            break
                                                        for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                            f.write(i)
                                                        f.write('\n')
                                                        if Item.find('.//Subitem1') != None:
                                                            f.write('\\begin{description}\n')
                                                            for Subitem1 in Item.findall('.//Subitem1'):
                                                                f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                                if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                    break
                                                                for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                    f.write(i)
                                                                f.write('\n')
                                                            f.write('\\end{description}\n')
                                                    f.write('\\end{description}\n')
                                        f.write('\\end{description}\n')
                        else:
                            for Article in Section.findall('Article'):
                                if Article.find('ArticleCaption') != None:
                                    for i in Article.find('ArticleCaption').itertext():
                                        f.write('\\noindent\\hspace{10pt}' + i + '\n')
                
                                para = 1
                                for Paragraph in Article.findall('Paragraph'):
                                    if len(Article.findall('Paragraph')) > 1:
                                        if para == 1:
                                            f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                            para += 1
                                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                break
                                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                break
                                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                            if Paragraph.find('.//Item') != None:
                                                f.write('\\begin{description}\n')
                                                for Item in Paragraph.findall('.//Item'):
                                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                        break
                                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                    if Item.find('.//Subitem1') != None:
                                                        f.write('\\begin{description}\n')
                                                        for Subitem1 in Item.findall('.//Subitem1'):
                                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                break
                                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                        f.write('\\end{description}\n')
                                                f.write('\\end{description}\n')
                                        else:
                                            f.write('\item[\\rensuji{' + str(para) + '}]')
                                            para += 1
                                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                break
                                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                                break
                                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                            if Paragraph.find('.//Item') != None:
                                                f.write('\\begin{description}\n')
                                                for Item in Paragraph.findall('.//Item'):
                                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                        break
                                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                    if Item.find('.//Subitem1') != None:
                                                        f.write('\\begin{description}\n')
                                                        for Subitem1 in Item.findall('.//Subitem1'):
                                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                                break
                                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                                f.write(i)
                                                            f.write('\n')
                                                        f.write('\\end{description}\n')
                                                f.write('\\end{description}\n')
                                    else:
                                        f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                        if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                                break
                                        if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                            break
                                        for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                            f.write(i)
                                        f.write('\n')
                                        if Paragraph.find('.//Item') != None:
                                            f.write('\\begin{description}\n')
                                            for Item in Paragraph.findall('.//Item'):
                                                f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                                if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                    break
                                                for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                    f.write(i)
                                                f.write('\n')
                                                if Item.find('.//Subitem1') != None:
                                                    f.write('\\begin{description}\n')
                                                    for Subitem1 in Item.findall('.//Subitem1'):
                                                        f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                        if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                            break
                                                        for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                            f.write(i)
                                                        f.write('\n')
                                                    f.write('\\end{description}\n')
                                            f.write('\\end{description}\n')
                                f.write('\\end{description}\n')
                else:
                    for Article in Chapter.findall('Article'):
                        if Article.find('ArticleCaption') != None:
                            for i in Article.find('ArticleCaption').itertext():
                                f.write('\\noindent\\hspace{10pt}' + i + '\n')
    
                        para = 1
                        for Paragraph in Article.findall('Paragraph'):
                            if len(Article.findall('Paragraph')) > 1:
                                if para == 1:
                                    f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                    para += 1
                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                        break
                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                        break
                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                        f.write(i)
                                    f.write('\n')
                                    if Paragraph.find('.//Item') != None:
                                        f.write('\\begin{description}\n')
                                        for Item in Paragraph.findall('.//Item'):
                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                break
                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                            if Item.find('.//Subitem1') != None:
                                                f.write('\\begin{description}\n')
                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                        break
                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                f.write('\\end{description}\n')
                                        f.write('\\end{description}\n')
                                else:
                                    f.write('\item[\\rensuji{' + str(para) + '}]')
                                    para += 1
                                    if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                        break
                                    if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                        break
                                    for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                        f.write(i)
                                    f.write('\n')
                                    if Paragraph.find('.//Item') != None:
                                        f.write('\\begin{description}\n')
                                        for Item in Paragraph.findall('.//Item'):
                                            f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                            if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                                break
                                            for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                            if Item.find('.//Subitem1') != None:
                                                f.write('\\begin{description}\n')
                                                for Subitem1 in Item.findall('.//Subitem1'):
                                                    f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                    if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                        break
                                                    for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                        f.write(i)
                                                    f.write('\n')
                                                f.write('\\end{description}\n')
                                        f.write('\\end{description}\n')
                            else:
                                f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                                if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                    break
                                if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                    break
                                for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                    f.write(i)
                                f.write('\n')
                                if Paragraph.find('.//Item') != None:
                                    f.write('\\begin{description}\n')
                                    for Item in Paragraph.findall('.//Item'):
                                        f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                        if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                            break
                                        for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                            f.write(i)
                                        f.write('\n')
                                        if Item.find('.//Subitem1') != None:
                                            f.write('\\begin{description}\n')
                                            for Subitem1 in Item.findall('.//Subitem1'):
                                                f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                                if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                    break
                                                for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                    f.write(i)
                                                f.write('\n')
                                            f.write('\\end{description}\n')
                                    f.write('\\end{description}\n')
                        f.write('\\end{description}\n')
        else:
            for Article in root.find('.//MainProvision').iter('Article'):
                if Article.find('ArticleCaption') != None:
                    for i in Article.find('ArticleCaption').itertext():
                        f.write('\\noindent\\hspace{10pt}' + i + '\n')
            
                para = 1
                for Paragraph in Article.findall('Paragraph'):
                    if len(Article.findall('Paragraph')) > 1:
                        if para == 1:
                            f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                            para += 1
                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                break
                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                break
                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                f.write(i)
                            f.write('\n')
                            if Paragraph.find('.//Item') != None:
                                f.write('\\begin{description}\n')
                                for Item in Paragraph.findall('.//Item'):
                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                        break
                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                        f.write(i)
                                    f.write('\n')
                                    if Item.find('.//Subitem1') != None:
                                        f.write('\\begin{description}\n')
                                        for Subitem1 in Item.findall('.//Subitem1'):
                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                break
                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                        f.write('\\end{description}\n')
                                f.write('\\end{description}\n')
                        else:
                            f.write('\item[\\rensuji{' + str(para) + '}]')
                            para += 1
                            if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                break
                            if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                                break
                            for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                                f.write(i)
                            f.write('\n')
                            if Paragraph.find('.//Item') != None:
                                f.write('\\begin{description}\n')
                                for Item in Paragraph.findall('.//Item'):
                                    f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                    if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                        break
                                    for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                        f.write(i)
                                    f.write('\n')
                                    if Item.find('.//Subitem1') != None:
                                        f.write('\\begin{description}\n')
                                        for Subitem1 in Item.findall('.//Subitem1'):
                                            f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                            if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                                break
                                            for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                                f.write(i)
                                            f.write('\n')
                                        f.write('\\end{description}\n')
                                f.write('\\end{description}\n')
                    else:
                        f.write('\\begin{description}\n\\item[' + Article.find('ArticleTitle').text + ']')
                        if Paragraph.find('ParagraphSentence').find('.//Sentence') == None:
                                break
                        if Paragraph.find('ParagraphSentence').find('.//Sentence').text == None:
                            break
                        for i in Paragraph.find('ParagraphSentence').find('.//Sentence').itertext():
                            f.write(i)
                        f.write('\n')
                        if Paragraph.find('.//Item') != None:
                            f.write('\\begin{description}\n')
                            for Item in Paragraph.findall('.//Item'):
                                f.write('\item[' + Item.find('.//ItemTitle').text + ']')
                                if Item.find('.//ItemSentence').find('.//Sentence') == None:
                                    break
                                for i in Item.find('.//ItemSentence').find('.//Sentence').itertext():
                                    f.write(i)
                                f.write('\n')
                                if Item.find('.//Subitem1') != None:
                                    f.write('\\begin{description}\n')
                                    for Subitem1 in Item.findall('.//Subitem1'):
                                        f.write('\item[' + Subitem1.find('Subitem1Title').text + ']')
                                        if Subitem1.find('.//Subitem1Sentence').find('.//Sentence') == None:
                                            break
                                        for i in Subitem1.find('.//Subitem1Sentence').find('.//Sentence').itertext():
                                            f.write(i)
                                        f.write('\n')
                                    f.write('\\end{description}\n')
                            f.write('\\end{description}\n')
                f.write('\\end{description}\n')
        f.write('\\end{document}\n')
        return Law_Name


def main():
    get_lawlist()
    Law_Name = search_get_LawContent()
    result = xml_to_tex(Law_Name)
    return result

if __name__ == '__main__':
    main()
