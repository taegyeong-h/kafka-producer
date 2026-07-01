

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



## timedatectl 설정
**카프카는 시간(Timestamp)에 엄청나게 집착하는 프로그램이기에 시간을 맞춰줘야 한다**
```bash
sudo timedatectl set-timezone Asia/Seoul
timedatectl
               Local time: Wed 2026-07-01 15:01:28 KST
           Universal time: Wed 2026-07-01 06:01:28 UTC
                 RTC time: Wed 2026-07-01 06:01:28
                **Time zone: Asia/Seoul (KST, +0900)**
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

## setting_python_env

sudo apt install software-properties-common
