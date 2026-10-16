# -*- coding: utf-8 -*-
"""Дорожная карта Кати по образцу страницы Алёны + стиль кабинета. Запуск: python3 -I build2.py"""
import os, re, html, shutil, zipfile
from build import md2html, SRC, OUT

def read(name):
    p=os.path.join(SRC,name)
    return open(p,encoding='utf-8').read() if os.path.exists(p) else None

def first_phrase(md, header, n=1):
    m=re.search(re.escape(header)+r'.*?\n\s*'+str(n)+r'\.\s*(.+?)\n', md, re.S)
    return m.group(1).strip().strip('«»') if m else ''

HEAD='''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%s · Катя Мотив</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&family=DM+Sans:ital@1&display=swap">
<link rel="stylesheet" href="style.css"></head>
<body><div class="wrap">
<div class="top"><a class="logo" href="index.html"><img src="assets/logo.png" alt="MS"><span>maysoulme</span></a><span class="muted">личная работа</span></div>
'''
FOOT='''<div class="foot"><p class="muted">Личная работа с Майей · maysoulme. Материалы не для передачи третьим лицам.</p><span class="hand">Майя</span></div>
</div><script src="page.js"></script></body></html>'''

def shell(title, inner, back=True):
    return HEAD % html.escape(title) + ('<a class="back" href="index.html">← К дорожной карте</a>' if back else '') + inner + FOOT

def doc_block(f, title, lead):
    md=read(f)
    if not md: return ''
    return '<section class="docsec" id="%s"><h2>%s</h2><p class="lead">%s <a class="dl" href="docs/%s" download>скачать файл</a></p><div class="docbody">%s</div></section>' % (f[:2], title, lead, f, md2html(md))

STAGE_PAGES = {
 'data-stage.html': ('Распаковка и аудитория', 'Из этих двух документов выросло всё остальное: кто Катя и что у её людей болит.', [
    ('02_аудитория.md','Анализ аудитории','Кто покупает у Кати и что у них болит. Сначала короткая выжимка из пяти главных болей, потом всё целиком: 13 болей словами людей, желания, страхи, возражения, что можно обещать.'),
    ('01_распаковка.md','Распаковка','Всё о Кате в одном документе: кто, путь, метод, голос, темы, границы.')]),
 'product-stage.html': ('Кто ты, продукт и оффер', 'Три документа, которые отвечают на вопросы «кто я», «что продаю» и «как об этом сказать».', [
    ('05_позиционирование.md','Позиционирование: кто Катя и для кого','Одна страница, которую читают все остальные помощники. Проверка: фразу из первого раздела можно сказать вслух незнакомому человеку.'),
    ('03_продукт.md','Продукт «Денежный чекап»','Десять дней, восемь уроков, 1 290 ₽. Каждый урок закрывает одну боль, у каждого написано, что показать на экране. Внутри бонусы, тарифы, порядок запуска и сбор отзывов.'),
    ('04_оффер.md','Оффер: как рассказать о продукте, чтобы купили','Ответы на четыре вопроса покупательницы: что получу, почему получится у меня, как быстро, что от меня нужно. В конце короткие версии для шапки, закрепа, ролика и личных сообщений.')]),
 'packaging-stage.html': ('Упаковка блога', 'Всё, что человек видит, когда заходит в профиль, и куда он после этого проваливается.', [
    ('06_упаковка.md','Шапка, актуальные, первые посты, Telegram','Три шапки на выбор, четыре актуальных со сценариями сторис, девять постов для ленты, описание и закреп для Telegram, карта «куда ни ткни».')]),
 'telegram-stage.html': ('Telegram: план, посты, сторис', 'Что выходит каждый день и из чего это сделано.', [
    ('10_план_канала.md','План канала на месяц','Каждый день с 20 октября по 16 ноября: формат, цель, почти готовое начало. Две недели живой человек, потом истории, возражения и открытие продаж 9 ноября. Без «успей до».'),
    ('11_посты.md','Готовые посты','Три поста из плана, кружок и анонс подкаста.'),
    ('12_сторис.md','Сторис','План на неделю, большая серия с пользой на 27 сторис и серия для дня открытия продаж на 22 сторис.')]),
 'funnel-stage.html': ('Воронка: статья и бот', 'Как человек доходит от ролика до покупки без участия Кати.', [
    ('13_воронка.md','Продающая статья и сообщения для бота','План статьи, сама статья целиком и все сообщения бота: приветствие, выдача теста, напоминания, письма после, вопрос с кнопками и ответы.')]),
}

PAINS = [
 ('Деньги заканчиваются за неделю до зарплаты','Зарплата приходит каждый месяц, а за неделю до следующей денег уже нет, и непонятно, куда всё делось.','Продукт учит, что делать в день зарплаты: сначала перевести часть себе на отдельный счёт, потом тратить остальное.'),
 ('Не вижу, куда уходят деньги','Ничего крупного не покупала, а денег нет.','Бесплатный тест по слову ТЕСТ показывает утечки за 15 минут.'),
 ('Любая поломка это долг','Сломалась машина, чек 60 тысяч, и снова занимать.','Третий блок продукта: подушка, которую собираешь маленькими суммами незаметно для бюджета.'),
 ('Стыдно открывать приложение банка','С высшим образованием, а в деньгах как школьница.','Катя говорит сначала про чувство, потом про причину, потом даёт одно действие с цифрой. Без стыда и без лекций.'),
 ('Каждый месяц обещаю себе начать и не начинаю','«С этой зарплаты точно начну».','Первый шаг в вечер оплаты: автоперевод, который нельзя забыть.'),
]

def mat(kind, title, desc, href, label, dl=False):
    return '<div class="mat"><span class="mat__ico">%s</span><span class="mat__txt"><b>%s</b> — %s</span><a class="go" href="%s"%s>%s</a></div>' % (kind,title,desc,href,' download' if dl else '',label)

def stage(n, title, sub, status, mats, docs=None, open_=False, extra=''):
    st='<span class="stage__status st-now">● сейчас</span>' if status=='now' else '<span class="stage__status st-done">✓ готово</span>'
    body=''.join(mats)
    for f,t,l in (docs or []):
        md=read(f)
        if md: body+='<details class="doc"><summary>%s</summary><p class="muted">%s</p><div class="docbody">%s</div></details>' % (t,l,md2html(md))
    body+=extra
    return ('<details class="stage"%s><summary><span class="stage__num">%s</span><span class="stage__head"><span class="stage__title">%s</span><span class="stage__sub">%s</span></span>%s</summary>'
            '<div class="stage__body">%s</div></details>') % (' open' if open_ else '', n, title, sub, st, body)

def build():
    os.makedirs(os.path.join(OUT,'docs'),exist_ok=True); os.makedirs(os.path.join(OUT,'downloads'),exist_ok=True)
    for f in os.listdir(SRC):
        if f.endswith('.md') and not f.startswith('Катя_Мотив'):
            shutil.copy(os.path.join(SRC,f),os.path.join(OUT,'docs',f))
    pk=os.path.join(SRC,'14_пакет')
    if os.path.isdir(pk):
        os.makedirs(os.path.join(OUT,'docs','14_пакет'),exist_ok=True)
        for f in os.listdir(pk):
            if f.endswith('.md'): shutil.copy(os.path.join(pk,f),os.path.join(OUT,'docs','14_пакет',f))
    zp=os.path.join(OUT,'downloads','katya-full-package.zip')
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        for root,_,files in os.walk(os.path.join(OUT,'docs')):
            for f in files:
                if f.endswith('.md'): z.write(os.path.join(root,f),os.path.relpath(os.path.join(root,f),os.path.join(OUT,'docs')))
    for fn,(title,lead,docs) in STAGE_PAGES.items():
        inner='<span class="badge">Этап</span><h1>%s</h1><p class="lead">%s</p>' % (title,lead) + ''.join(doc_block(f,t,l) for f,t,l in docs)
        open(os.path.join(OUT,fn),'w',encoding='utf-8').write(shell(title,inner))
    items=[]
    if os.path.isdir(pk):
        for f in sorted(os.listdir(pk)):
            if not f.endswith('.md'): continue
            txt=open(os.path.join(pk,f),encoding='utf-8').read(); k='k%d'%len(items)
            items.append('<details class="doc kitdoc"><summary>%s</summary><div class="kitbar"><button class="btn" data-copy="%s">Скопировать помощника</button><a class="btn ghost" href="docs/14_пакет/%s" download>Скачать</a></div><textarea id="%s" hidden>%s</textarea><div class="docbody">%s</div></details>' % (html.escape(f[:-3].replace('_',' ')),k,f,k,html.escape(txt),md2html(txt)))
    kit_inner='<span class="badge">Этап</span><h1>Помощники Кати, <em>готовые к работе</em></h1><p class="lead">Каждый помощник уже знает Катю: внутри её паспорт, голос и правила письма. Открой нужного, нажми «Скопировать», вставь в новый чат Claude или ChatGPT и напиши команду из первой строки. Первым идёт паспорт, его читают все остальные.</p>'+''.join(items)
    open(os.path.join(OUT,'kit.html'),'w',encoding='utf-8').write(shell('Помощники Кати',kit_inner))
    off=read('04_оффер.md') or ''; off2=first_phrase(off,'## 1. Одной фразой',2)
    pains=''.join('<li><span class="n">%d</span><b>%s</b><p class="q">%s</p><p class="a">%s</p></li>' % (i+1,html.escape(t),html.escape(q),html.escape(a)) for i,(t,q,a) in enumerate(PAINS))
    SP=STAGE_PAGES
    stages=[
     stage(0,'Распаковка и аудитория','Кто Катя, как говорит, кто её люди и что у них болит.','done',
           [mat('WEB','Страница этапа','оба документа на отдельной странице','data-stage.html','открыть'),
            mat('MD','Распаковка','файл','docs/01_распаковка.md','скачать',True),
            mat('MD','Анализ аудитории','файл','docs/02_аудитория.md','скачать',True)], SP['data-stage.html'][2]),
     stage(1,'Кто ты, продукт и оффер','Позиционирование «Деньги с головой», «Денежный чекап» за 1 290 ₽ и оффер.','done',
           [mat('WEB','Страница этапа','три документа на отдельной странице','product-stage.html','открыть'),
            mat('MD','Позиционирование','файл','docs/05_позиционирование.md','скачать',True),
            mat('MD','Продукт','файл','docs/03_продукт.md','скачать',True),
            mat('MD','Оффер','файл','docs/04_оффер.md','скачать',True)], SP['product-stage.html'][2]),
     stage(2,'Упаковка блога','Шапка, четыре актуальных со сторис, девять постов, описание и закреп для Telegram.','done',
           [mat('WEB','Страница этапа','упаковка на отдельной странице','packaging-stage.html','открыть'),
            mat('MD','Упаковка','файл','docs/06_упаковка.md','скачать',True)], SP['packaging-stage.html'][2]),
     stage(3,'Telegram: план, посты, сторис','План канала на месяц, готовые посты, кружок, подкаст, сторис.','done',
           [mat('WEB','Страница этапа','план, посты и сторис на отдельной странице','telegram-stage.html','открыть'),
            mat('MD','План канала','файл','docs/10_план_канала.md','скачать',True),
            mat('MD','Посты','файл','docs/11_посты.md','скачать',True),
            mat('MD','Сторис','файл','docs/12_сторис.md','скачать',True)], SP['telegram-stage.html'][2]),
     stage(4,'Воронка: статья и бот','Бесплатный тест по слову ТЕСТ, продающая статья, сообщения бота.','done',
           [mat('WEB','Страница этапа','статья и бот на отдельной странице','funnel-stage.html','открыть'),
            mat('MD','Воронка','файл','docs/13_воронка.md','скачать',True)], SP['funnel-stage.html'][2]),
     stage(5,'Дизайн-отдел','Четыре дизайн-скилла для Claude Code: гайды, презентации, карусели. Ставятся одной командой, перекрашиваются под бренд.','now',
           [mat('WEB','Дизайн-отдел: установка и скиллы','гайд с кнопками «скачать» и «скопировать»','https://maysoulme.ru/design-skills/','открыть'),
            mat('MD','Что оформить первым','файл','docs/00_дизайн_отдел.md','скачать',True)], [('00_дизайн_отдел.md','Что оформить первым','Воркбук-тест, восемь презентаций к урокам, страница продукта, памятка «день зарплаты».')], open_=True),
     stage(6,'Помощники Кати','Пятнадцать помощников с данными Кати внутри. Работают в любой нейросети.','done',
           [mat('WEB','Страница помощников','каждый помощник с кнопкой «Скопировать»','kit.html','открыть'),
            mat('ZIP','Весь пакет','все документы и помощники одним архивом','downloads/katya-full-package.zip','скачать',True)]),
    ]
    qs=[]
    for fn in sorted(os.listdir(SRC)):
        if fn.startswith('00_отчёт'):
            t=open(os.path.join(SRC,fn),encoding='utf-8').read()
            m=re.search(r'##[^\n]*(не хватило|Чего не хватило|ждёт Катю|уточнить)[^\n]*\n(.*?)(?=\n## |\Z)',t,re.S|re.I)
            if m: qs.append(md2html(m.group(2)))
    ask=('<details class="stage"><summary><span class="stage__num">?</span><span class="stage__head"><span class="stage__title">Что спросить у Кати</span><span class="stage__sub">Чего нет в её файлах. В текстах на этих местах стоят пометки.</span></span><span class="stage__status st-now">● ждёт ответа</span></summary><div class="stage__body">%s</div></details>') % ''.join('<div class="hw">%s</div>' % q for q in qs)
    inner=('<div class="peach"><div class="hero"><div>'
      '<span class="hand">Катя</span><span class="badge">Личная работа · maysoulme</span>'
      '<h1>Дорожная карта: <em>система блога</em> Кати шаг за шагом</h1>'
      '<p class="lead">Все данные по порядку: кто ты, что продаёшь, как об этом говорить, что писать. Нажми на этап, внутри всё целиком.</p>'
      '<p class="meta">7 этапов · помощники под каждый шаг · все материалы в одном месте</p>'
      '</div><div class="photo"><img src="assets/katya.jpg" alt="Катя"></div></div></div>'
      '<div class="offer"><span class="k">Главное предложение</span><p>%s</p></div>'
      '<h2 class="h2">Пять болей, на которые всё отвечает</h2><ol class="pains">%s</ol>'
      ''
      '%s%s<div class="btns"><a class="btn" href="downloads/katya-full-package.zip" download>Весь пакет (zip)</a><a class="btn ghost" href="https://maysoulme.ru/design-skills/">Дизайн-отдел</a></div>') % (html.escape(off2), pains, ''.join(stages), ask)
    open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(shell('Дорожная карта',inner,back=False))
    print('built: index + %d stage pages + kit (%d helpers)' % (len(STAGE_PAGES), len(items)))

if __name__=='__main__':
    build()
