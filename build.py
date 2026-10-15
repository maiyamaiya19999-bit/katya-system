# -*- coding: utf-8 -*-
"""Собирает index.html страницы Кати из markdown-файлов в тест/катя. Запуск: python3 -I build.py"""
import re, html, os, json
SRC='/Users/majasebarsina/Desktop/клод/проекты/intensive-v2/тест/катя'
OUT=os.path.dirname(os.path.abspath(__file__))

def md2html(text):
    out=[]; lines=text.split('\n'); i=0; in_code=False; code=[]; para=[]; lst=None; table=None
    def flush_para():
        nonlocal para
        if para: out.append('<p>'+inline(' '.join(para))+'</p>'); para=[]
    def flush_list():
        nonlocal lst
        if lst: out.append('<%s>'%lst[0]+''.join('<li>'+inline(x)+'</li>' for x in lst[1])+'</%s>'%lst[0]); lst=None
    def flush_table():
        nonlocal table
        if table:
            head,rows=table[0],table[1:]
            out.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+inline(c)+'</th>' for c in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table></div>'); table=None
    def inline(s):
        s=html.escape(s,quote=False)
        s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
        s=re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)',r'<em>\1</em>',s)
        s=re.sub(r'_(.+?)_',r'<em>\1</em>',s)
        s=re.sub(r'`(.+?)`',r'<code>\1</code>',s)
        s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2" target="_blank" rel="noopener">\1</a>',s)
        return s
    while i<len(lines):
        ln=lines[i]
        if ln.strip().startswith('```'):
            flush_para(); flush_list(); flush_table()
            if in_code: out.append('<pre class="px">'+html.escape('\n'.join(code))+'</pre>'); code=[]; in_code=False
            else: in_code=True
            i+=1; continue
        if in_code: code.append(ln); i+=1; continue
        if ln.strip().startswith('|') and ln.strip().endswith('|'):
            flush_para(); flush_list()
            cells=[c.strip() for c in ln.strip().strip('|').split('|')]
            if all(re.fullmatch(r':?-{2,}:?',c) for c in cells): i+=1; continue
            table=(table or [])+[cells]; i+=1; continue
        else: flush_table()
        m=re.match(r'^(#{1,6})\s+(.*)',ln)
        if m:
            flush_para(); flush_list(); lvl=len(m.group(1)); t=inline(m.group(2))
            tag={1:'h2',2:'h3',3:'h4'}.get(lvl,'h4'); cls={'h2':' class="sub big"','h3':' class="sub"','h4':' class="sub small"'}[tag]
            out.append(f'<{tag}{cls}>{t}</{tag}>'); i+=1; continue
        m=re.match(r'^\s*([-*•▸]|\d+[.)])\s+(.*)',ln)
        if m:
            flush_para(); kind='ol' if m.group(1)[0].isdigit() else 'ul'
            if lst and lst[0]!=kind: flush_list()
            if not lst: lst=(kind,[])
            lst[1].append(m.group(2)); i+=1; continue
        if ln.strip()=='' : flush_para(); flush_list(); i+=1; continue
        if ln.strip()=='---': flush_para(); flush_list(); out.append('<hr>'); i+=1; continue
        if lst and ln.startswith('  '): lst[1][-1]+=' '+ln.strip(); i+=1; continue
        flush_list(); para.append(ln.strip()); i+=1
    flush_para(); flush_list(); flush_table()
    if in_code: out.append('<pre class="px">'+html.escape('\n'.join(code))+'</pre>')
    return '\n'.join(out)

def section(sid, num, title, lead, body_html, open_=False):
    return f'''<section id="{sid}"><h2 class="sec"><span>{num}</span>{title}</h2>{('<p class="lead">'+lead+'</p>') if lead else ''}
<details class="doc"{' open' if open_ else ''}><summary>Открыть документ целиком</summary><div class="docbody">{body_html}</div></details></section>'''

if __name__=='__main__':
    print(md2html(open(os.path.join(SRC,'02_аудитория.md'),encoding='utf-8').read())[:1500])

# ---------------- страница ----------------
CSS = open(os.path.join(OUT,'style.css'),encoding='utf-8').read() if os.path.exists(os.path.join(OUT,'style.css')) else ''

SECTIONS = [
 # (id, title, lead, file, open)
 ('pos','Кто Катя и для кого','Одна страница, которую читают все остальные помощники: позиция «середина» между хардкорными экспертами и обтекаемыми блогерами, три шага в каждой теме: чувство, почему так, один шаг с цифрой.','05_позиционирование.md',True),
 ('prod','Продукт «Денежный чекап»','Мини-продукт за 1 290 ₽: десять дней, восемь коротких уроков в четырёх блоках, каждый урок привязан к боли из анализа аудитории, десять бонусов и три тарифа. Первый урок открывается в день оплаты.','03_продукт.md',False),
 ('offer','Оффер и продающие тексты','Самый сильный оффер для чекапа: ответы на четыре вопроса покупателя, цена и что она значит, короткие версии для шапки, закрепа, ролика и личных сообщений.','04_оффер.md',False),
 ('pack','Упаковка профиля и канала','Шапка в трёх вариантах, четыре актуальных со сценариями сторис, девять стартовых постов, описание и закреп для Telegram, карта «куда ни ткни».','06_упаковка.md',False),
 ('topics','Темы на месяц и 50 идей','Тридцать тем по неделям из болей аудитории и пятьдесят идей для роликов с текстом в описании.','07_темы_и_идеи.md',False),
 ('reels','Три ролика целиком','Экспертный, короткая инструкция и личная история: первые три секунды, сценарий под суфлёр, заголовок на экране, описание, призыв, подсказка по съёмке.','08_ролики.md',False),
 ('car','Карусель','Девять слайдов по ролям и подпись под постом.','09_карусель.md',False),
 ('stories','Сторис','План недели, умная линия на 20–30 сторис и продающая линия для дня открытия продаж.','12_сторис.md',False),
 ('tgplan','Telegram: план месяца','План канала по дням с 20 октября по 16 ноября: две недели живой человек, потом кейсы, возражения и открытие продаж 9 ноября без единого «успей».','10_план_канала.md',False),
 ('tgposts','Telegram: посты','Три поста по заходам из плана, кружок и анонс подкаста.','11_посты.md',False),
 ('funnel','Воронка: статья и бот','План бесплатного материала, готовая продающая статья и все сообщения для бота: приветствие, выдача, напоминания, письма после, вопрос с кнопками.','13_воронка.md',False),
 ('unpack','Распаковка','Основа всего: кто она, путь, метод, голос, темы, границы. Собрана из её трёх файлов.','01_распаковка.md',False),
 ('aud','Анализ аудитории','Три группы на выбор, выбранная группа «зарплата есть, денег нет», одиннадцать разделов: боли, желания, решения, страхи, возражения, что можно обещать, как они говорят.','02_аудитория.md',False),
]

def read(name):
    p=os.path.join(SRC,name)
    return open(p,encoding='utf-8').read() if os.path.exists(p) else None

def first_phrase(md, header):
    m=re.search(re.escape(header)+r'.*?\n\s*\n?1\.\s*(.+?)\n', md, re.S)
    return m.group(1).strip().strip('«»') if m else ''

def build():
    os.makedirs(os.path.join(OUT,'docs'),exist_ok=True)
    pos=read('05_позиционирование.md') or ''; off=read('04_оффер.md') or ''
    pos1=first_phrase(pos,'## 1. Я одной фразой'); off2=''
    m=re.search(r'## 1\. Одной фразой.*?\n2\.\s*(.+?)\n',off,re.S); off2=m.group(1).strip() if m else ''
    toc=''.join(f'<li><a href="#{sid}">{t}</a></li>' for sid,t,_,f,_ in SECTIONS if read(f))
    body=[]
    n=0
    for sid,title,lead,f,op in SECTIONS:
        md=read(f)
        if not md: continue
        n+=1
        open(os.path.join(OUT,'docs',f),'w',encoding='utf-8').write(md)
        body.append(section(sid,'%02d'%n,title,lead+f' <a class="dl" href="docs/{f}" download>Скачать файл</a>',md2html(md),op))
    # пакет помощников
    pk=os.path.join(SRC,'14_пакет')
    if os.path.isdir(pk):
        n+=1; items=[]
        os.makedirs(os.path.join(OUT,'docs','14_пакет'),exist_ok=True)
        for fn in sorted(os.listdir(pk)):
            if not fn.endswith('.md'): continue
            txt=open(os.path.join(pk,fn),encoding='utf-8').read()
            open(os.path.join(OUT,'docs','14_пакет',fn),'w',encoding='utf-8').write(txt)
            items.append(f'<details class="doc"><summary>{html.escape(fn[:-3].replace("_"," "))} <a class="dl" href="docs/14_пакет/{fn}" download>скачать</a></summary><div class="docbody">{md2html(txt)}</div></details>')
        body.append(f'<section id="kit"><h2 class="sec"><span>{n:02d}</span>Пакет помощников</h2><p class="lead">Каждый помощник с данными Кати внутри. Открой, скопируй целиком, вставь в новый чат Claude или ChatGPT и напиши команду из первой строки.</p>{"".join(items)}</section>')
    # что уточнить у Кати: из отчётов
    qs=[]
    for fn in sorted(os.listdir(SRC)):
        if fn.startswith('00_отчёт'):
            t=open(os.path.join(SRC,fn),encoding='utf-8').read()
            m=re.search(r'##[^\n]*(не хватило|Чего не хватило|ждёт Катю|уточнить)[^\n]*\n(.*?)(?=\n## |\Z)',t,re.S|re.I)
            if m: qs.append(md2html(m.group(2)))
    if qs:
        n+=1
        body.append(f'<section id="ask"><h2 class="sec"><span>{n:02d}</span>Что уточнить у Кати</h2><p class="lead">Всё, что помощники не нашли в её файлах и оставили пометками. Это короткий список вопросов, после которых тексты можно публиковать.</p>'+''.join(f'<div class="highlight">{q}</div>' for q in qs)+'</section>')
    page=f'''<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="robots" content="noindex, nofollow"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Катя Мотив · система блога</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600;700&family=DM+Sans:ital@1&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<nav class="nav"><b>Катя Мотив</b><span>maysoulme · система блога</span></nav>
<div class="container">
<section class="hero">
<div class="badge">Тест системы · первый пользователь</div>
<div class="herogrid"><div>
<h1>Система блога Кати: <em>деньги с головой</em></h1>
<p class="desc">{html.escape(pos1)}</p>
<p class="meta">экспертный блог · telegram-канал · «денежный чекап» 1 290 ₽</p>
</div><div class="photo"><img src="assets/katya.jpg" alt="Катя"></div></div>
</section>
<div class="intro-bold">{html.escape(off2)}</div>
<p class="intro-text">Всё на этой странице собрано помощниками кабинета из трёх файлов Кати: распаковка, анализ аудитории, продукт, оффер, позиционирование, упаковка, контент, Telegram, воронка и пакет помощников с её данными внутри. Ничего не придумано: цифры и факты только её, а там, где данных не хватило, стоят пометки.</p>
<div class="toc"><div class="tt">Содержание</div><ol>{toc}<li><a href="#kit">Пакет помощников</a></li><li><a href="#ask">Что уточнить у Кати</a></li></ol></div>
{''.join(body)}
<div class="footer">Кабинет интенсива «ИИ-команда для блога» · maysoulme · собрано {__import__('datetime').date.today().strftime('%d.%m.%Y')}</div>
</div></body></html>'''
    open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(page)
    print('built, sections:',n,'size',len(page))

if __name__=='__main__':
    build()
