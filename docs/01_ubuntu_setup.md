# Kafka Cluster Instance Setup Guide (Ubuntu 26.04 Server)

### 이 문서는 VirtualBox 가상 가상머신 환경에서 Confluent Kafka 커뮤니티 에디션 클러스터(3 Node)를 구축하기 위한 초기 인프라 설정 가이드입니다.


## kafka 개별 환경 설정   

**인스턴스 공통 리소스**   
- CPU: 2
- Memory: 4GB
- SSD: 50GB

**인스턴스 개별 IP**   
- kafka-broker01= enp8: 192.168.56.100/24
- kafka-broker02= enp8: 192.168.56.101/24
- kafka-broker03= enp8: 192.168.56.102/24

## 인스턴스 개별 설정

### 인스턴스 개별 고정 IP
```bash
etc/netplan
# addresses 항목을 고유 IP인 192.168.56.10x/24 고정 IP로 수정 후 저장
sudo netplan apply
```


### 호스트네임(컴퓨터 이름) 수정
``` Bash
# (※ -s 뒤에 f를 붙이면 기존에 파일이 있든 없든 무시하고 강제로 새로 연결합니다.)
sudo hostnamectl set-hostname kafka-broker01 ~ 3

```

### 고유 머신 ID 새로 발급
```Bash
sudo ln -sf /etc/machine-id /var/lib/dbus/machine-id
```

### 원본 이름으로 적힌 부분을 kafka-broker0x 로 수정
```Bash
sudo nano /etc/hosts
127.0.1.1 kafka-broker0x 
```

## 패키지 리스트 업데이트
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip python3-venv software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# 2. 내 프로젝트 폴더로 이동한 뒤 가상환경을 생성합니다. (폴더명은 .venv를 추천합니다)
mkdir kafka-project && cd kafka-project
python3 -m venv .venv

# 3. 생성한 가상환경 방으로 입장(활성화)합니다.
source .venv/bin/activate

(.venv) ubuntu@kafka-broker03:~/kafka-project$
```

## 공통 유틸리티 및 SSH 서버 설치
``` bash
  sudo apt install vim curl wget net-tools, openssh-server -y
```

## 공통 Kafka 설치
``` bash
curl -O https://packages.confluent.io/archive/8.3/confluent-community-8.3 
```
