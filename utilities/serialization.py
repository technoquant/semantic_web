import pickle


def serialize(graph, filename):
    """
    Serialize a graph to a file via pickle.
    :param graph: graph
    :param filename: filename
    :return: None
    """
    output_file = open(filename, 'wb')
    pickle.dump(graph, output_file)
    output_file.close()


def deserialize(filename):
    """
    Deserialize a file to a graph via pickle.
    :param filename: filename
    :return: graph
    """
    input_file = open(filename, 'rb')
    graph = pickle.load(input_file)
    input_file.close()
    return graph
