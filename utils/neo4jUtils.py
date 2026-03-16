from middleware.neo4j_client import Neo4jClient
from typing import Dict, List, Optional, Any, Union

neo4j_client = Neo4jClient()


def execute_query(query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """执行 Cypher 查询
    
    Args:
        query: Cypher 查询语句
        parameters: 查询参数
    
    Returns:
        查询结果列表
    """
    return neo4j_client.execute_query(query, parameters or {})


# ==================== 节点操作 ====================

def create_node(
    label: str,
    properties: Optional[Dict[str, Any]] = None,
    return_node: bool = True
) -> List[Dict]:
    """创建节点
    
    Args:
        label: 节点标签
        properties: 节点属性字典
        return_node: 是否返回创建的节点
    
    Returns:
        创建的节点列表
    """
    params = properties or {}
    
    query_parts = [f"CREATE (n:{label}"]
    if params:
        query_parts.append(" {")
        query_parts.append(", ".join([f"{key}: ${key}" for key in params.keys()]))
        query_parts.append("}")
    query_parts.append(")")
    if return_node:
        query_parts.append(" RETURN n")
    
    query = "".join(query_parts)
    return execute_query(query, params)


def create_nodes(
    nodes: List[Dict[str, Any]],
    label: Optional[str] = None
) -> List[Dict]:
    """批量创建节点
    
    Args:
        nodes: 节点列表，每个节点是一个字典，可包含 'label' 和 'properties' 键
               或者直接是属性字典（此时使用全局 label）
        label: 全局标签（如果节点未指定）
    
    Returns:
        创建的节点列表
    """
    if not nodes:
        return []
    
    results = []
    
    for node_data in nodes:
        if "label" in node_data and "properties" in node_data:
            node_label = node_data["label"]
            node_properties = node_data["properties"]
        else:
            node_label = label
            node_properties = node_data
        
        if not node_label:
            raise ValueError("每个节点必须指定 label，或者提供全局 label")
        
        result = create_node(node_label, node_properties)
        results.extend(result)
    
    return results


def get_node(
    label: str,
    properties: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None
) -> List[Dict]:
    """获取节点
    
    Args:
        label: 节点标签
        properties: 节点属性条件
        limit: 返回数量限制
    
    Returns:
        匹配的节点列表
    """
    params = properties or {}
    
    query_parts = [f"MATCH (n:{label}"]
    if params:
        query_parts.append(" {")
        query_parts.append(", ".join([f"{key}: ${key}" for key in params.keys()]))
        query_parts.append("}")
    query_parts.append(")")
    query_parts.append(" RETURN n")
    if limit:
        query_parts.append(f" LIMIT {limit}")
    
    query = "".join(query_parts)
    return execute_query(query, params)


def get_node_by_id(node_id: int) -> List[Dict]:
    """通过 ID 获取节点
    
    Args:
        node_id: 节点 ID
    
    Returns:
        匹配的节点列表
    """
    query = "MATCH (n) WHERE id(n) = $node_id RETURN n"
    return execute_query(query, {"node_id": node_id})


def update_node(
    label: str,
    match_properties: Dict[str, Any],
    update_properties: Dict[str, Any],
    return_node: bool = True
) -> List[Dict]:
    """更新节点
    
    Args:
        label: 节点标签
        match_properties: 匹配条件属性
        update_properties: 要更新的属性
        return_node: 是否返回更新后的节点
    
    Returns:
        更新的节点列表
    """
    params = {**match_properties, **update_properties}
    
    match_clause = ", ".join([f"n.{key} = ${key}" for key in match_properties.keys()])
    set_clause = ", ".join([f"n.{key} = ${key}" for key in update_properties.keys()])
    
    query_parts = [f"MATCH (n:{label}) WHERE {match_clause}"]
    query_parts.append(f" SET {set_clause}")
    if return_node:
        query_parts.append(" RETURN n")
    
    query = "".join(query_parts)
    return execute_query(query, params)


def update_node_properties(
    node_id: int,
    properties: Dict[str, Any],
    return_node: bool = True
) -> List[Dict]:
    """通过 ID 更新节点属性
    
    Args:
        node_id: 节点 ID
        properties: 要更新的属性
        return_node: 是否返回更新后的节点
    
    Returns:
        更新的节点列表
    """
    params = {"node_id": node_id, **properties}
    set_clause = ", ".join([f"n.{key} = ${key}" for key in properties.keys()])
    
    query_parts = [f"MATCH (n) WHERE id(n) = $node_id"]
    query_parts.append(f" SET {set_clause}")
    if return_node:
        query_parts.append(" RETURN n")
    
    query = "".join(query_parts)
    return execute_query(query, params)


def delete_node(
    label: str,
    properties: Optional[Dict[str, Any]] = None,
    detach: bool = True
) -> List[Dict]:
    """删除节点
    
    Args:
        label: 节点标签
        properties: 节点属性条件
        detach: 是否同时删除关系
    
    Returns:
        删除操作结果
    """
    params = properties or {}
    
    query_parts = [f"MATCH (n:{label}"]
    if params:
        query_parts.append(" {")
        query_parts.append(", ".join([f"{key}: ${key}" for key in params.keys()]))
        query_parts.append("}")
    query_parts.append(")")
    if detach:
        query_parts.append(" DETACH DELETE n")
    else:
        query_parts.append(" DELETE n")
    
    query = "".join(query_parts)
    return execute_query(query, params)


def delete_node_by_id(node_id: int, detach: bool = True) -> List[Dict]:
    """通过 ID 删除节点
    
    Args:
        node_id: 节点 ID
        detach: 是否同时删除关系
    
    Returns:
        删除操作结果
    """
    query = f"MATCH (n) WHERE id(n) = $node_id {'DETACH' if detach else ''} DELETE n"
    return execute_query(query, {"node_id": node_id})


def merge_node(
    label: str,
    match_properties: Dict[str, Any],
    on_create_properties: Optional[Dict[str, Any]] = None,
    on_match_properties: Optional[Dict[str, Any]] = None,
    return_node: bool = True
) -> List[Dict]:
    """合并节点（如果存在则更新，不存在则创建）
    
    Args:
        label: 节点标签
        match_properties: 匹配条件属性
        on_create_properties: 创建时设置的属性
        on_match_properties: 匹配时更新的属性
        return_node: 是否返回节点
    
    Returns:
        合并后的节点列表
    """
    params = {**match_properties}
    
    match_clause = ", ".join([f"{key}: ${key}" for key in match_properties.keys()])
    
    query_parts = [f"MERGE (n:{label} {{ {match_clause} }})"]
    
    if on_create_properties:
        params.update(on_create_properties)
        set_clause = ", ".join([f"n.{key} = ${key}" for key in on_create_properties.keys()])
        query_parts.append(f" ON CREATE SET {set_clause}")
    
    if on_match_properties:
        params.update(on_match_properties)
        set_clause = ", ".join([f"n.{key} = ${key}" for key in on_match_properties.keys()])
        query_parts.append(f" ON MATCH SET {set_clause}")
    
    if return_node:
        query_parts.append(" RETURN n")
    
    query = "".join(query_parts)
    return execute_query(query, params)


# ==================== 关系操作 ====================

def create_relationship(
    from_label: str,
    from_properties: Dict[str, Any],
    to_label: str,
    to_properties: Dict[str, Any],
    rel_type: str,
    rel_properties: Optional[Dict[str, Any]] = None,
    return_rel: bool = True
) -> List[Dict]:
    """创建关系
    
    Args:
        from_label: 起始节点标签
        from_properties: 起始节点属性
        to_label: 目标节点标签
        to_properties: 目标节点属性
        rel_type: 关系类型
        rel_properties: 关系属性
        return_rel: 是否返回关系
    
    Returns:
        创建的关系列表
    """
    params = {
        **from_properties,
        **to_properties,
        **(rel_properties or {})
    }
    
    from_match = ", ".join([f"a.{key} = $from_{key}" for key in from_properties.keys()])
    to_match = ", ".join([f"b.{key} = $to_{key}" for key in to_properties.keys()])
    
    # 重命名参数避免冲突
    renamed_params = {}
    for key, value in from_properties.items():
        renamed_params[f"from_{key}"] = value
    for key, value in to_properties.items():
        renamed_params[f"to_{key}"] = value
    if rel_properties:
        renamed_params.update(rel_properties)
    
    query_parts = [
        f"MATCH (a:{from_label}), (b:{to_label})",
        f" WHERE {from_match} AND {to_match}",
        f" CREATE (a)-[r:{rel_type}"
    ]
    
    if rel_properties:
        query_parts.append(" {")
        query_parts.append(", ".join([f"{key}: ${key}" for key in rel_properties.keys()]))
        query_parts.append("}")
    
    query_parts.append("]->(b)")
    
    if return_rel:
        query_parts.append(" RETURN a, r, b")
    
    query = "".join(query_parts)
    return execute_query(query, renamed_params)


def create_relationship_by_ids(
    from_id: int,
    to_id: int,
    rel_type: str,
    rel_properties: Optional[Dict[str, Any]] = None,
    return_rel: bool = True
) -> List[Dict]:
    """通过节点 ID 创建关系
    
    Args:
        from_id: 起始节点 ID
        to_id: 目标节点 ID
        rel_type: 关系类型
        rel_properties: 关系属性
        return_rel: 是否返回关系
    
    Returns:
        创建的关系列表
    """
    params = {"from_id": from_id, "to_id": to_id, **(rel_properties or {})}
    
    query_parts = [
        "MATCH (a), (b)",
        " WHERE id(a) = $from_id AND id(b) = $to_id",
        f" CREATE (a)-[r:{rel_type}"
    ]
    
    if rel_properties:
        query_parts.append(" {")
        query_parts.append(", ".join([f"{key}: ${key}" for key in rel_properties.keys()]))
        query_parts.append("}")
    
    query_parts.append("]->(b)")
    
    if return_rel:
        query_parts.append(" RETURN a, r, b")
    
    query = "".join(query_parts)
    return execute_query(query, params)


def get_relationships(
    from_label: Optional[str] = None,
    from_properties: Optional[Dict[str, Any]] = None,
    rel_type: Optional[str] = None,
    to_label: Optional[str] = None,
    to_properties: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None
) -> List[Dict]:
    """获取关系
    
    Args:
        from_label: 起始节点标签
        from_properties: 起始节点属性
        rel_type: 关系类型
        to_label: 目标节点标签
        to_properties: 目标节点属性
        limit: 返回数量限制
    
    Returns:
        匹配的关系列表
    """
    params = {}
    
    query_parts = ["MATCH (a"]
    if from_label:
        query_parts.append(f":{from_label}")
    if from_properties:
        query_parts.append(" {")
        query_parts.append(", ".join([f"{key}: $from_{key}" for key in from_properties.keys()]))
        query_parts.append("}")
        for key, value in from_properties.items():
            params[f"from_{key}"] = value
    
    query_parts.append(")-[r")
    if rel_type:
        query_parts.append(f":{rel_type}")
    query_parts.append("]->(b")
    
    if to_label:
        query_parts.append(f":{to_label}")
    if to_properties:
        query_parts.append(" {")
        query_parts.append(", ".join([f"{key}: $to_{key}" for key in to_properties.keys()]))
        query_parts.append("}")
        for key, value in to_properties.items():
            params[f"to_{key}"] = value
    
    query_parts.append(") RETURN a, r, b")
    
    if limit:
        query_parts.append(f" LIMIT {limit}")
    
    query = "".join(query_parts)
    return execute_query(query, params)


def update_relationship(
    from_label: str,
    from_properties: Dict[str, Any],
    rel_type: str,
    to_label: str,
    to_properties: Dict[str, Any],
    update_properties: Dict[str, Any],
    return_rel: bool = True
) -> List[Dict]:
    """更新关系
    
    Args:
        from_label: 起始节点标签
        from_properties: 起始节点属性
        rel_type: 关系类型
        to_label: 目标节点标签
        to_properties: 目标节点属性
        update_properties: 要更新的属性
        return_rel: 是否返回更新后的关系
    
    Returns:
        更新的关系列表
    """
    params = {
        **from_properties,
        **to_properties,
        **update_properties
    }
    
    from_match = ", ".join([f"a.{key} = $from_{key}" for key in from_properties.keys()])
    to_match = ", ".join([f"b.{key} = $to_{key}" for key in to_properties.keys()])
    set_clause = ", ".join([f"r.{key} = ${key}" for key in update_properties.keys()])
    
    # 重命名参数
    renamed_params = {}
    for key, value in from_properties.items():
        renamed_params[f"from_{key}"] = value
    for key, value in to_properties.items():
        renamed_params[f"to_{key}"] = value
    renamed_params.update(update_properties)
    
    query_parts = [
        f"MATCH (a:{from_label})-[r:{rel_type}]->(b:{to_label})",
        f" WHERE {from_match} AND {to_match}",
        f" SET {set_clause}"
    ]
    
    if return_rel:
        query_parts.append(" RETURN a, r, b")
    
    query = "".join(query_parts)
    return execute_query(query, renamed_params)


def delete_relationship(
    from_label: str,
    from_properties: Dict[str, Any],
    rel_type: str,
    to_label: str,
    to_properties: Dict[str, Any]
) -> List[Dict]:
    """删除关系
    
    Args:
        from_label: 起始节点标签
        from_properties: 起始节点属性
        rel_type: 关系类型
        to_label: 目标节点标签
        to_properties: 目标节点属性
    
    Returns:
        删除操作结果
    """
    from_match = ", ".join([f"a.{key} = $from_{key}" for key in from_properties.keys()])
    to_match = ", ".join([f"b.{key} = $to_{key}" for key in to_properties.keys()])
    
    renamed_params = {}
    for key, value in from_properties.items():
        renamed_params[f"from_{key}"] = value
    for key, value in to_properties.items():
        renamed_params[f"to_{key}"] = value
    
    query = f"""
    MATCH (a:{from_label})-[r:{rel_type}]->(b:{to_label})
    WHERE {from_match} AND {to_match}
    DELETE r
    """
    return execute_query(query, renamed_params)


def merge_relationship(
    from_label: str,
    from_properties: Dict[str, Any],
    rel_type: str,
    to_label: str,
    to_properties: Dict[str, Any],
    on_create_properties: Optional[Dict[str, Any]] = None,
    on_match_properties: Optional[Dict[str, Any]] = None,
    return_rel: bool = True
) -> List[Dict]:
    """合并关系（如果存在则更新，不存在则创建）
    
    Args:
        from_label: 起始节点标签
        from_properties: 起始节点属性
        rel_type: 关系类型
        to_label: 目标节点标签
        to_properties: 目标节点属性
        on_create_properties: 创建时设置的属性
        on_match_properties: 匹配时更新的属性
        return_rel: 是否返回关系
    
    Returns:
        合并后的关系列表
    """
    params = {}
    
    from_match = ", ".join([f"a.{key} = $from_{key}" for key in from_properties.keys()])
    to_match = ", ".join([f"b.{key} = $to_{key}" for key in to_properties.keys()])
    
    renamed_params = {}
    for key, value in from_properties.items():
        renamed_params[f"from_{key}"] = value
    for key, value in to_properties.items():
        renamed_params[f"to_{key}"] = value
    
    query_parts = [
        f"MATCH (a:{from_label}), (b:{to_label})",
        f" WHERE {from_match} AND {to_match}",
        f" MERGE (a)-[r:{rel_type}]->(b)"
    ]
    
    if on_create_properties:
        renamed_params.update(on_create_properties)
        set_clause = ", ".join([f"r.{key} = ${key}" for key in on_create_properties.keys()])
        query_parts.append(f" ON CREATE SET {set_clause}")
    
    if on_match_properties:
        renamed_params.update(on_match_properties)
        set_clause = ", ".join([f"r.{key} = ${key}" for key in on_match_properties.keys()])
        query_parts.append(f" ON MATCH SET {set_clause}")
    
    if return_rel:
        query_parts.append(" RETURN a, r, b")
    
    query = "".join(query_parts)
    return execute_query(query, renamed_params)


# ==================== 高级查询 ====================

def get_neighbors(
    label: str,
    properties: Dict[str, Any],
    direction: str = "both",
    rel_type: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict]:
    """获取邻居节点
    
    Args:
        label: 节点标签
        properties: 节点属性
        direction: 方向 (in, out, both)
        rel_type: 关系类型
        limit: 返回数量限制
    
    Returns:
        邻居节点列表
    """
    params = properties.copy()
    
    match_clause = ", ".join([f"n.{key} = ${key}" for key in properties.keys()])
    
    rel_pattern = ""
    if direction == "in":
        rel_pattern = "<-[r" + (f":{rel_type}" if rel_type else "") + "]-"
    elif direction == "out":
        rel_pattern = "-[r" + (f":{rel_type}" if rel_type else "") + "]->"
    else:
        rel_pattern = "-[r" + (f":{rel_type}" if rel_type else "") + "]-"
    
    query_parts = [
        f"MATCH (n:{label}){rel_pattern}(m)",
        f" WHERE {match_clause}",
        " RETURN n, r, m"
    ]
    
    if limit:
        query_parts.append(f" LIMIT {limit}")
    
    query = "".join(query_parts)
    return execute_query(query, params)


def get_path(
    from_label: str,
    from_properties: Dict[str, Any],
    to_label: str,
    to_properties: Dict[str, Any],
    max_depth: int = 5
) -> List[Dict]:
    """获取两个节点之间的路径
    
    Args:
        from_label: 起始节点标签
        from_properties: 起始节点属性
        to_label: 目标节点标签
        to_properties: 目标节点属性
        max_depth: 最大深度
    
    Returns:
        路径列表
    """
    params = {}
    
    from_match = ", ".join([f"a.{key} = $from_{key}" for key in from_properties.keys()])
    to_match = ", ".join([f"b.{key} = $to_{key}" for key in to_properties.keys()])
    
    renamed_params = {}
    for key, value in from_properties.items():
        renamed_params[f"from_{key}"] = value
    for key, value in to_properties.items():
        renamed_params[f"to_{key}"] = value
    
    query = f"""
    MATCH path = (a:{from_label})-[*1..{max_depth}]-(b:{to_label})
    WHERE {from_match} AND {to_match}
    RETURN path
    """
    return execute_query(query, renamed_params)


def count_nodes(label: str, properties: Optional[Dict[str, Any]] = None) -> int:
    """统计节点数量
    
    Args:
        label: 节点标签
        properties: 节点属性条件
    
    Returns:
        节点数量
    """
    params = properties or {}
    
    query_parts = [f"MATCH (n:{label}"]
    if params:
        query_parts.append(" {")
        query_parts.append(", ".join([f"{key}: ${key}" for key in params.keys()]))
        query_parts.append("}")
    query_parts.append(") RETURN count(n) AS count")
    
    query = "".join(query_parts)
    result = execute_query(query, params)
    return result[0]["count"] if result else 0


def clear_database(confirm: bool = False) -> List[Dict]:
    """清空数据库（谨慎使用！）
    
    Args:
        confirm: 是否确认操作
    
    Returns:
        操作结果
    """
    if not confirm:
        return [{"warning": "此操作会清空所有数据！请设置 confirm=True 确认"}]
    
    query = "MATCH (n) DETACH DELETE n"
    return execute_query(query)
