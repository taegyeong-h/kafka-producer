

## 카프카 3대 서버의 클러스터 매핑 정보 설정

#### etc/hosts
```bash
127.0.0.1       localhost
127.0.1.1       kafka-broker0x       # <-- 자기 자신 이름

# 카프카 클러스터 (3대 모두 동일하게 복사)
192.168.56.100  kafka-broker01
192.168.56.101  kafka-broker02
192.168.56.102  kafka-broker03


[ipv6]
::1
fe
```

**주소확인**
```bash
ubuntu@kafka-broker03:~$ ping -c 3 kafka-broker01 ~ 3

64 bytes from kafka-broker0x (192.168.56.10x): icmp_seq=1 ttl=64 time=2.00 ms
64 bytes from kafka-broker0x (192.168.56.10x): icmp_seq=2 ttl=64 time=0.908 ms
64 bytes from kafka-broker0x (192.168.56.10x): icmp_seq=3 ttl=64 time=1.94 ms

```

#### kafka 1번 서버
``` bash
1. 처음에 토픽 목록 확인 (아무것도 없어서 빈 줄만 출력됨)
kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --list

# 2. 'test.hello'라는 이름의 토픽 생성
kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --create --topic test.hello

# 3. 다시 토픽 목록 확인 ('test.hello'가 출력됨)
kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --list
```

#### kafka 2,3 번 서버
``` bash
# 1번에서 만든 토픽이 여기서도 똑같이 보이는지 확인!
kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --list
```
