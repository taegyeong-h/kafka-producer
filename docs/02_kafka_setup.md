

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

### 3대 서버 파일 설정 수정
```bash
**vim ~/confluent-8.3.0/etc/kafka/server.properties**
**kafka-broker01**

process.roles=broker,controller
node.id=1
#controller.quorum.bootstrap.servers=localhost:9093
controller.quorum.voters=1@kafka-broker01:9093,2@kafka-broker02:9093,3@kafka-broker03:9093

#advertised.listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
advertised.listeners=PLAINTEXT://kafka-broker01:9092,CONTROLLER://kafka-broker01:9093

# [수정] 2번 서버니까 ID를 2로 바꿉니다.
**kafka-broker02**
node.id=2
process.roles=broker,controller

# [수정] bootstrap은 주석처리!
#controller.quorum.bootstrap.servers=localhost:9093
controller.quorum.voters=1@kafka-broker01:9093,2@kafka-broker02:9093,3@kafka-broker03:9093

# [수정] 다른 컴퓨터가 나(2번)를 찾아올 수 있게 주소를 kafka-broker02로 바꿉니다.
#advertised.listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
advertised.listeners=PLAINTEXT://kafka-broker02:9092,CONTROLLER://kafka-broker02:9093


# [수정] 3번 서버니까 ID를 3로 바꿉니다.
**kafka-broker03**
node.id=3
process.roles=broker,controller

# [수정] bootstrap은 주석처리!
#controller.quorum.bootstrap.servers=localhost:9093
controller.quorum.voters=1@kafka-broker01:9093,2@kafka-broker02:9093,3@kafka-broker03:9093

# [수정] 다른 컴퓨터가 나(2번)를 찾아올 수 있게 주소를 kafka-broker02로 바꿉니다.
#advertised.listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
advertised.listeners=PLAINTEXT://kafka-broker03:9092,CONTROLLER://kafka-broker03:9093

kafka-server 1,2,3 공통
~/confluent-8.3.0/bin/kafka-server-start ~/confluent-8.3.0/etc/kafka/server.properties
```

#### kafka 
``` bash

1단계: 클러스터 비밀번호(UUID) 발급받기 (1번 서버에서만 딱 1번 실행)
- 3대의 카프카 서버를 하나의 팀으로 묶어줄 고유한 ID 카드를 발급받는 과정입니다. 1번 서버 터미널에 아래 명령어를 입력하세요.
~/confluent-8.3.0/bin/kafka-storage random-uuid
Oe6T-YusRpO6D0OIAD08gw

2단계: 3대 서버 각각 포맷하기 (1, 2, 3번 서버 모두 각각 실행)
아까 발급받으신 진짜 UUID인 Oe6T-YusRpO6D0OIAD08gw를 사용해 3대의 서버 저장 공간을 각각 포맷합니다. 3대 서버 터미널에 각각 붙여넣으세요.
~/confluent-8.3.0/bin/kafka-storage format -t Oe6T-YusRpO6D0OIAD08gw -c ~/confluent-8.3.0/etc/kafka/server.properties

```bash
 ~/confluent-8.3.0/bin/kafka-storage format -t Oe6T-YusRpO6D0OIAD08gw -c ~/confluent-8.3.0/etc/kafka/server.properties
Bootstrap metadata: BootstrapMetadata(records=[ApiMessageAndVersion(FeatureLevelRecord(name='metadata.version', featureLevel=30) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='eligible.leader.replicas.version', featureLevel=1) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='group.version', featureLevel=1) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='share.version', featureLevel=1) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='streams.version', featureLevel=1) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='transaction.version', featureLevel=2) at version 0)], metadataVersionLevel=30, source=format command)
Formatting metadata directory /tmp/kraft-combined-logs with metadata.version 4.3-IV0.

```

첫번째 kafka-broker01 세션을 복사하여 아래와 같이 입력 

-- create --topic 이름은 test.hello 
~/confluent-8.3.0/bin/kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --create --topic test.hello

WARNING: Due to limitations in metric names, topics with a period ('.') or underscore ('_') could collide. To avoid issues it is best to use either, but not both.
**Created topic test.hello.**

-- list (토픽 현황들을 보겠다)
(.venv) ubuntu@kafka-broker01:~$ ~/confluent-8.3.0/bin/kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --list
test.hello

-- list (토픽 현황들을 보겠다)
(.venv) ubuntu@kafka-broker01:~$ ~/confluent-8.3.0/bin/kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --describe

Topic: test.hello       TopicId: V5ovxmhjTuK6kIqJIyAQww PartitionCount: 1       ReplicationFactor: 1    Configs: min.insync.replicas=1,segment.bytes=1073741824
        Topic: test.hello       Partition: 0    Leader: 2       Replicas: 2     Isr: 2  Elr:    LastKnownElr:



1단계: 3대 서버 각각 카프카 전원 켜기 (1, 2, 3번 모두 실행)
매번 창을 3개씩이나 '잠긴 상태'로 놔두면 모니터 화면이 부족하겠죠? 그래서 앞으로는 뒤에 -daemon을 붙여서 무대 뒤(백그라운드)로 깔끔하게 켜줍니다.

3대의 서버 터미널에 각각 아래 명령어를 한 줄씩 던져주세요.

```Bash
~/confluent-8.3.0/bin/kafka-server-start -daemon ~/confluent-8.3.0/etc/kafka/server.properties
# 확인
~/confluent-8.3.0/bin$ ps -ef | grep server.properties
kafka ~ 하는 자바 프로세스가 상단에 나오면 성공이다 

```

2단계: 1번 서버에서 파이썬 가상환경 켜기
이제 내 작업실인 1번 서버(kafka-broker01) 창으로 와서 폴더로 이동하고 가상환경을 쏩니다.

```Bash
cd ~/kafka-project
source .venv/bin/activate
```

3단계: 내 파이썬 코드 실행하기
가상환경 앞에 (.venv)가 붙은 것을 확인했다면, 이따가 작성할 파이썬 프로듀서/컨슈머 코드를 실행하시면 됩니다!

```Bash
python 내_카프카_코드.py
```

🛑 퇴근 루틴 (서버 안전하게 끄는 법)
실습을 마치고 가상머신을 끄거나 잠시 쉬고 싶을 때는, 카프카가 하드디스크에 데이터를 안전하게 저장하고 잠들 수 있도록 전원을 꺼주는 것이 좋습니다. 3대 서버 각각 아래 명령어를 치면 백그라운드에서 돌던 카프카가 얌전하게 종료됩니다.

```Bash
~/confluent-8.3.0/bin$ ./kafka-server-stop
```


## producer와 consumer test 
기존 3개의 서버를 아무거나 2개 복사 해서 하나는 producer, 다른 하나는 consumer 로 만든다
첫번쨰 세션 복사: ~/confluent-8.3.0/bin/kafka-console-producer --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --topic test.hello
첫번째 세션 복사: ~/confluent-8.3.0/bin/kafka-console-consumer --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --topic test.hello --from-beginning    # 




## 보통은 producer 에서 바꾼다 topic 을 test.hello -> new로 수정 + 파티션 추가 
**각 파티션끼리 데이터가 공유되지 않고 브로커(리더)가 존재한다**
**파티션은 브로커수와 상관없이 늘리거나 줄일 수 있다**

~/confluent-8.3.0/bin/kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --create --topic new --partitions 3

## producer와 consumer new 
기존 3개의 서버를 아무거나 2개 복사 해서 하나는 producer, 다른 하나는 consumer 로 만든다
첫번쨰 세션 복사: ~/confluent-8.3.0/bin/kafka-console-producer --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --topic new
첫번째 세션 복사: ~/confluent-8.3.0/bin/kafka-console-consumer --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --topic new --from-beginning    # 





파티션 + 복제본 
**브로커 3대, 파티션3개, 복제본 3개 예시 : 파티션 3**
**PRODUCER와 CONSUMER는 각 파티션 리더로부터 메시지를 받아와 동기화만 수행**
**F는 (L)READER 와 동기화되어 데이터를 복제 하는데만 노력한다**

**복제본 개수는 이란적으로 3개를 설정한다 가용성이 매우 중요하면 5개를 설정하는 경우도 존재하나, 브로커 개수를 초과하여 설정할 수 없다**
**반드시 브로커와 파티션 갯수를 맞추는건 아니다 Producer, Consumer 성능에 따라 성능이 변화할 수있고 (특히 Consumer가 일을 더 많이 한다) 그래서 파티션 수는 정답이 없다 **
~/confluent-8.3.0/bin/kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --create --topic new --partitions 3 --replication-factor 3




토픽 homework.ch4-5.ptt5-3으로 하되, 파티션 갯수를 5개, 복제본 갯수를 3개로 생성
잘 만들었는지 확인 후, 리더가 어떤 노드에 있는지 어떻게 알 수있을까?

~/confluent-8.3.0/bin/kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --create --topic homework.ch4-5.ptt5-3 --partitions 5 --replication-factor 3
Created topic homework.ch4-5.ptt5-3.



~/confluent-8.3.0/bin/kafka-topics --bootstrap-server kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092 --topic homework.ch4-5.ptt5-3 --describe
Topic: homework.ch4-5.ptt5-3    TopicId: Y4s2NpipTBmC3yMONb9f3A PartitionCount: 5       ReplicationFactor: 3    Configs: min.insync.replicas=1,segment.bytes=1073741824
        Topic: homework.ch4-5.ptt5-3    Partition: 0    Leader: 1       Replicas: 1,2,3 Isr: 1,2,3      Elr:    LastKnownElr:
        Topic: homework.ch4-5.ptt5-3    Partition: 1    Leader: 2       Replicas: 2,3,1 Isr: 2,3,1      Elr:    LastKnownElr:
        Topic: homework.ch4-5.ptt5-3    Partition: 2    Leader: 3       Replicas: 3,1,2 Isr: 3,1,2      Elr:    LastKnownElr:
        Topic: homework.ch4-5.ptt5-3    Partition: 3    Leader: 1       Replicas: 1,3,2 Isr: 1,3,2      Elr:    LastKnownElr:
        Topic: homework.ch4-5.ptt5-3    Partition: 4    Leader: 3       Replicas: 3,2,1 Isr: 3,2,1      Elr:    LastKnownElr:


        




