USE agricultura;

CREATE TABLE IF NOT EXISTS precios_crypto (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL,
    criptomoneda VARCHAR(50) NOT NULL,
    precio_usd DOUBLE NOT NULL,
    volumen_24h DOUBLE NOT NULL,
    cambio_24h DOUBLE NOT NULL,
    INDEX idx_fecha (fecha),
    INDEX idx_crypto (criptomoneda)
);

-- Datos iniciales de arranque
INSERT INTO precios_crypto (fecha, criptomoneda, precio_usd, volumen_24h, cambio_24h) VALUES
(NOW() - INTERVAL 10 MINUTE, 'bitcoin', 65000.00, 25000000.0, 1.2),
(NOW() - INTERVAL 10 MINUTE, 'ethereum', 3400.00, 12000000.0, -0.5),
(NOW() - INTERVAL 10 MINUTE, 'solana', 150.00, 5000000.0, 2.8);