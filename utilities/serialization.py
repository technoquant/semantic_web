import pickle


def pickle_knowledge_graph(g, filename):
    output_file = open(filename, 'wb')
    pickle.dump(g, output_file)
    output_file.close()


def unpickle_knowledge_graph(filename):
    input_file = open(filename, 'rb')
    g = pickle.load(input_file)
    input_file.close()
    return g
