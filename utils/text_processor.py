import re
import threading
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 加载 expand_map
try:
    from cache_data.expand_map import expand_text_map
except ImportError:
    # 如果文件不存在，使用空列表
    expand_text_map = []

# 线程锁，确保多线程安全
transform_lock = threading.RLock()


class SimHash:
    """SimHash 实现，用于文本相似度检测"""
    
    def __init__(self, hash_bits=64):
        """
        初始化 SimHash
        
        Args:
            hash_bits: hash 位数，默认为 64 位
        """
        self.hash_bits = hash_bits
    
    def _hash_func(self, token):
        """计算 token 的 hash 值"""
        # 使用 MD5 生成 hash
        hash_value = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
        return hash_value
    
    def _get_features(self, text):
        """提取文本特征（分词）"""
        # 使用正则表达式提取单词
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 使用 3-gram 作为特征
        features = []
        for i in range(len(words) - 2):
            feature = ' '.join(words[i:i+3])
            features.append(feature)
        
        # 如果文本太短，直接使用单词
        if not features and words:
            features = words
        
        return features
    
    def get_hash(self, text):
        """
        计算文本的 SimHash 值
        
        Args:
            text: 输入文本
        
        Returns:
            SimHash 值（整数）
        """
        if not text:
            return 0
        
        features = self._get_features(text)
        
        if not features:
            return 0
        
        # 初始化向量
        vector = [0] * self.hash_bits
        
        # 计算每个特征的 hash 并累加
        for feature in features:
            hash_value = self._hash_func(feature)
            for i in range(self.hash_bits):
                bit = (hash_value >> i) & 1
                if bit == 1:
                    vector[i] += 1
                else:
                    vector[i] -= 1
        
        # 生成 SimHash
        simhash = 0
        for i in range(self.hash_bits):
            if vector[i] > 0:
                simhash |= (1 << i)
        
        return simhash
    
    def get_hash_str(self, text):
        """
        获取 SimHash 的字符串表示
        
        Args:
            text: 输入文本
        
        Returns:
            SimHash 字符串（十六进制）
        """
        hash_value = self.get_hash(text)
        return format(hash_value, f'0{self.hash_bits // 4}x')
    
    def hamming_distance(self, hash1, hash2):
        """
        计算两个 hash 值的汉明距离
        
        Args:
            hash1: 第一个 hash 值
            hash2: 第二个 hash 值
        
        Returns:
            汉明距离
        """
        xor = hash1 ^ hash2
        distance = 0
        while xor:
            distance += 1
            xor &= xor - 1
        return distance
    
    def similarity(self, text1, text2):
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度（0-1 之间，1 表示完全相同）
        """
        hash1 = self.get_hash(text1)
        hash2 = self.get_hash(text2)
        
        distance = self.hamming_distance(hash1, hash2)
        # 相似度 = 1 - (汉明距离 / hash 位数)
        return 1 - (distance / self.hash_bits)
    
    def is_duplicate(self, text1, text2, threshold=3):
        """
        判断两个文本是否重复（相似）
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            threshold: 汉明距离阈值，小于等于此值认为是重复
        
        Returns:
            是否重复
        """
        hash1 = self.get_hash(text1)
        hash2 = self.get_hash(text2)
        distance = self.hamming_distance(hash1, hash2)
        return distance <= threshold


# 创建全局 SimHash 实例
simhash = SimHash()


def get_text_simhash(text, hash_bits=64):
    """
    获取文本的 SimHash 值
    
    Args:
        text: 输入文本
        hash_bits: hash 位数
    
    Returns:
        SimHash 值（整数）
    """
    hasher = SimHash(hash_bits=hash_bits)
    return hasher.get_hash(text)


def get_text_simhash_str(text, hash_bits=64):
    """
    获取文本的 SimHash 字符串表示
    
    Args:
        text: 输入文本
        hash_bits: hash 位数
    
    Returns:
        SimHash 字符串（十六进制）
    """
    hasher = SimHash(hash_bits=hash_bits)
    return hasher.get_hash_str(text)


def calculate_text_similarity(text1, text2, hash_bits=64):
    """
    计算两个文本的相似度
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        hash_bits: hash 位数
    
    Returns:
        相似度（0-1 之间）
    """
    hasher = SimHash(hash_bits=hash_bits)
    return hasher.similarity(text1, text2)


def is_duplicate_text(text1, text2, threshold=3, hash_bits=64):
    """
    判断两个文本是否重复
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        threshold: 汉明距离阈值
        hash_bits: hash 位数
    
    Returns:
        是否重复
    """
    hasher = SimHash(hash_bits=hash_bits)
    return hasher.is_duplicate(text1, text2, threshold)


def find_duplicate_texts(texts, threshold=3, hash_bits=64):
    """
    从文本列表中找出重复的文本
    
    Args:
        texts: 文本列表
        threshold: 汉明距离阈值
        hash_bits: hash 位数
    
    Returns:
        重复文本组的列表
    """
    hasher = SimHash(hash_bits=hash_bits)
    
    # 计算所有文本的 hash
    hashes = [(i, hasher.get_hash(text)) for i, text in enumerate(texts)]
    
    # 找出重复组
    duplicates = []
    used = set()
    
    for i, (idx1, hash1) in enumerate(hashes):
        if idx1 in used:
            continue
        
        group = [idx1]
        for idx2, hash2 in hashes[i+1:]:
            if idx2 in used:
                continue
            
            distance = hasher.hamming_distance(hash1, hash2)
            if distance <= threshold:
                group.append(idx2)
                used.add(idx2)
        
        if len(group) > 1:
            duplicates.append(group)
            used.add(idx1)
    
    return duplicates


def transform_text_with_expand_map(text, keys=None):
    """根据 expand_map 转换文本并处理关键字扩展
    
    Args:
        text: 输入文本
        keys: 要扩展的关键字列表
    
    Returns:
        元组 (original_text, transformed_text)
    """
    with transform_lock:
        # 保留原始文本
        original_text = text
        transformed_text = text
        
        # 1. 处理 expand_map 替换
        for item in expand_text_map:
            for target, synonyms in item.items():
                for synonym in synonyms:
                    # 构建正则表达式，确保匹配整个词
                    pattern = r'\b' + re.escape(synonym) + r'\b'
                    # 使用不区分大小写的匹配
                    transformed_text = re.sub(pattern, target, transformed_text, flags=re.IGNORECASE)
        
        # 2. 处理 keys 参数，将关键字重复
        if keys:
            for key in keys:
                # 构建正则表达式，确保匹配整个词
                pattern = r'\b' + re.escape(key) + r'\b'
                # 替换为重复的关键字
                transformed_text = re.sub(pattern, lambda m: m.group(0) * 2, transformed_text)
        
        return original_text, transformed_text


def remove_section_descriptors(text):
    """去掉文本中的分段描述符
    
    Args:
        text: 输入文本
    
    Returns:
        处理后的文本
    """
    # 移除常见的分段描述符，如 "1. "、"2. "、"a. "、"b. " 等
    patterns = [
        r'^\s*[0-9]+\.\s+',  # 数字编号
        r'^\s*[a-zA-Z]+\.\s+',  # 字母编号
        r'^\s*[-*•]\s+',  # 项目符号
        r'^\s*[\[\(]?[0-9]+[\]\)]?\s+',  # 带括号的数字
    ]
    
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        processed_line = line
        for pattern in patterns:
            processed_line = re.sub(pattern, '', processed_line, flags=re.MULTILINE)
        if processed_line.strip():
            processed_lines.append(processed_line)
    
    return '\n'.join(processed_lines)


def clean_text(text):
    """清理文本，去除多余空白字符
    
    Args:
        text: 输入文本
    
    Returns:
        清理后的文本
    """
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    text = text.strip()
    return text


def normalize_whitespace(text):
    """标准化空白字符
    
    Args:
        text: 输入文本
    
    Returns:
        标准化后的文本
    """
    # 替换连续的空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 保留换行符
    text = re.sub(r'\s*\n\s*', '\n', text)
    return text


def remove_special_characters(text, keep_chars=None):
    """移除特殊字符
    
    Args:
        text: 输入文本
        keep_chars: 要保留的特殊字符
    
    Returns:
        处理后的文本
    """
    if keep_chars:
        # 构建保留字符的正则表达式
        keep_pattern = ''.join(re.escape(c) for c in keep_chars)
        pattern = f'[^a-zA-Z0-9\s{keep_pattern}]'
    else:
        pattern = r'[^a-zA-Z0-9\s]'
    
    return re.sub(pattern, '', text)


def get_chunked_text(text, max_chunk_size=1000):
    """将文本分割成指定大小的块
    
    Args:
        text: 输入文本
        max_chunk_size: 每个块的最大大小
    
    Returns:
        文本块列表
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(text)
    return chunks
