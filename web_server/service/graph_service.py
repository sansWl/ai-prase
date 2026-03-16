from typing import List
from utils import logger,neo4jUtils,redisUtils
from web_server.class_model import graph


def saveOrUpdate_graph_nodes(nodes: List[graph.graphNode]):
    """保存图节点"""
    # neo4jUtils.create_nodes(nodes,"graphNode")
    pass

def get_graph_nodes()->List[graph.graphNode]:
    """获取图节点"""
    pass

def saveOrUpdate_graph_edges(edges: List[graph.graphEdge]):
    """保存图边"""
    pass

def get_graph_edges()->List[graph.graphEdge]:
    """获取图边"""
    pass

def del_graph_nodes(nodeIds: List[str]):
    """删除图节点"""
    pass

def del_graph_edges(edgeIds: List[str]):
    """删除图边"""
    pass