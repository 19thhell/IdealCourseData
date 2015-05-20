import json
import pickle
import re
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer('english')
total_info = json.load(open('total.json'))
stopwords = pickle.load(open('../stopwords.pickle'))
tftable = {}
idftable = {}
tftable_desc = {}
idftable_desc = {}
unique = set()
start = 0
end = len(total_info)
total_num = 0
total_len = 0
total_fail = 0
new_info = []
skip = 0
rest = 0
print len(total_info)
for i in range(len(total_info)):
    cur_info = total_info[i]
    cur_info['title_bag'] = cur_info['title'].split()
    digit = 0
    while digit < len(cur_info['title_bag']):
        if not cur_info['title_bag'][digit].isdigit():
            break
        digit += 1
    cur_info['title_bag'] = cur_info['title_bag'][digit : ]
    cur_info['title'] = ' '.join(cur_info['title_bag'])
    key = (cur_info['title'], cur_info['department'], cur_info['school'])
    if key in unique:
        skip += 1
        print i, 'skip'
        continue
    else:
        unique.add(key)
    cur_info['school_bag'] = {}
    for word in cur_info['school'].split():
        word = word.lower()
        word = stemmer.stem(word)
        cur_info['school_bag'][word] = 1
    cur_info['department_bag'] = {}
    for word in cur_info['department'].split()[ : -1]:
        word = word.lower()
        word = stemmer.stem(word)
        cur_info['department_bag'][word] = 1
    for j in range(len(cur_info['title_bag'])):
        word = cur_info['title_bag'][j]
        word = word.lower()
        word = stemmer.stem(word)
        cur_info['title_bag'][j] = word
    desc_words = re.split('\W', cur_info['description'])
    cur_info['description_bag'] = {}
    cur_info['supplement_bag'] = {}
    for word in desc_words:
        if word.isalpha():
            word = word.lower()
            if word in stopwords:
                continue
            word = stemmer.stem(word)
            if word not in cur_info['description_bag']:
                cur_info['description_bag'][word] = 0
            cur_info['description_bag'][word] += 1
            if word not in tftable_desc:
                tftable_desc[word] = {}
                idftable_desc[word] = 0
            if i not in tftable_desc[word]:
                tftable_desc[word][i] = 0
            if tftable_desc[word][i] == 0:
                idftable_desc[word] += 1
            tftable_desc[word][i] += 1
    filename = 'jsons/items_' + str(i) + '.json'
    try:
        if i >= end:
            print i, 'empty'
            rest += 1
            new_info.append(cur_info)
            continue
        info = json.load(open(filename))[0]
        word_num = 0
        for j in range(len(info['detail'])):
            content = info['detail'][j]['content'].split()
            for word in content:
                word = word.strip(' \r\n')
                if word.isalpha():
                    word = word.lower()
                    if word == 'obj':
                        break
                    if word in stopwords:
                        continue
                    word = stemmer.stem(word)
                    if word not in cur_info['supplement_bag']:
                        cur_info['supplement_bag'][word] = 0
                    cur_info['supplement_bag'][word] += 1
                    if word not in tftable:
                        tftable[word] = {}
                        idftable[word] = 0
                    if i not in tftable[word]:
                        tftable[word][i] = 0
                    if tftable[word][i] == 0:
                        idftable[word] += 1
                    tftable[word][i] += 1
                    word_num += 1
                    total_len += len(word)
        print i, word_num
        new_info.append(cur_info)
        total_num += word_num
    except ValueError:
        print i, 'fail'
        total_fail += 1
print 'Average word length: ', total_len * 1.0 / total_num
print 'Average word number: ', total_num * 1.0 / (end - start)
print 'Percentage failure: ', total_fail * 1.0 / (end - start)
print 'Percentage skipped: ', skip * 1.0 / (end - start)
print 'Total courses: ', len(new_info)
print 'Supplemented: ', len(new_info) - rest
print 'Unique words in description: ', len(tftable_desc)
print 'Unique words in supplement: ', len(tftable)
json.dump(new_info, open('../extend.json', 'w'))
pickle.dump(idftable, open('../idftable.pickle', 'w'))
pickle.dump(idftable_desc, open('../idftable_desc.pickle', 'w'))
