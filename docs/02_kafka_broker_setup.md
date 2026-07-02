
# 🚊 서울 지하철 파이프라인: 3대 카프카 브로커 클러스터 (KRaft 모드) 구축 가이드

> [!IMPORTANT]
> 본 가이드는 주키퍼(Zookeeper) 없이 자체 합의 알고리즘으로 구동되는 최신 **KRaft(Kafka Raft) 모드** 기준 분산 인프라 설정 명세서입니다.

### 01_etc/hosts
```bash
127.0.0.1       localhost

# 카프카 분산 클러스터 진짜 고속도로 개통 (3대 모두 동일하게 복사)
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

### 3대 브로커 서버 환경 설정


#### 💾 1. 리눅스 `/tmp` 저장소 해제 및 영구 경로 변경

> [!NOTE]
> **왜 경로를 변경해야 하나요?**
> 리눅스(Ubuntu) 시스템은 컴퓨터가 재부팅될 때 `/tmp` 폴더 내부를 자동으로 싹 청소(Format)해 버리는 고약한 버릇이 있습니다. 
> 여기에 카프카 장부를 그대로 두면 **재부팅 시 카프카가 마스터 도장(UUID)을 잃어버리고 즉사**하게 되므로, 반드시 영구 보존이 가능한 사용자의 홈 디렉토리(`~/data/...`) 하위로 격리해야 합니다.

각 가상머신 서버의 `~/confluent-8.3.0/etc/kafka/server.properties` 파일을 열고 아래와 같이 저장소 경로를 영구 경로로 수정합니다.

```diff
# server.properties 수정 항목
- log.dirs=/tmp/kraft-combined-logs
+ log.dirs=/home/ubuntu/data/kafka-logs
```

> [!NOTE]
> **💡 각 서버별 필수 치환 항목 (1~3번 서버 각각 다르게 설정)**
> * **`node.id`:** 각 서버 번호에 맞게 수정 각 서버별로 중복되지 않는 고유 정수 숫자를 지정 (예: `1`, `2`, `3`,`100`, `101`, `102`)
> * **`advertised.listeners`:** 주소 중간의 이름표를 자기 호스트네임에 맞게 치환 
>   * *(예: 2번 서버는 `kafka-broker02`, 3번 서버는 `kafka-broker03`)*

```diff
# [필수 수정] IP 뒷자리 매핑 정석 적용 (1번 서버: 100, 2번 서버: 101, 3번 서버: 102)
node.id=100
process.roles=broker,controller

# 쿼럼(합의체) 투표권자 명부 등록 (3대 삼형제 주소록 바인딩)
- controller.quorum.bootstrap.servers=localhost:9093
+ controller.quorum.voters=100@kafka-broker01:9093,101@kafka-broker02:9093,102@kafka-broker03:9093

# 외부(윈도우 호스트/옆방 가상머신) 통신용 외부 노출 주소 선언
- advertised.listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
+ advertised.listeners=PLAINTEXT://kafka-broker01:9092,CONTROLLER://kafka-broker01:9093
```
#### 🔑 3. KRaft 마스터 클러스터 ID(UUID) 생성 및 포맷팅

> [!WARNING]
> **🚨 반드시 1번 서버(`kafka-broker01`) 터미널에서만 '딱 1번' 실행하세요!**
> 3대의 카프카 서버를 하나의 팀(클러스터)으로 묶어줄 고유한 주민등록번호를 발급받는 과정입니다. 2, 3번 서버에서 이 명령어를 중복 실행하면 클러스터가 쪼개져 통곡의 벽에 갇히게 됩니다.

1번 서버 터미널에 아래 명령어를 입력하여 무작위 UUID 도장을 발행합니다.

```bash
# Confluent 8.3.0+ 최신 버전 규격 명령어
~/confluent-8.3.0/bin/kafka-storage random-uuid
```

* **출력 예시:** `rgEz4HuGQnGnNk5y9onTzQ` (위 명령어로 출력된 긴 문자열을 복사하여 다음 단계에 사용합니다.)


### ② 발행된 UUID로 3대 서버 장부 포맷팅 (3대 서버 각각 모두 실행)

> [!NOTE]
> **💡 왜 3대 서버를 모두 포맷(`format`)해야 하나요?**
> 1단계에서 발급받은 UUID 도장은 우리 삼형제를 하나의 클러스터 팀으로 묶어주는 **'가족 결합 도장'**입니다. 
> 3대의 가상머신 서버 각각에 이 도장을 들고 들어가 포맷팅을 처리해 주어야, 카프카 엔진이 **자네가 지정한 안전한 영구 경로(`~/data/kraft-combined-logs`)에 장부 폴더를 하위까지 100% 자동으로 생성**하고, 그 안에 "우리는 한 팀이다!"라는 메타데이터 서류를 안전하게 박제하게 됩니다.

1, 2, 3번 가상머신 터미널 각각에 접속하여, 위에서 복사한 진짜 UUID 값을 `-t` 뒤에 넣고 아래 포맷 명령어를 각각 실행합니다.

```bash
# <주의> 발급받은 진짜 UUID 주소(rgEz4...)를 넣고 실행하세요!
~/confluent-8.3.0/bin/kafka-storage format -t rgEz4HuGQnGnNk5y9onTzQ -c ~/confluent-8.3.0/etc/kafka/server.properties

* **출력 예시:**
Bootstrap metadata: BootstrapMetadata(records=[ApiMessageAndVersion(FeatureLevelRecord(name='metadata.version', featureLevel=30) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='eligible.leader.replicas.version', featureLevel=1) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='group.version', featureLevel=1) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='share.version', featureLevel=1) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='streams.version', featureLevel=1) at version 0), ApiMessageAndVersion(FeatureLevelRecord(name='transaction.version', featureLevel=2) at version 0)], metadataVersionLevel=30, source=format command)
Formatting metadata directory **/home/ubuntu/data/kafka-logs** with metadata.version 4.3-IV0.
```


#### 🔍 5단계: 생성된 메타데이터 장부 파일 검증

포맷팅이 정상 완료되면 `~/data/kafka-logs/` 경로에 아래 두 파일이 자동 생성됩니다.

1. **`meta.properties`:** 클러스터 고유 ID와 브로커 고유 번호(`node.id`)가 박제되는 영구 신분증 파일입니다. 3대 서버의 `cluster.id`가 일치해야 한 팀으로 묶입니다.
   # 카프카 스토리지 메타데이터 서류
   version=1
   cluster.id=rgEz4HuGQnGnNk5y9onTzQ
   node.id=102
3. **`bootstrap.checkpoint`:** KRaft 메타데이터 장부의 최초 동기화 시작 지점(Offset 0)을 기록해 두는 이정표 파일입니다.
   0
   1
**명령어 실행 후 내부 확인:**
```bash
cat ~/data/kafka-logs/meta.properties



## 🚀 4. 카프카 브로커 클러스터 최종 기동 및 생사 확인

> [!TIP]
> 3대 서버의 장부 파일(`meta.properties`) 검증이 완료되었다면, 아래 명령어를 통해 백그라운드 모드(`-daemon`)로 카프카 엔진의 첫 숨을 불어넣습니다.

1, 2, 3번 가상머신 터미널 각각에 접속하여 아래 기동 명령어를 실행합니다.

```diff
# 3대 서버 공통 카프카 엔진 백그라운드 가동
+ ~/confluent-8.3.0/bin/kafka-server-start -daemon ~/confluent-8.3.0/etc/kafka/server.properties
# 프로세스 팩트 체크 명령어 실행
+ ps -ef | grep kafka
```

> [!TIP]
> 로컬 ubu
> 9092 포트 (PLAINTEXT) : "손님용 정문"
> 역할: 파이참에서 짠 파이썬 코드(Producer)나 컨슈머 같은 외부 클라이언트(손님)들이 데이터를 집어넣고 빼가기 위해 노크하는 카프카 브로커의 정문

방화벽 개방 필수 이유: 이 문이 닫혀있으면 외부의 파이참 클라이언트가 아예 서버 안으로 들어오질 못하네.
> 9093 포트 (CONTROLLER) : " 뒷문 (합의체 통로)"
> 손님들은 절대 못 들어오는, 오직 가상머신 삼형제(broker01, 02, 03)들끼리만 서로 밀담을 나누는 사내 비밀 통로
> 3대 브로커 서버 모두 9092 ~ 9093 방화벽 해제 후 적용을 시켜줘야 한다
sudo ufw allow 9092/tcp
sudo ufw allow 9093/tcp
sudo ufw reload

