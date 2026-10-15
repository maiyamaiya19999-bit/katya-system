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
CSS = open(os.path.join(OUT,'style.css'),encoding='utf-8').read()

# (id, заголовок, что это простыми словами, что с этим делать, файл, открыт ли)
SECTIONS = [
 ('pos','Кто Катя и для кого','Одна страница: кто Катя, для кого её блог, чем она отличается. Её читают все остальные помощники, поэтому шапка, ролики и посты говорят об одном и том же.','Прочитать, сказать вслух фразу из первого раздела. Если не стыдно, всё верно.','05_позиционирование.md',True),
 ('prod','Продукт «Денежный чекап»','Что Катя продаёт: десять дней, восемь коротких уроков, 1 290 ₽. Каждый урок закрывает одну боль из списка выше. Внутри бонусы, цены и порядок запуска.','Проверить цены второго и третьего тарифа, они стоят как ориентир. Решить, оставлять ли урок про инвестиции.','03_продукт.md',False),
 ('offer','Как рассказать о продукте, чтобы купили','Оффер. Это ответы на четыре вопроса покупательницы: что получу, почему получится у меня, как быстро, что от меня нужно. Плюс короткие версии для шапки, закрепа, ролика и личных сообщений.','Взять короткие версии и поставить в профиль. Длинную взять за основу продающего поста.','04_оффер.md',False),
 ('pack','Профиль: шапка, актуальные, первые посты','Всё, что человек видит, когда заходит в профиль: три шапки на выбор, четыре актуальных со сценариями сторис, девять постов для ленты, описание и закреп для Telegram.','Вставить шапку. Снять актуальное «Кто я» по сценарию. Выложить пост «Давай знакомиться», он готов целиком.','06_упаковка.md',False),
 ('topics','О чём снимать: темы на месяц и 50 идей','Тридцать тем по неделям и пятьдесят идей для роликов с текстом в описании. Все из болей аудитории.','Выбрать темы на ближайшую неделю, остальные в запас.','07_темы_и_идеи.md',False),
 ('reels','Три ролика, готовых к съёмке','Полные сценарии: что сказать в кадре, что написать на экране, что написать в описании, как снимать.','Прочитать вслух с таймером. Снять в один съёмочный день.','08_ролики.md',False),
 ('car','Карусель','Пост из девяти картинок про то, куда уходят деньги, когда зарплата приходит каждый месяц, а их всё равно нет. Текст по слайдам и подпись.','Собрать картинки по памятке из кабинета, выложить как пост.','09_карусель.md',False),
 ('stories','Сторис','План на неделю, одна большая серия с пользой на 27 сторис и серия для дня открытия продаж на 22 сторис. У каждой сторис написано, что снять и что написать.','Снимать по плану, 10–15 минут в день.','12_сторис.md',False),
 ('tgplan','Telegram: план на месяц','Что выходит в канале каждый день с 20 октября по 16 ноября. Две недели просто живой человек, потом истории, возражения и открытие продаж 9 ноября. Без «успей до».','Каждое утро открыть нужный день и отдать его Копирайтеру.','10_план_канала.md',False),
 ('tgposts','Telegram: готовые посты','Три поста из плана, кружок и анонс подкаста. Можно выкладывать.','Выложить по плану.','11_посты.md',False),
 ('funnel','Воронка: статья и бот','Как человек доходит от ролика до покупки. Готовая продающая статья и все сообщения для бота: приветствие, выдача теста, напоминания, письма после, вопрос с кнопками.','Поставить тексты в бот. Статью опубликовать в Teletype.','13_воронка.md',False),
 ('unpack','Распаковка','Всё о Кате в одном документе: кто, путь, метод, голос, темы, границы. Из этого выросло всё остальное.','Прочитать и поправить, если что-то не так. Это основа.','01_распаковка.md',False),
 ('aud','Анализ аудитории целиком','Кто покупает у Кати и что у них болит: 13 болей словами самих людей, желания, страхи, возражения и что можно обещать.','Прочитать боли. Если «да, мне так и пишут», всё верно.','02_аудитория.md',False),
]

PAINS = [
 ('Деньги заканчиваются за неделю до зарплаты','«Зарплата приходит каждый месяц, а за неделю до следующей денег уже нет, и я не понимаю, куда всё делось»','Продукт учит, что делать в день зарплаты: сначала перевести часть себе на отдельный счёт, потом тратить остальное. Об этом первый ролик и большая серия сторис.','prod','Продукт'),
 ('Не вижу, куда уходят деньги','«Ничего крупного не покупала, а денег нет»','Бесплатный тест по слову ТЕСТ показывает утечки за 15 минут. Про это карусель и статья в воронке.','funnel','Воронка'),
 ('Любая поломка это долг','«Сломалась машина, чек 60 тысяч, и я опять занимаю»','Третий блок продукта: подушка, которую собираешь незаметно для бюджета.','prod','Продукт'),
 ('Стыдно открывать приложение банка','«Я с высшим образованием, а в деньгах как школьница»','Всё позиционирование Кати про это: сначала почему стыдно, потом одно действие с цифрой.','pos','Кто Катя'),
 ('Каждый месяц обещаю себе начать и не начинаю','«С этой зарплаты точно начну»','Оффер обещает честно: оплатила сегодня, вечером уже первый шаг.','offer','Оффер'),
]

def read(name):
    p=os.path.join(SRC,name)
    return open(p,encoding='utf-8').read() if os.path.exists(p) else None

def first_phrase(md, header, n=1):
    m=re.search(re.escape(header)+r'.*?\n\s*'+str(n)+r'\.\s*(.+?)\n', md, re.S)
    return m.group(1).strip().strip('«»') if m else ''

def build():
    os.makedirs(os.path.join(OUT,'docs'),exist_ok=True)
    pos=read('05_позиционирование.md') or ''; off=read('04_оффер.md') or ''
    pos1=first_phrase(pos,'## 1. Я одной фразой',1); off2=first_phrase(off,'## 1. Одной фразой',2)
    body=[]; n=0
    pains=''.join(f'<li><span class="n">{i+1}</span><b>{html.escape(t)}</b><p class="q">{html.escape(q)}</p><p class="a">{html.escape(a)} <a href="#{sid}">{html.escape(lbl)} →</a></p></li>' for i,(t,q,a,sid,lbl) in enumerate(PAINS))
    for sid,title,what,do,f,op in SECTIONS:
        md=read(f)
        if not md: continue
        n+=1
        open(os.path.join(OUT,'docs',f),'w',encoding='utf-8').write(md)
        body.append(f'<section class="sec" id="{sid}"><span class="num">{n:02d}</span><h2>{title}</h2><p class="what"><b>Что это.</b> {what}</p><p class="what"><b>Что делать.</b> {do}</p><p class="st">✓ готово · <a class="dl" href="docs/{f}" download>скачать</a></p><details class="doc"{" open" if op else ""}><summary>Весь документ</summary><div class="docbody">{md2html(md)}</div></details></section>')
    pk=os.path.join(SRC,'14_пакет')
    if os.path.isdir(pk):
        n+=1; items=[]
        os.makedirs(os.path.join(OUT,'docs','14_пакет'),exist_ok=True)
        for fn in sorted(os.listdir(pk)):
            if not fn.endswith('.md'): continue
            txt=open(os.path.join(pk,fn),encoding='utf-8').read()
            open(os.path.join(OUT,'docs','14_пакет',fn),'w',encoding='utf-8').write(txt)
            items.append(f'<details class="doc"><summary>{html.escape(fn[:-3].replace("_"," "))} <a class="dl" href="docs/14_пакет/{fn}" download>скачать</a></summary><div class="docbody">{md2html(txt)}</div></details>')
        body.append(f'<section class="sec kit" id="kit"><span class="num">{n:02d}</span><h2>Помощники Кати, готовые к работе</h2><p class="what"><b>Что это.</b> Каждый помощник с данными Кати внутри. Это и есть её ИИ-команда: сценарист, упаковщик, копирайтер и остальные.</p><p class="what"><b>Что делать.</b> Открыть нужного, скопировать целиком, вставить в новый чат Claude или ChatGPT, написать команду из первой строки.</p>{"".join(items)}</section>')
    qs=[]
    for fn in sorted(os.listdir(SRC)):
        if fn.startswith('00_отчёт'):
            t=open(os.path.join(SRC,fn),encoding='utf-8').read()
            m=re.search(r'##[^\n]*(не хватило|Чего не хватило|ждёт Катю|уточнить)[^\n]*\n(.*?)(?=\n## |\Z)',t,re.S|re.I)
            if m: qs.append(md2html(m.group(2)))
    if qs:
        n+=1
        body.append(f'<section class="sec" id="ask"><span class="num">{n:02d}</span><h2>Что спросить у Кати</h2><p class="what"><b>Что это.</b> Всё, чего помощники не нашли в её файлах. В текстах на этих местах стоят пометки.</p><p class="what"><b>Что делать.</b> Задать Кате эти вопросы, вписать ответы, и тексты можно публиковать.</p>'+''.join(f'<div class="note">{q}</div>' for q in qs)+'</section>')
    toc=''.join(f'<li><a href="#{sid}">{t}</a></li>' for sid,t,_,_,f,_ in SECTIONS if read(f))+'<li><a href="#kit">Помощники Кати</a></li><li><a href="#ask">Что спросить у Кати</a></li>'
    page=f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Катя Мотив · система блога</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&family=DM+Sans:ital@1&display=swap">
<style>{CSS}</style></head>
<body><div class="wrap">
<div class="top"><a class="logo" href="#"><img src="assets/logo.png" alt="MS"><span>maysoulme</span></a><span class="muted">система блога</span></div>

<div class="peach"><div class="hero"><div>
<span class="hand">Катя</span>
<h1>Блог Кати, собранный <em>целиком</em></h1>
<p class="lead">Здесь всё, что нужно, чтобы вести блог и продавать: кто ты, для кого, что продаёшь, как об этом говорить, что снимать и что писать. Каждый пункт уже готов.</p>
<p class="meta">экспертный блог про деньги · telegram-канал · продукт за 1 290 ₽</p>
</div><div class="photo"><img src="assets/katya.jpg" alt="Катя"></div></div></div>

<div class="offer"><span class="k">Главное предложение</span><p>{html.escape(off2)}</p></div>

<div class="how">
<div><b>Что болит у её людей</b><span>Пять самых сильных болей из анализа. Под каждой написано, что с ней делает система.</span></div>
<div><b>Что готово</b><span>Пятнадцать разделов ниже. В каждом: что это, что делать и весь документ.</span></div>
<div><b>Что осталось</b><span>Ответить на вопросы из последнего раздела и выложить.</span></div>
</div>

<h2>Пять болей, на которые всё отвечает</h2>
<ol class="pains">{pains}</ol>

<div class="note"><p><b>Как читать страницу.</b> Сверху вниз, как путь ученицы: сначала кто она и что продаёт, потом профиль, потом контент, потом Telegram и воронка. В конце помощники, которые будут делать всё это дальше, и вопросы Кате.</p></div>

<div class="box"><b>Содержание</b><ol class="toc">{toc}</ol></div>

{"".join(body)}

<div class="foot"><p class="muted">Кабинет интенсива «ИИ-команда для блога». Собрано помощниками из трёх файлов Кати. Ничего не придумано: цифры только её, где данных не хватило, стоят пометки.</p><span class="hand">Майя</span></div>
</div></body></html>'''
    open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(page)
    print('built, sections:',n,'size',len(page))

if __name__=='__main__':
    build()
