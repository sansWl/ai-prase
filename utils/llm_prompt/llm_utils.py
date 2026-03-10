from typing import Any, List, Dict
from factories.llmsFactory.llms_factory import LLMsFactory
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class WebContentExtractor:
    """网页内容提取器"""
    
    # 域名特定的提取规则
    DOMAIN_RULES = {
        'zhipin.com': {
            'name': 'BOSS直聘',
            'selectors': {
                'job_card': '.job-card-wrapper',
                'title': '.job-card-left',
                'salary': '.salary',
                'experience': '.tag-list',
                'company': '.company-name',
                'location': '.job-area',
                'job_desc': '.job-sec-text',
                'job_require': '.job-sec-text'
            }
        }
    }
    
    @classmethod
    def get_domain_rules(cls, url: str) -> Dict[str, Any]:
        """根据URL获取对应的提取规则"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 移除www前缀
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # 查找匹配的域名规则
        for rule_domain, rules in cls.DOMAIN_RULES.items():
            if rule_domain in domain:
                return rules
        
        # 默认规则
        return {
            'name': '通用网页',
            'selectors': {
                'content': 'body'
            }
        }
    
    @classmethod
    def extract(cls, url: str, target_region: str = None) -> Dict[str, Any]:
        """提取网页内容
        
        Args:
            url: 网页URL
            target_region: 目标区域选择器（可选）
            
        Returns:
            提取的内容字典
        """
        try:
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.zhipin.com/'
            }
            
            # 发送请求
            with httpx.Client(timeout=30) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取域名规则
            domain_rules = cls.get_domain_rules(url)
            selectors = domain_rules['selectors']
            
            # 提取内容
            result = {
                'url': url,
                'domain': domain_rules['name'],
                'raw_html': response.text[:50000],  # 限制HTML大小
                'extracted_data': {}
            }
            
            # 根据目标区域提取
            if target_region and target_region in selectors:
                selector = selectors[target_region]
                elements = soup.select(selector)
                result['extracted_data'][target_region] = [
                    elem.get_text(strip=True) for elem in elements
                ]
            else:
                # 提取所有定义的区域
                for region_name, selector in selectors.items():
                    elements = soup.select(selector)
                    result['extracted_data'][region_name] = [
                        elem.get_text(strip=True) for elem in elements[:20]  # 限制数量
                    ]
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'extracted_data': {}
            }


@tool
def fetch_webpage(url: str) -> str:
    """获取网页的完整HTML内容
    
    Args:
        url: 网页URL
        
    Returns:
        网页HTML内容
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
        
        return response.text
    except Exception as e:
        return f"获取网页失败: {str(e)}"


@tool
def extract_job_info(url: str) -> List[Dict[str, Any]]:
    """从BOSS直聘网页提取职位信息
    
    Args:
        url: BOSS直聘职位列表页面URL
        
    Returns:
        职位信息列表
    """
    extractor = WebContentExtractor()
    result = extractor.extract(url)
    
    if 'error' in result:
        return [{'error': result['error']}]
    
    jobs = []
    data = result.get('extracted_data', {})
    
    # 提取职位卡片信息
    job_cards = data.get('job_card', [])
    titles = data.get('title', [])
    salaries = data.get('salary', [])
    experiences = data.get('experience', [])
    companies = data.get('company', [])
    locations = data.get('location', [])
    
    # 构建职位信息
    for i in range(min(len(titles), 20)):
        job = {
            'title': titles[i] if i < len(titles) else '',
            'salary': salaries[i] if i < len(salaries) else '',
            'experience': experiences[i] if i < len(experiences) else '',
            'company': companies[i] if i < len(companies) else '',
            'location': locations[i] if i < len(locations) else '',
            'source_url': url
        }
        if job['title']:
            jobs.append(job)
    
    return jobs


@tool
def analyze_webpage_content(url: str, query: str) -> str:
    """使用LLM分析网页内容
    
    Args:
        url: 网页URL
        query: 分析查询
        
    Returns:
        LLM分析结果
    """
    # 获取网页内容
    html = fetch_webpage.invoke({'url': url})
    
    if html.startswith("获取网页失败"):
        return html
    
    # 提取文本内容
    soup = BeautifulSoup(html, 'html.parser')
    
    # 移除脚本和样式
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text(separator='\n', strip=True)
    text = '\n'.join(line for line in text.split('\n') if line.strip())
    text = text[:8000]  # 限制文本长度
    
    # 使用LLM分析
    llm = LLMsFactory().create_llm()
    
    prompt = f"""请分析以下网页内容，回答用户的问题。
                网页URL: {url}

                网页内容:
                {text}

                用户问题: {query}

                请提供详细的分析结果。"""
    
    response = llm.invoke(prompt)
    return response.content if hasattr(response, 'content') else str(response)


class LLMUtils:
    """LLM工具类"""
    
    def __init__(self, llm_react: bool = False, prompt: Any = None, 
                 memory: Any = None, memory_config: Any = None, tools: List = None):
        self.llm_react = llm_react
        self.prompt = prompt
        self.memory = memory
        self.memory_config = memory_config
        self.tools = tools or []
        self.llm = None
        self.agent = None
        self.agent_executor = None
        
    def set_llm(self):
        """设置LLM模型"""
        factory = LLMsFactory()
        self.llm = factory.create_llm()
        return self
    
    def create_llm_agent(self):
        """创建LLM Agent（使用langchain.agents）"""
        if self.llm_react and self.tools:
            # 使用langchain的ReAct Agent
            from langchain import hub
            
            # 拉取ReAct提示模板
            react_prompt = hub.pull("hwchase17/react")
            
            # 创建ReAct Agent
            self.agent = create_react_agent(
                llm=self.llm or LLMsFactory().create_llm(),
                tools=self.tools,
                prompt=react_prompt
            )
            
            # 创建Agent执行器
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=self.memory or ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                ),
                verbose=True,
                handle_parsing_errors=True
            )
        
        return self
    
    def invoke_agent(self, query: str) -> Dict[str, Any]:
        """调用Agent执行查询"""
        if self.agent_executor:
            return self.agent_executor.invoke({"input": query})
        else:
            # 直接调用LLM
            llm = self.llm or LLMsFactory().create_llm()
            response = llm.invoke(query)
            return {"output": response.content if hasattr(response, 'content') else str(response)}
    
    def invoke_agent_stream(self, query: str) -> Dict[str, Any]:
        """调用Agent执行查询（流式模式）"""
        if self.agent_executor:
            return self.agent_executor.stream({"input": query})
        else:
            # 直接调用LLM
            llm = self.llm or LLMsFactory().create_llm()
            return llm.stream(query)

    async def stream_agent_praser(self, iterator):
         for event in iterator:
            if "output" in event:
                yield f"data: {event['output']} \n\n"
            else:
                yield f"data: {event.content}  \n\n"

    def extract_webpage_info(self, url: str, region: str = None) -> Dict[str, Any]:
        """提取网页信息"""
        extractor = WebContentExtractor()
        return extractor.extract(url, region)
    
    def analyze_content(self, content: str, query: str) -> str:
        """使用LLM分析内容"""
        llm = self.llm or LLMsFactory().create_llm()
        
        prompt = f"""请分析以下内容，回答用户的问题。
                    内容:
                    {content[:5000]}

                    用户问题: {query}

                    请提供详细的分析结果。"""
        
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)


class LLMBuilder:
    """LLM工具构建器"""
    
    def __init__(self):
        self._prompt = None
        self._llm_react = False
        self._memory = None
        self._memory_config = None
        self._tools = []
        
    def set_prompt(self, prompt: Any):
        """设置prompt模板"""
        self._prompt = prompt
        return self
    
    def set_llm_react(self, react_agent: bool):
        """设置是否使用ReAct Agent"""
        self._llm_react = react_agent
        return self
    
    def set_tools(self, tools: List):
        """设置工具列表"""
        self._tools = tools
        return self
    
    def add_tool(self, tool_func):
        """添加单个工具"""
        self._tools.append(tool_func)
        return self

    def set_memory(self, memory: Any):
        """设置记忆组件"""
        self._memory = memory
        return self

    def set_memory_config(self, sessionId: str):
        """设置记忆配置"""
        self._memory_config = {"configurable": {"thread_id": sessionId}}
        return self

    def build(self) -> LLMUtils:
        """构建LLMUtils实例"""
        # 创建短期记忆
        from langchain.memory import ConversationBufferMemory
        memory = self._memory or ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        llm_utils = LLMUtils(
            llm_react=self._llm_react,
            prompt=self._prompt,
            memory=memory,
            memory_config=self._memory_config,
            tools=self._tools
        )
        
        
        # 创建Agent
        if self._llm_react:
            llm_utils.create_llm_agent()
        
        return llm_utils


# 预定义的Agent构建函数
def create_boss_zhipin_agent() -> LLMUtils:
    """创建BOSS直聘专用Agent"""
    return LLMBuilder() \
        .set_llm_react(True) \
        .add_tool(extract_job_info) \
        .add_tool(analyze_webpage_content) \
        .add_tool(fetch_webpage) \
        .build()

def create_normal_agent(react:bool = False) -> LLMUtils:
    """创建普通LLM Agent"""
    return LLMBuilder() \
        .set_llm_react(react) \
        .build()

