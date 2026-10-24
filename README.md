```mermaid
flowchart TD
    %% Estilos globales
    classDef external fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b;
    classDef container fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c;
    classDef storage fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20;
    classDef client fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100;

    %% Nodos externos
    API["🌐 API Pública CoinGecko<br/><code>/simple/price</code>"]:::external
    USER["💻 Navegador Web / Cliente<br/><code>http://localhost:8050</code>"]:::client

    %% Red Docker
    subgraph DOCKER_NET [" 🐳 Red Privada Docker (proyecto-crypto_default) "]
        
        subgraph S_INGESTA [" Contenedor Ingesta (Worker Daemon) "]
            I_WORKER["🐍 ingesta.py<br/><i>Polling cada 30s</i>"]:::container
            I_RETRY{"¿Respuesta HTTP 200?"}:::container
            I_ERR["⚠️ Captura de excepción<br/><i>(Tolerancia a fallos)</i>"]:::container
        end

        subgraph S_MYSQL [" Contenedor MySQL 8.4 (DBMS) "]
            DB_HEALTH["🩺 Healthcheck activo<br/><code>SELECT 1 FROM precios_crypto</code>"]:::storage
            DB_ENGINE[("🗄️ Base de Datos: agricultura<br/>Tabla: precios_crypto")]:::storage
        end

        subgraph S_DASH [" Contenedor Dash (Web Server) "]
            D_GUNICORN["🚀 Servidor Gunicorn<br/><code>2 Workers | WSGI</code>"]:::container
            D_APP["📊 app.py (Dash + Plotly)<br/><i>Callback reactivo (10s)</i>"]:::container
        end

    end

    %% Persistencia
    VOLUME[("💾 Volumen Persistente<br/><code>mysql_data:/var/lib/mysql</code>")]:::storage

    %% Flujos de Ingesta
    API -->|"GET (BTC, ETH, SOL)<br/>JSON"| I_WORKER
    I_WORKER --> I_RETRY
    I_RETRY -- "No (Error/Timeout)" --> I_ERR
    I_ERR -.->|"Espera siguiente ciclo"| I_WORKER
    I_RETRY -- "Sí (Status 200)" -->|"INSERT parametrizado<br/>+ commit()"| DB_ENGINE

    %% Orquestación y Dependencias
    DB_HEALTH -->|"service_healthy"| I_WORKER
    DB_HEALTH -->|"service_healthy"| D_GUNICORN

    %% Flujos de Base de Datos y Persistencia
    DB_ENGINE <-->|"Escribe / Lee datos físicos"| VOLUME

    %% Flujos de Visualización
    D_GUNICORN --> D_APP
    DB_ENGINE -->|"SELECT últimas 500 filas<br/>(Filtro dropdown)"| D_APP
    D_APP -->|"Renderiza gráfica interactiva"| USER