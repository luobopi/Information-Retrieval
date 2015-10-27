__author__ = 'yixing'

from elasticsearch import Elasticsearch
from sklearn import tree
import string
import operator

LABEL_PATH = '/Users/yixing/Documents/trec07p/full/index'
RESULT_PATH = '/Users/yixing/Documents/CS6200/Homework7/result'
ngrams_list = ['free', 'win', 'porn', 'sex', 'viagra','erect','long','click']
train_label_vector = []
test_label_vector = []
train_feature_matrix = []
test_feature_matrix = []
train_set = set()
test_set = set()
train_index = []
test_index = []
label_map = {}
feature_map = {}
train_result = {}
test_result = {}


INDEX = 'spam'
DOC_TYPE = 'document'


def read_label_to_map():
    fh = open(LABEL_PATH, "r")
    for line in fh.readlines():
        new_line = string.strip(line, '\n')
        # print new_line
        [label, path] = new_line.split(' ')
        doc_id = path.split('/')[-1]
        # print doc_id, label
        if label == 'spam':
            grade = 1
        else:
            grade = 0
        label_map[doc_id] = grade

def build_feature_map(es):
    for gram in ngrams_list:
        print "Now query", gram, "in elasticsearch"
        query={
          "fields":"class",
          "query": {
            "function_score": {
              "query": {
                "term": {
                  "text": gram
                }
              },
              "functions": [
                {
                  "script_score": {
                    "lang": "groovy",
                    "script_file": "tf-score",
                    "params": {
                      "term": gram,
                      "field": "text"
                    }
                  }
                }
              ],
              "boost_mode": "replace"
            }
          }
        }

        resp = es.search(index=INDEX, doc_type=DOC_TYPE,body=query, explain=False, scroll="100m",size=100)
        scrollId= resp['_scroll_id']
        total_number = resp['hits']['total']
        print "The total number is:", total_number
        while True:
            if resp is None:
                print "resp none"
                break
            for i in resp['hits']['hits']:
                tf = i['_score']
                # print tf
                doc_id = i['_id']
                # print doc_id
                class_set = i['fields']['class'][0]
                # print tf, doc_id, class_set
                if class_set == 'train':
                    train_set.add(doc_id)
                else:
                    test_set.add(doc_id)
                if doc_id not in feature_map:
                    feature_map[doc_id] = {gram: tf}
                else:
                    feature_map[doc_id][gram] = tf
            resp = es.scroll(scroll_id = scrollId, scroll='1000ms')
            if len(resp['hits']['hits']) > 0:
                # print len(resp['hits']['hits'])
                scrollId = resp['_scroll_id']
            else:
                break

def build_feature_matrix():
    for doc_id in feature_map:
        map = feature_map[doc_id]
        vector = []
        label = label_map[doc_id]
        for word in ngrams_list:
            if word in map:
                vector.append(map[word])
            else:
                vector.append(0)
        if doc_id in train_set:
            train_index.append(doc_id)
            train_feature_matrix.append(vector)
            train_label_vector.append(label)
        elif doc_id in test_set:
            test_index.append(doc_id)
            test_feature_matrix.append(vector)
            test_label_vector.append(label)
    print "The train feature length is:", len(train_feature_matrix)
    print "The train label length is:", len(train_label_vector)
    print "The train index length is:", len(train_index)
    print "The train set length is:", len(train_set)
    print "The test feature length is:", len(test_feature_matrix)
    print "The test label length is:", len(test_label_vector)
    print "The test index length is:", len(test_index)
    print "The test set length is:", len(test_set)

def decision_tree_model():
    clf = tree.DecisionTreeClassifier()
    clf.fit(train_feature_matrix,train_label_vector)
    train_result = clf.predict(train_feature_matrix)
    test_result = clf.predict(test_feature_matrix)
    train_result_map, test_result_map = analyse_result(train_result, test_result)
    write_to_file(train_result_map, "decision_tree_train_performance")
    write_to_file(test_result_map, "decision_tree_test_performance")

def analyse_result(raw_train_result, raw_test_result):
    train_result = {}
    test_result = {}
    train_accuracy = 0
    test_accuracy = 0
    for i in range(len(raw_train_result)):
        doc_id = train_index[i]
        score = raw_train_result[i]
        train_result[doc_id] = score
        if int(score) == int(label_map[doc_id]):
            train_accuracy += 1
    train_acc = float(train_accuracy) / len(train_index)
    for i in range(len(raw_test_result)):
        doc_id = test_index[i]
        score = raw_test_result[i]
        test_result[doc_id] = score
        if int(score) == int(label_map[doc_id]):
            test_accuracy += 1
    test_acc = float(test_accuracy) / len(test_index)
    print "The train correct number is:", train_accuracy
    print "The test correct number is:", test_accuracy
    print "The train set accuracy is:", train_acc
    print "The test set accuracy is:", test_acc
    # print train_result, test_result
    return train_result, test_result

def write_to_file(result_map, filename):
    outpath = RESULT_PATH + '/' + filename
    fh = open(outpath, "w")
    sorted_result = sorted(result_map.items(), key=operator.itemgetter(1), reverse = True)
    count = 1
    for pair in sorted_result:
        fh.write('%s %d %f Exp\n'%(pair[0], count, pair[1]))
        count += 1
    fh.close()


def main():
    read_label_to_map()
    es = Elasticsearch()
    build_feature_map(es)
    build_feature_matrix()
    decision_tree_model()

if __name__ == '__main__':
    main()