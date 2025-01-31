# bot_manager.py
import threading
from typing import Dict
from app.utils.trading_bot import TradingBot

class BotManager:
    def __init__(self):
        self.active_bots: Dict[int, threading.Thread] = {}
        self.bot_instances: Dict[int, 'TradingBot'] = {}  # Almacena instancias de TradingBot

    def start_bot(self, bot_id: int):
        from .trading_bot import TradingBot  # Asegúrate de importar correctamente
    
        if bot_id in self.active_bots:
            return
    
        trading_bot = TradingBot(bot_id)  # Pasa la sesión de DB si es necesario
        bot_thread = threading.Thread(target=trading_bot.run)
        bot_thread.daemon = True
    
        self.active_bots[bot_id] = {
            'thread': bot_thread,
            'instance': trading_bot
        }
        bot_thread.start()

    def stop_bot(self, bot_id: int):
        if bot_id in self.active_bots:
            # Detén el bot de manera segura
            trading_bot = self.bot_instances.get(bot_id)
            if trading_bot:
                trading_bot.stop()  # Asegúrate de que TradingBot tenga un método stop()
            
            # Elimina referencias
            del self.active_bots[bot_id]
            del self.bot_instances[bot_id]

    def _run_bot(self, trading_bot: 'TradingBot'):
        trading_bot.run()  # Ejecuta la lógica del TradingBot

bot_manager = BotManager()