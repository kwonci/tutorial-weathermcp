# MCP Tutorials

### Reference

https://modelcontextprotocol.io/quickstart/server

- [v] 튜토리얼에서 제공한 mcp 서버를 cline을 통해서 사용해보기

1. cline에서 에러가 발생했다고 하는데, cline에서 debug level의 로그를 내는 과정에서 성공한 에러까지 stderr로 내는 것 아닐까 추정, loglevel을 error로 만드니 해결([링크](https://github.com/cline/cline/issues/1272))

- [] Tools에 argument에 대한 설명이 제대로 뜨지 않음, 이슈인지 아닌지 확인 필요
- [] Python linter와 formatter 다시 설치

API 요청을 안 사용하지는 않는다. (나의 요청 + MCP 서버들이 제공하는 tools)를 LLM이 보고 판단하여서, 알아서 실행시키고 이 과정에서 API 요청이 2회 발생. $0.05, $0.03. 어쨌거나 tools를 잘 이용해서 가져오는 걸 알 수 있었다.