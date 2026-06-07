 # Browser Configuration Guide

## Setup de Resolution/Viewport para Testes Behave

Este projeto agora suporta múltiplas resoluções e tipos de dispositivos (Desktop, Mobile, Tablet) via arquivo de configuração e variáveis de ambiente.

## Arquivos Criados

- `browser_config.json` - Arquivo de configuração com definições de devices
- `python/config/browser_config.py` - Loader de configuração
- `python/config/__init__.py` - Package init

## Configurações Disponíveis

### Desktop (Full HD 1920x1080)
```json
{
  "desktop": {
    "name": "Desktop Full HD",
    "viewport": {"width": 1920, "height": 1080},
    "device_scale_factor": 1,
    "is_mobile": false,
    "has_touch": false
  }
}
```

### Mobile (iPhone 12 - 390x844)
```json
{
  "mobile": {
    "name": "Mobile iPhone 12",
    "viewport": {"width": 390, "height": 844},
    "device_scale_factor": 3,
    "is_mobile": true,
    "has_touch": true,
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0..."
  }
}
```

### Tablet (iPad - 768x1024)
```json
{
  "tablet": {
    "name": "Tablet iPad",
    "viewport": {"width": 768, "height": 1024},
    "device_scale_factor": 2,
    "is_mobile": false,
    "has_touch": true
  }
}
```

## Como Usar

### 1. Executar com Desktop (padrão)
```bash
behave
```

### 2. Executar com Mobile
```bash
BROWSER_DEVICE=mobile behave
```

### 3. Executar com Tablet
```bash
BROWSER_DEVICE=tablet behave
```

### 4. Em PyCharm
- Vá em **Run > Edit Configurations**
- Na seção "Behave", adicione uma variável de ambiente:
  - **Name:** `BROWSER_DEVICE`
  - **Value:** `mobile` (ou `tablet`, `desktop`)

### 5. Personalizar Configurações

Edite `browser_config.json` para:
- Mudar viewports/resoluções
- Adicionar novos devices
- Modificar user agents
- Ajustar device_scale_factor

Exemplo de novo device (Galaxy S21):
```json
{
  "galaxy_s21": {
    "name": "Samsung Galaxy S21",
    "viewport": {"width": 360, "height": 800},
    "device_scale_factor": 2,
    "is_mobile": true,
    "has_touch": true,
    "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36..."
  }
}
```

## API Python

```python
from python.config.browser_config import BrowserConfig

# Obter tipo de device atual
device = BrowserConfig.get_device_type()  # "desktop", "mobile", etc.

# Obter configuração completa
config = BrowserConfig.get_config()
# {
#   "name": "Desktop Full HD",
#   "viewport": {"width": 1920, "height": 1080},
#   "is_mobile": false,
#   ...
# }

# Obter apenas viewport
viewport = BrowserConfig.get_viewport()  # {"width": 1920, "height": 1080}

# Obter nome do device
name = BrowserConfig.get_device_name()  # "Desktop Full HD"

# Listar devices disponíveis
devices = BrowserConfig.get_all_devices()  # ["desktop", "mobile", "tablet"]

# Imprimir info de configuração (debug)
BrowserConfig.print_config_info()
```

## Uso em Steps

Você pode acessar o device type do cenário via `context.device_type`:

```python
@when('o usuário abre o navegador')
def step_open_browser(context):
    device = context.device_type  # "desktop", "mobile", ou "tablet"
    print(f"Rodando teste em: {device}")
```

## Exemplo Completo

### Feature
```gherkin
Scenario: Login em Desktop
  When o usuário loga como admin
  Then o usuário estará logado
```

### Execução
```bash
# Desktop (1920x1080)
behave

# Mobile (390x844)
BROWSER_DEVICE=mobile behave

# Tablet (768x1024)
BROWSER_DEVICE=tablet behave
```

## Notas Importantes

1. **Viewport**: Define o tamanho da janela do navegador
2. **device_scale_factor**: Multiplicador de pixel (afeta densidade de exibição)
3. **is_mobile**: Ativa modo mobile no navegador
4. **has_touch**: Ativa suporte a touch events
5. **user_agent**: Identifica o navegador/dispositivo

## Troubleshooting

**Erro: Device não encontrado**
```
[Warning] Device 'xyz' not found. Using 'desktop'.
```
Solução: Verifique se o device está definido em `browser_config.json`

**Config não carrega**
```
[Warning] Config file not found at .../browser_config.json
```
Solução: Certifique-se de que `browser_config.json` está na raiz do projeto

**Output esperado ao executar**
```
============================================================
[Browser Config] Device Type: mobile
[Browser Config] Name: Mobile iPhone 12
[Browser Config] Viewport: {'width': 390, 'height': 844}
[Browser Config] Mobile: True
============================================================
```

