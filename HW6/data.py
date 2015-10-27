__author__ = 'yixing'

import random
from sklearn import linear_model
from sklearn import svm
from sklearn import tree
import operator

FILE_PATH = '/Users/yixing/Documents/CS6200/Homework6/result/'
QREL_PATH = '/Users/yixing/Documents/CS6200/Homework6/qrels.adhoc.51-100.AP89.txt'
QUERY_PATH = '/Users/yixing/Documents/CS6200/Homework6/query_desc.51-100.short.txt'
RESULT_PATH = '/Users/yixing/Documents/CS6200/Homework6/performance/'
BM25 = 'bm25'
LMJM = 'lmjm'
LMLA = 'lmlaplace'
OK = 'okapitf'
TF = 'tfidf'
FEATURE_LIST = [TF, OK, BM25, LMJM, LMLA]

feature_map = {}
label_map = {}
QUERY_LIST = []
TRAIN_QUERY = []
TEST_QUERY = []
QUERY_DOC_LIST = []
train_feature_matrix = []
test_feature_matrix = []
train_label_vector = []
test_label_vector = []
train_index = []
test_index = []


def readfile_to_map():
    for feature in FEATURE_LIST:
        print "This process feature is:", feature
        path = FILE_PATH + feature
        fh = open(path, "r")
        for line in fh.readlines():
            query_id, _, doc_id, _, score, _ = line.split()
            score = float(score)
            if (query_id, doc_id) in label_map:
                if (query_id, doc_id) not in feature_map:
                    feature_map[(query_id, doc_id)] = {feature:score}
                else:
                    feature_map[(query_id,doc_id)][feature] = score
        fh.close()
    print "The feature map leangth is:", len(feature_map)

def readqrel_to_map():
    fh = open(QREL_PATH, "r")
    for line in fh.readlines():
        query_id, _, doc_id, grade = line.split()
        if query_id in QUERY_LIST:
            label_map[(query_id, doc_id)] = int(grade)
    print "The label map length is:", len(label_map)
    fh.close()

def random_split_set():
    global TRAIN_QUERY
    global TEST_QUERY
    TRAIN_QUERY = random.sample(QUERY_LIST, 20)
    TEST_QUERY = list(set(QUERY_LIST) - set(TRAIN_QUERY))
    # print "The train set is:", TRAIN_QUERY
    # print "The test set is:", TEST_QUERY

def get_query_list():
    fh = open(QUERY_PATH, "r")
    for line in fh.readlines():
        query_id = line.split(".")[0]
        if query_id not in QUERY_LIST:
            QUERY_LIST.append(query_id)
    print "The query list length is:", len(QUERY_LIST)
    random_split_set()
    fh.close()


def build_feature_label_matrix():
    # print "The train query list is:", TRAIN_QUERY
    # print "The test query list is:", TEST_QUERY
    for pairs in sorted(feature_map.keys()):
        query_id = pairs[0]
        # print "The query id is:", type(query_id)
        tmp_feature = feature_map[pairs]
        feature_vector = []
        grade = label_map[pairs]
        for feature in FEATURE_LIST:
            if feature in tmp_feature:
                feature_vector.append(tmp_feature[feature])
            else:
                feature_vector.append(0)
        # print "The feature vector is:", feature_vector
        if query_id in TRAIN_QUERY:
            train_index.append(pairs)
            # print "The train index is:", train_index
            train_feature_matrix.append(feature_vector)
            train_label_vector.append(grade)
        elif query_id in TEST_QUERY:
            test_index.append(pairs)
            # print "The test index is:", test_index
            test_feature_matrix.append(feature_vector)
            test_label_vector.append(grade)
    # print "The train feature matrix length is:", len(train_feature_matrix)
    # print "The train label length is:", len(train_label_vector)
    # print "The train index length is:", len(train_index)
    # print "The test feature matrix length is:", len(test_feature_matrix)
    # print "The test label length is:", len(test_label_vector)
    # print "The test index length is:", len(test_index)

def run_machinelearning_model():
    linear_regression()
    decision_tree()
    support_vector_machine()

def linear_regression():
    clf = linear_model.LinearRegression()
    clf.fit(train_feature_matrix, train_label_vector)
    train_result = clf.predict(train_feature_matrix)
    # print train_result
    test_result = clf.predict(test_feature_matrix)
    # print test_result
    train_result_map, test_result_map = analyse_result(train_result, test_result)
    write_to_file(train_result_map, "linear_regression_train_performance")
    write_to_file(test_result_map, "linear_regression_test_performance")

def decision_tree():
    clf = tree.DecisionTreeClassifier()
    clf.fit(train_feature_matrix,train_label_vector)
    train_result = clf.predict(train_feature_matrix)
    test_result = clf.predict(test_feature_matrix)
    train_result_map, test_result_map = analyse_result(train_result, test_result)
    write_to_file(train_result_map, "decision_tree_train_performance")
    write_to_file(test_result_map, "decision_tree_test_performance")

def support_vector_machine():
    clf = svm.SVC()
    clf.fit(train_feature_matrix,train_label_vector)
    train_result = clf.predict(train_feature_matrix)
    test_result = clf.predict(test_feature_matrix)
    train_result_map, test_result_map = analyse_result(train_result, test_result)
    write_to_file(train_result_map, "svm_train_performance")
    write_to_file(test_result_map, "svm_test_performance")

def analyse_result(raw_train_result, raw_test_result):
    train_result = {}
    test_result = {}
    for i in range(len(raw_train_result)):
        pairs = train_index[i]
        query_id = pairs[0]
        doc_id = pairs[1]
        score = raw_train_result[i]
        if query_id not in train_result:
            train_result[query_id] = {doc_id: score}
        else:
            train_result[query_id][doc_id] = score
    for i in range(len(raw_test_result)):
        pairs = test_index[i]
        query_id = pairs[0]
        doc_id = pairs[1]
        score = raw_test_result[i]
        if query_id not in test_result:
            test_result[query_id] = {doc_id: score}
        else:
            test_result[query_id][doc_id] = score
    print train_result, test_result
    return train_result, test_result


def write_to_file(result_map, filename):
    outpath = RESULT_PATH + filename
    fh = open(outpath, "w")
    for query_id in result_map:
        result = result_map[query_id]
        # print result
        sorted_result = sorted(result.items(), key=operator.itemgetter(1), reverse = True)
        # print sorted_result
        count = 1
        for element in sorted_result:
            if count <= 1000:
                fh.write('%s Q0 %s %d %f Exp\n'%(query_id, element[0], count, element[1]))
                count+= 1
            else:
                break
    fh.close()

def main():
    get_query_list()
    print "The train query list is:", TRAIN_QUERY
    print "The test query list is:", TEST_QUERY
    readqrel_to_map()
    readfile_to_map()
    build_feature_label_matrix()
    print "The train feature matrix length is:", len(train_feature_matrix)
    print "The train label length is:", len(train_label_vector)
    print "The train index length is:", len(train_index)
    print "The test feature matrix length is:", len(test_feature_matrix)
    print "The test label length is:", len(test_label_vector)
    print "The test index length is:", len(test_index)
    # print test_feature_matrix
    # print test_label_vector
    run_machinelearning_model()





if __name__=='__main__':
    main()
