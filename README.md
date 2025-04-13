# MCP Tutorials

### Reference

https://modelcontextprotocol.io/quickstart/server

- [v] 튜토리얼에서 제공한 mcp 서버를 cline을 통해서 사용해보기

1. cline에서 에러가 발생했다고 하는데, cline에서 debug level의 로그를 내는 과정에서 성공한 에러까지 stderr로 내는 것 아닐까 추정, loglevel을 error로 만드니 해결([링크](https://github.com/cline/cline/issues/1272))

- [] Tools에 argument에 대한 설명이 제대로 뜨지 않음, 이슈인지 아닌지 확인 필요
- [v] Python linter와 formatter 다시 설치(-> ruff로 설치)

API 요청을 안 사용하지는 않는다. (나의 요청 + MCP 서버들이 제공하는 tools)를 LLM이 보고 판단하여서, 알아서 실행시키고 이 과정에서 API 요청이 2회 발생. $0.05, $0.03. 어쨌거나 tools를 잘 이용해서 가져오는 걸 알 수 있었다.

2. 예제들 확인해보기

- filesystem: tools 사용
- drive: resources 사용. -> resources로 가능한 모든 operation은 tools로도 가능하나 다른 abstraction을 제공(REST API의 GET과 POst 정도의 차이로 이해)

## 예제 추가

Python SDK 에 있는 내용들 이해하기

<https://github.com/modelcontextprotocol/python-sdk>

1. Resource의 정의

<https://modelcontextprotocol.io/docs/concepts/resources#resource-templates>

Any kinds of data that an MCP server wants to make available to MCP clients.

- Resource discovery(MCP clients는 MCP server에 available한 resource를 어떻게 알아내는가)
  - direct resources: `resources/list` 엔드포인트를 통해 아래의 형식으로 리소스들을 노출

```javascript
{
  uri: string;  // Unique identifier of the resource
  name: string; // human-readable name of resource
  description?: string; // optional description
  mimeType?: string; // optionam mimetype
}
```

- resource templates: `uritemplate`을 통해 제공하는 리소스들을 노출

```javascript
{
  uriTemplate: string;   // URI template following RFC 6570
  name: string;          // Human-readable name for this type
  description?: string;  // Optional description
  mimeType?: string;     // Optional MIME type for all matching resources
}
```

- MCP client가 resource discovery를 통해, available한 resources를 mcp server로부터 불러왔다면, 어떤 식으로 호출할 수 있을까?
  - resource read handler를 정의하는 방법은 두 가지
    - @mcp.resource()를 통해 `uri`를 입력받는 함수를 decorate하면서 정의
    - 혹은 @mcp.resource(`uri_template`)을 통해서 정의

정리하자면, mcpserver은 resource discovery가 가능하도록 리소스의 URI를 직접, 혹은 템플릿을 통해 노출한다. `mcpclients`는 available한 resource를 discover한 후 URI를 통해 해당 리소스를 요청할 수 있다.