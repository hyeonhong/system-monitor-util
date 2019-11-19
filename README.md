## System Monitor Util

### 구동시 유의사항

#### 1. ssh 용 key 파일의 경로를 지정하기

```
vi monitor_usage/key_path.conf
```

key 파일(\*.pem)이 있는 경로를 본인의 주소에 맞게 수정

#### 2. shell script 실행하기

```
cd bin
./ monitor_usage.sh   # 혹시 안될경우, chmod u+x monitor_usage.sh 입력한 후 실행
```
