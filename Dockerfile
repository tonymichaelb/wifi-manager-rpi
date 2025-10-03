FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    hostapd \
    dnsmasq \
    iproute2 \
    wireless-tools \
    wpasupplicant \
    iptables \
    procps \
    net-tools \
    iw \
    gcc \
    python3-dev \
    build-essential \
    network-manager \
    dhcpcd5 \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY templates/ ./templates/

# Criar diretórios necessários
RUN mkdir -p /var/lib/dhcp \
    && mkdir -p /var/run/hostapd \
    && mkdir -p /var/log/wifi-manager

# Dar permissões de execução aos scripts
RUN chmod +x scripts/*.sh

# Expor porta para interface web
EXPOSE 8080

# Comando padrão
CMD ["python", "src/main.py"]