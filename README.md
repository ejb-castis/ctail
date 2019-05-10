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


# CCat

## 기능

- cilog 포멧에 대한 하이라이트
- eventlog 포멧에 대한 하이라이트
- 괄호 내 단어들에 대한 하이라이트
- stdin pipe 지원

## 사용 예
```bash

# cat 
$ ccat -v test/test* 
>>> Open files :['test/test1.log', 'test/test2.log', 'test/test3.log', 'test/test4.log', 'test/test5.log', 'test/test6.log']
>>> Open :test/test1.log , size :120
2018-10-26 16:37:42 Global none LoadBalancer2 STARTED!
2018-10-26 16:37:45 Global debug Ping-Client : IsServerAlive ERROR!! -> -1, 127.0.0.1
>>> Open :test/test2.log , size :75
2018-10-26 16:37:48 Global debug Ping-Client : IsServerAlive ERROR!! -> -1, 127.0.0.1
>>> Open :test/test3.log , size :75
2018-10-26 16:37:51 Global debug Ping-Client : IsServerAlive ERROR!! -> -1, 127.0.0.1
>>> Open :test/test4.log , size :75
2018-10-26 16:37:54 Global debug Ping-Client : IsServerAlive ERROR!! -> -1, 127.0.0.1
>>> Open :test/test5.log , size :225
2018-10-26 16:37:57 Global debug Ping-Client : IsServerAlive ERROR!! -> -1, 127.0.0.1
2018-10-26 16:38:00 Global debug Ping-Client : IsServerAlive ERROR!! -> -1, 127.0.0.1
2018-10-26 16:38:03 Global debug Ping-Client : IsServerAlive ERROR!! -> -1, 127.0.0.1
>>> Open :test/test6.log , size :91
2018-10-26 16:38:07 Global none SCP-Client : IsServerAlive RECOVERY (OnObjectServerResponse)!! -> -1

>>> Open files :{'test/test5.log': 225, 'test/test1.log': 120, 'test/test6.log': 91, 'test/test2.log': 75, 'test/test4.log': 75, 'test/test3.log': 75} 
>>> Last Open :test/test6.log , offset :91

# pipe
$ cat EventLog.log | ccat
```
