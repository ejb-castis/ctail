# CTail

최신 파일(linux)을 계속해서 tail -f 해주는 python(>=2.4) 스크립트

## 기능

- 폴더 내 최신 텍스트 파일을 자동으로 열어줌
- cilog 포멧에 대한 하이라이트
- eventlog 포멧에 대한 하이라이트
- ncsa combined log 포멧에 대한 하이라이트
- 괄호 내 단어들에 대한 하이라이트
- stdin pipe 지원
- 지정한 파일만 tail하는 옵션 추가
- tail 하고 있던 파일에 대한 retry 기능
- cilog 포맷의 name, id, date, time 필드 표시하지않는 옵션 추가
- cilog 를 simple 하게 볼 수 있는 옵션 추가
- pipe 사용 시에 옵션을 사용할 수 있게 수정
- 바이너리 파일 지원하지 않음

## 설치

```
$ wget -O - https://raw.githubusercontent.com/castisdev/ctail/master/install.sh --no-check-certificate | bash
```

## 사용 예
```
# 폴더의 최신 텍스트 파일을 tail
$ ctail /var/log/castis/vod/2015-03/2015-
...

# 지정한 텍스트 파일을 tail
$ ctail -f /var/log/castis/vod/event.log
...

# pipe
$ cat EventLog.log | ctail
$ cat cilog.log | ctail --simple
...
```

## 데모

![](https://github.com/castisdev/ctail/blob/master/sample.png)


## CPU 사용률

- 11M 크기의 text file 2002 개가 있는 directory 에 대해서 수행할 경우

|   버전          | 수행 대상               | CPU 사용률 |
| --------------- | ------------------------| ---------- |
| 최초 버전       | directory               |  10 ~ 15%  |
| 0.1.8           | directory               |  65 ~ 68%  |
| 0.1.9 ~ 0.1.10  | directory               |  15 ~ 20%  |
| -               | -                       |     -      |
| 0.1.6           | file(-f option 사용시)  |   1 ~ 2%   |
| 0.1.8           | file(-f option 사용시)  |  50 ~ 55%  |
| 0.1.9 ~ 0.1.10  | file(-f option 사용시)  |   0 ~ 1%   |

* binary file인지 검사하는 기능 때문에 CPU 사용률이 최초 버전보다 5 ~ 10% 정도 올라가는 것으로 보임

## Release Notes

### 0.1.10

[버그]
* -f 옵션 사용하고 link 파일을 tail 할 때,  link 파일이 가리키는 파일이 다른 파일로 변할 때, tail 안되는 버그(0.1.9) 수정
  * open, close 반복하지 않게 수정하면서 생긴 문제
  * 파일의 inode 값이 변했는지 검사하는 코드 추가

[변경]
* -f 옵션 사용 시, tail 중인 파일의 이름이 바뀌거나 지워지는 경우, 종료됨(이전 버전에서는 종료 안됨)

### 0.1.9

[버그]
* 파일 크기가 작은 경우, 마지막 line이 출력되지 않는 버그(0.1.8) 수정
* -f option 사용 시 파일에 변화가 없을 때 binary 파일인지 반복해서 검사하는 버그(0.1.7) 수정
* 파일에 변화가 없을 때 close, open 반복해서 수행하던 버그(0.1.2) 수정

[변경]
* 파일에 변화가 없을 때 sleep time을 최초 버전대로 수정(0.01초 -> 0.1초)
  * sleep time이 0.01초이고 binary 파일인지 반복해서 검사하면 CPU 사용률 50% 정도 더 사용하게 됨
* 불필요하게 복잡해진 코드를 최초 버전과 유사하게 되돌림
* 일부 python 2.7 코드를 python 2.4 호환코드로 변경
* 일부 test code(>= python 2.7) 추가

### 0.1.8

* 폴더 내 파일이 많은 경우 최신 파일 찾는 데 오래 걸리는 현상 수정
