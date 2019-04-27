# CTail

최신 파일을 계속해서 tail -f 해주는 python(>=2.4) 스크립트

## 기능

- 폴더 내 최신 파일을 자동으로 열어줌
- cilog 포멧에 대한 하이라이트
- eventlog 포멧에 대한 하이라이트
- 괄호 내 단어들에 대한 하이라이트
- stdin pipe 지원
- 지정한 파일만 tail하는 기능
- tail 하고 있던 파일에 대한 retry 기능

## 설치

```
$ wget -O - https://raw.githubusercontent.com/castisdev/ctail/master/install.sh --no-check-certificate | bash
```

## 사용 예
```
# 폴더의 최신 파일을 tail
$ ctail /var/log/castis/vod/2015-03/2015-
...

# 지정한 파일을 tail
$ ctail -f /var/log/castis/vod/event.log
...

# pipe
$ cat EventLog.log | ctail
...
```

## 데모 

![](https://github.com/castisdev/ctail/blob/master/sample.png)

