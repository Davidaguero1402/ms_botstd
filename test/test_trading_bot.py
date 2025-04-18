import pytest
from unittest.mock import patch, MagicMock
from app.utils.trading_bot import TradingBot
from app.models.bot import Bot
from app.models.exchange import Exchanges
from app.models.estrategias import Estrategias
from app.models.activos import Activos

class MockExchange:
    def __init__(self, config):
        self.config = config
        self.load_markets_called = False

    def load_markets(self):
        self.load_markets_called = True

@pytest.fixture
def db_session():
    """Fixture para simular una sesión de base de datos."""
    return MagicMock()

@pytest.fixture
def bot_config():
    """Configuración de ejemplo para un bot de trading."""
    return {
        'nombre': 'bingx',
        'api_key': 'VD2cVcBHYOZ0ReSmygjYooHKXtcpM3OSuyRvhL0oYffzDFrooxGl5yLPf5r8nzLqzP5F9ZgctijQcnhA',
        'secret_key': '3qEgUonDspiScaBxnaAFfEEJG1UE6vk1AJ0sGCzvCVA3DntOZt9Ft4j6NLFmRpUs9C9EDEm3YMP4FZNfzCw'
    }

@pytest.fixture
def trading_bot(db_session, bot_config):
    """Fixture para crear un TradingBot con mocks configurados."""
    # Mock para Bot
    mock_bot = MagicMock()
    mock_bot.exchange_id = 1
    mock_bot.activo_id = 1
    mock_bot.estrategia_id = 1
    mock_bot.intervalo = 60  # Añade un intervalo por defecto

    # Mock para Exchange
    mock_exchange = MagicMock()
    mock_exchange.nombre = bot_config['nombre']
    mock_exchange.api_key = bot_config['api_key']
    mock_exchange.secret_key = bot_config['secret_key']

    # Mock para Estrategia con parámetros JSON válidos
    mock_estrategia = MagicMock()
    mock_estrategia.parametros = '{"param1": "value1", "param2": "value2"}'

    # Mock para Activo
    mock_activo = MagicMock()

    # Configurar los métodos get del mock de sesión
    db_session.get.side_effect = lambda model, id: {
        Bot: mock_bot,
        Exchanges: mock_exchange,
        Estrategias: mock_estrategia,
        Activos: mock_activo
    }.get(model, None)

    # Crear el TradingBot con la sesión mockeada
    bot = TradingBot(bot_id=1, db_session=db_session)
    return bot

@patch('app.utils.exchange_factory.ExchangeFactory.create_exchange', autospec=True)
def test_init_bot_config(mock_create_exchange, trading_bot, bot_config):
    """
    Test para verificar la inicialización correcta del bot:
    - Configuración cargada correctamente
    - Exchange creado con los parámetros correctos
    """
    # Configurar el mock del exchange
    mock_exchange = MockExchange({
        'apiKey': bot_config['api_key'],
        'secret': bot_config['secret_key'],
        'enableRateLimit': True,
        'options': {'adjustForTimeDifference': True}
    })
    mock_create_exchange.return_value = mock_exchange

    # DEBUG: Imprimir los detalles de la configuración del exchange
    print("Exchange Config:", 
        getattr(trading_bot.exchange_config, 'nombre', None),
        getattr(trading_bot.exchange_config, 'api_key', None),
        getattr(trading_bot.exchange_config, 'secret_key', None)
    )

    # Verificaciones
    assert trading_bot.bot is not None
    assert trading_bot.exchange_config is not None
    assert trading_bot.activo is not None
    assert trading_bot.strategy_params == {"param1": "value1", "param2": "value2"}

    # DEBUG: Imprimir las llamadas al mock
    print("Mock Calls:", mock_create_exchange.call_args_list)

    # Verificar que el exchange se inicializó correctamente
    mock_create_exchange.assert_called_once_with(
        bot_config['nombre'],
        bot_config['api_key'],
        bot_config['secret_key']
    )

def test_load_bot_config_error(db_session):
    """
    Test para verificar manejo de errores en carga de configuración
    """
    # Configurar sesión para que no encuentre el bot
    db_session.get.return_value = None

    with pytest.raises(ValueError, match="Bot 1 no encontrado"):
        TradingBot(bot_id=1, db_session=db_session)

def test_load_bot_config_incomplete(db_session):
    """
    Test para verificar manejo de configuración incompleta
    """
    # Mock para Bot
    mock_bot = MagicMock()
    mock_bot.exchange_id = 1
    mock_bot.activo_id = 1
    mock_bot.estrategia_id = 1

    # Configurar get para devolver None en algún recurso
    def side_effect(model, id):
        if model == Bot:
            return mock_bot
        return None

    db_session.get.side_effect = side_effect

    with pytest.raises(ValueError, match="Configuración incompleta"):
        TradingBot(bot_id=1, db_session=db_session)